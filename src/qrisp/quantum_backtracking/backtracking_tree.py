"""
\********************************************************************************
* Copyright (c) 2023 the Qrisp authors
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* This Source Code may also be made available under the following Secondary
* Licenses when the conditions for such availability set forth in the Eclipse
* Public License, v. 2.0 are satisfied: GNU General Public License, version 2
* with the GNU Classpath Exception which is
* available at https://www.gnu.org/software/classpath/license.html.
*
* SPDX-License-Identifier: EPL-2.0 OR GPL-2.0 WITH Classpath-exception-2.0
********************************************************************************/
"""

from itertools import product

import numpy as np
import networkx as nx
from sympy.physics.quantum import Ket, OrthogonalKet

from qrisp import (QuantumFloat, QuantumBool, QuantumArray, mcz, cx, h, ry, swap, QFT, 
                   auto_uncompute, invert, control, IterationEnvironment, bin_rep, 
                   cyclic_shift, multi_measurement, increment)

"""
As specified in the paper (https://arxiv.org/abs/1509.02374), the key challenge
in implementing the quantum backtracking algorithm is the realization of the operators
R_A and R_B. These operators consists of the direct some of diffuser operators D_x,
where x is an arbitrary node of the backtracking graph.
R_A and R_B are defined as the direct sum of these

R_A = [direct sum] D_x  [summed over all nodes x with even depth]
R_B = |r><r| [direct sum] D_x [summed over all nodes x with even depth]

Or in words: Each node x together with it's children {y : x->y}
defines a subspace H_x = span(|x>, {|y>, x->y}) on which the operator D_x is acting
in-place.

The definition of the D_x operators consists of multiple conditions:
    
    1. If x is an "accept" node, D_x = 1 (ie. the identity)
    2. If x is the root D_x = 1 - 2|psi_r><psi_r|
        Where |psi_r> = (1+d_r*n)**-0.5 * (|r> + n**0.5 * [sum] |y>)
        Where d_r is  the degree of the root, n is the maximum depth of the tree
        and the sum iterates over all children of r
    3. Otherwise: D_x = 1 - 2 |psi_x><psi_x|
        Where |psi_x> = (d_x)**-0.5 (|x> + [sum] |y>)
        Where d_x is the degree of x and the sum iterates over all children of x

To implement this operator, we will rewrite it a bit:
    
D_x = 1 - (1+(-1)**accept(x)) * |psi_r><psi_r|
    
The next step is to assume an operator U_x, which prepares |psi_x> from x

|psi_x> = U_x |x>

We can then write

D_x = D_x = 1 - (1+(-1)**accept(x)) * |psi_r><psi_r|
    = U_x (1 - (1+(-1)**accept(x))*|x><x|) U_x^(-1)

If we pick an encoding, where each node state |x> is a computational basis state,
the center bracket (1 - (1+(-1)**accept(x))*|x><x|) can be realized as a 
multi-controlled Z-gate on the bitstring of |x>, which is also controlled on the 
result of accept(x).

The operator U_x is implemented as the function psi_prep below.

The operator D_x is implemented as the method qstep_diffuser of the
QuantumBacktrackingTree class.

This brings us to another important point in the implementation of the algorithm:
The encoding of the node states.

In principle, the paper makes no statement how such an encoding could be realized.
The approach we took here is the following:
    
A node state |x> is specified by:
    1. A QuantumFloat l, which specifies the distance of x from the root
    2. A QuantumArray branch_qa, which specifies the path to take to reach x.

A few things have to be said about this encoding:
    
The initial state of branch_qa is |0>|0>|0>...

Any state where there is a non-zero state at an index higher than l is considered
"non-algorithmic", ie. the state does not represent a node. An example could be

|0>|0>|1>...|l = 1>

Another important point: As it turns out a much more efficient implementation is 
possible if branch_qa holds the path from the node to the root instead of root-to-node.
For an example of this can be found in the docstring of QuantumBacktrackingTree.

"""



class QuantumBacktrackingTree:
    """
    This class describes the central data structure to run backtracking algorithms in
    a quantum setting. `Backtracking algorithms <https://en.wikipedia.org/wiki/Backtracking>`_ 
    are a very general class of algorithms which cover many problems of combinatorial 
    optimization such as 3-SAT or TSP.
    
    Backtracking algorithms can be put into a very general form. Given is a maximum 
    recursion depth, two functions called ``accept``/``reject`` and the set of 
    possible assignments for an iterable x.
        
    ::
        
        from problem import accept, reject, max_depth, assignments
        
        def backtracking(x):
            
            if accept(x):
                return x
            
            if reject(x) or len(x) == max_depth:
                return None
            
            for j in assigments:
                y = list(x)
                y.append(j)
                res = backtracking(y)
                if res is not None:
                    return res
                
    
    The power of these algorithms lies in the fact that they can quickly discard
    large parts of the potential solution space by using the reject function to
    cancel the recursion. Compared to an unstructured search, where only the 
    accept function is available, this can significantly cut the required resources.
            
    The quantum algorithm for solving these problems has been 
    `proposed by Ashley Montanaro <https://arxiv.org/abs/1509.02374>`_ and yields
    a 1 to 1 correspondence between an arbitrary classical backtracking algorithm
    and it's quantum equivalent. The quantum version achieves a quadratic speed up
    over the classical one.
    
    The algorithm is based on performing quantum phase estimation on a quantum walk
    operator, which traverses the backtracking tree. The core algorithm returns 
    "Node exists" if the 0 component of the quantum phase estimation result 
    has a higher probability then 3/8 = 0.375.
    
    Similar to the classical version, for the Qrisp implementation of this quantum 
    algorithm, a backtracking problem is specified by a maximum recursion depth
    and two functions, each returning a :ref:`QuantumBool` respectively:
    
    **accept**: Is the function that returns True, if called on a node, satisfying the 
    specifications.
    
    **reject**: Is the function that returns True, if called on a node, representing a 
    branch that should no longer be considered.
    
    Furthermore required is a :ref:`QuantumVariable` that specifies the branches
    that can be taken by the algorithm at each node.
    
    .. note::
        
        Many implementations of backtracking also include the possibility for
        deciding which entries of x to assign based on some user provided heuristic.
        The quantum version also supports this feature, however it is not yet
        implemented in Qrisp.

    Parameters
    ----------

    max_depth : integer
        The depth of the backtracking tree.
    branch_qv : QuantumVariable
        A QuantumVariable representing the possible branches of each node.
    accept : function
        A function taking an instance of QuantumBacktrackingTree and returning 
        a QuantumBool, which is True, if called on a satisfying node.
    reject : function
        A function taking an instance of QuantumBacktrackingTree and returning 
        a QuantumBool, which is True, if a called on a node where the corresponding
        branch should no longer be investigated.
        
    
    Attributes
    ----------
    
    h : :ref:`QuantumFloat`
        A QuantumFloat representing the height of the represented node. The root 
        has h = max_depth, it's children have h = max_depth-1 etc.
    branch_qa : :ref:`QuantumArray`
        A QuantumArray representing the path from the root to the current node.
        The qtype of this QuantumArray is what is been provided as branch_qv.
        Note that for implementation efficiency reasons, the path is reversed.
        In a binary tree of depth 4, the node which is reached after taking the
        branches 100 is therefore represented by h = 1, branch_qa = [0,0,1,0].
        States that have a non-zero value at entries indexed bigger than max_depth-h, 
        are considered non-algorithmic and will never be visited 
        (eg. h=3, branch_qa = [1,1,1,1]).
    qs : :ref:`QuantumSession`
        The QuantumSession of the backtracking tree.
    max_depth : int
        An integer specifying the maximum depth of each node.
    
    
    Examples
    --------
    
    We recommend skipping to the "Attributes" section to gain an understanding
    on how the backtracking nodes are encoded into QuantumVariables.
    
    **Checking for the existence of a solution**
    
    Even though the backtracking problems primary purpose is to __find__ a solution,
    at the core, Montanaros algorithm only determines solution existence. This can 
    however still be leveraged into a solution finding algorithm.
    
    To demonstrate the solution existence functionality, we search the binary 
    tree that consists only of nodes with alternating branching.
    We accept if we find the node [1,0,0] (doesn't exist in this tree).
    
    For this we first set up the reject condition. 
    
    ::
        
        from qrisp import *
        
        @auto_uncompute    
        def reject(tree):
            exclude_init = (tree.h < tree.max_depth -1 )
            alternation_condition = (tree.branch_qa[0] == tree.branch_qa[1])
            
            return exclude_init & alternation_condition
        
    Note that the root and it's children are never rejected, or else the algorithm would
    cancel immediately. For the encoding of the nodes please refer to the attributes
    section of this page.
    
    The third condition makes sure that each node where the last branching 
    (tree.branch_qa[0]) is equal to the branching before (tree.branch_qa[1])
    is rejected.
    
    We now implement the accept condition:
    
    ::
        
        @auto_uncompute    
        def accept(tree):
            height_condition = (tree.h == tree.max_depth - 3)
            path_condition = (tree.branch_qa[0] == 0)
            path_condition = path_condition & (tree.branch_qa[1] == 0)
            path_condition = path_condition & (tree.branch_qa[2] == 1)
            
            return height_condition & path_condition
        
    
    Subsequently we set up the class instance:
    
    ::        
        
        from qrisp.quantum_backtracking import QuantumBacktrackingTree
        
        tree = QuantumBacktrackingTree(max_depth = 3,
                                       branch_qv = QuantumFloat(1),
                                       accept = accept,
                                       reject = reject)
        
        tree.init_node([])
        
    We can evaluate the statevector:
        
    >>> tree.statevector()
    1.0*|[]>
    
    The ``[]`` indicates that this is the root state. If the tree was in the state
    of a child of the root (say the one connected to the 1 branch) it would be ``[1]``.
    
    Note that the ``statevector`` method decodes the QuantumVariables holding the
    node state for convenient readibility. If you want to see the encoded variables
    you can take a look at the :ref:`QuantumSession` s :meth:`statevector method<qrisp.QuantumSession.statevector>`:
        
    >>> tree.qs.statevector()
    |0>**4*|3>
    
    We can also visualize the statevector of the tree:
        
    >>> import matplotlib.pyplot as plt
    >>> tree.visualize_statevector()
    >>> plt.show()
    
    .. image:: ./root_state_plot.png
        :width: 200
        :alt: Root statevector plot
        :align: left
    
    |
    |
    |
    |
    |
    
    And finally evaluate the algorithm:
        
    ::
        
        qpe_res = tree.estimate_phase(precision = 4)
    
    Perform a measurement
    
    >>> mes_res = qpe_res.get_measurement()
    >>> mes_res[0]
    0.0253
    
    The 0 component has only 0.0253% probability of appearing, therefore we can conclude,
    that in the specified tree no such node exists.
    
    We now perform the same process but with a trivial reject function:
        
    ::
        
        def reject(tree):
            return QuantumBool()
        
        tree = QuantumBacktrackingTree(max_depth = 3,
                                       branch_qv = QuantumFloat(1),
                                       accept = accept,
                                       reject = reject)
        
        tree.init_node([])
        
        qpe_res = tree.estimate_phase(precision = 4)
        
        
    >>> mes_res = qpe_res.get_measurement()
    >>> mes_res[0]
    0.5027
    
    We see a probability of more than 50%, implying a solution exists in
    this tree.
    
    **Finding a solution**

    Montanaros approach to determine a solution is to classically traverse the tree,     
    by always picking the child node where the quantum algorithm returns "Node exists".
    Finding a solution can therefore be considered a hybrid algorithm.
    
    The Qrisp implementation abuses a little shortcut: After having measured the
    result of the quantum phase estimation, the $\ket{0}$ state is entangled with
    the $\ket{\phi}$ state. This state contains information about the path to
    an accepted node. Therefore by measuring also the tree variables, we
    can make an informed decision which path to take. This implies, that in the 
    limit of infinite shots, only a single query is needed!
    
    To demonstrate, we search for the node [1,1,1] with a trivial reject function.
    
    ::
        
        @auto_uncompute    
        def accept(tree):
            height_condition = (tree.h == tree.max_depth - 3)
            path_condition = QuantumBool()
            mcx(tree.branch_qa[:3], path_condition)
            
            return height_condition & path_condition
        
        def reject(tree):
            return QuantumBool()
        
    
    Set up the QuantumBacktrackingTree instance:
        
        
    >>> max_depth = 4
    >>> tree = QuantumBacktrackingTree(max_depth,
                                       branch_qv = QuantumFloat(1),
                                       accept = accept,
                                       reject = reject)
    
    And call the solution finding algorithm
    
    >>> tree.find_solution(precision = 5)
    [1, 1, 1]
    
        
    """
    
    def __init__(self, max_depth, branch_qv, accept, reject):
        
        self.max_depth = max_depth
        
        self.degree = 2**branch_qv.size
        
        self.branch_qa = QuantumArray(qtype = branch_qv, shape = max_depth)
        
        h_size = int(np.ceil(np.log2(max_depth+2)))

        self.branch_workspace = branch_qv.duplicate(qs = self.branch_qa.qs, name = "branch_workspace*")

        self.h = QuantumFloat(h_size, name = "h*", qs = self.branch_qa.qs)
        
        self.qs = self.h.qs
        
        self.accept_function = accept
        self.reject_function = reject
    
    def accept(self):
        return self.accept_function(self)
    
    def reject(self):
        return self.reject_function(self)

    @auto_uncompute
    def qstep_diffuser(self, even = True, ctrl = []):
        """
        Performs the operators :math:`R_A` or :math:`R_B`. For more information on these operators check `the paper <https://arxiv.org/abs/1509.02374>`_.

        Parameters
        ----------
        even : bool, optional
            If set to ``True`` :math:`R_A` will be performed. Otherwise :math:`R_B` will be performed. The default is True.
        ctrl : List[Qubit], optional
            A list of qubits that allows performant controlling. The default is [].

        Examples
        --------
        
        We set up a QuantumBackTrackingTree and perform the diffuser on a marked node 
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def accept(tree):
                return (tree.h == 1)
            
            
            tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
            
            tree.init_node([1,1]) 
        
        >>> print(tree.qs.statevector())
        |1>**2*|0>*|2>*|0>
        >>> tree.qstep_diffuser()
        >>> print(tree.qs.statevector())
        |1>**2*|0>*|2>*|0>
        
        We see that the node (as expected) is invariant under :math:`R_A`.
        """
        
        
        #This function performs the operation
        # D_x = U_x (1 - (1+(-1)**accept(x))*|x><x|) U_x^(-1)
        #For more information, check the beginning of this file
        
        
        #Perform U_x^(-1)
        with invert():
            psi_prep(self, even = even)

        #We now perform the operation
        # 1 - (1+(-1)**accept(x))*|x><x|
        #by executing an appropriate mcz gate
        
        #Two additional details to consider:
        #   1. We allow for additional control qubits. This is important because 
        #   this operator will undergo phase estimation and we want to prevent 
        #   performing automatic synthesis of the controlled operation, 
        #   as this would imply controlling EVERY gate. Instead we can just
        #   control the mcz gate.
        #   2. If reject(x) = True, this node has no children, implying
        #   D_x = 1 - 2*|x><x|
        #   We realize this behavior by adding an additional control on the value
        #   of the reject function to the mcz gate, such that if reject(x) = True
        #   the operator U_x mcz U_x^(-1) = 1
        #   We then realize D_x = 1 - 2*|x><x| with another mcz gate.
        #   This has the disadvantage, that the reject function needs to be 
        #   evaluated twice. If you find a better solution, that requires only a
        #   single evaluation feel free to message us
        #   raphael.seidel@fokus.fraunhofer.de
        

        #This list will hold the qubit for the first mcz gate.
        mcz_list = []
        
        #D_x operates on the space span(|x>, {|y>, x->y})
        #In order to make sure our mcz gate only marks |x>, we can use the
        #oddity of l, because if l(x) is odd, then l(y) is not.
        oddity_qb = self.h.significant(0)
        mcz_list.append(oddity_qb)
        
        #Prepare control state specificator
        if even:
            #If we are in the even case, we want to tag only the states with
            #even l, so we want oddity_qb to be in state 0
            ctrl_state = "0"
        else:
            ctrl_state = "1"
        
        
        #It turns out U_x^(-1) also produces non-algorithmic states, but we
        #only want to tag |x>. Luckily, the non algorithmic states can be identified
        #by checking wether the branch_workspace QuantumVariable is 0. For more
        #details why this is the case, examine the role of this QuantumVariable
        #in the function psi_prep.
        # is_valid = (self.branch_workspace == 0)
        # mcz_list.append(is_valid)
        mcz_list.append(list(self.branch_workspace))
        ctrl_state += "0"*len(self.branch_workspace)
        
        #Determine accept value
        accept_value = self.accept()
        accept_value.flip()
        mcz_list.append(accept_value)
        ctrl_state += "1"
        
        #Determine reject value
        reject_value = self.reject()
        reject_value.flip()
        mcz_list.append(reject_value)
        ctrl_state += "1"
        
        
    	#Add additional control qubits        
        mcz_list += ctrl
        ctrl_state += "1"*len(ctrl)
        
        #Perform mcz gate
        mcz(mcz_list, ctrl_state = ctrl_state)
        
        #Perform U_x
        psi_prep(self, even = even)
        
        
        #Perpare the qubits for the second mcz gate
        mcz_list = [oddity_qb]
        
        #We need to evaluate reject again, because psi_prep 
        #changed the state of the tree
        reject_value = self.reject()
        mcz_list.append(reject_value)
        
        #Add additional control qubits
        mcz_list += ctrl
        
        #Specify the control state for the second mcz
        if even:
            ctrl_state = "0"
        else:
            ctrl_state = "1"
        
        ctrl_state += (len(mcz_list)-1)*"1"
        
        #Perform the second mcz
        mcz(mcz_list, ctrl_state = ctrl_state)
        
        
        
    def quantum_step(self, ctrl=[]):
        """
        Performs the operator :math:`R_B R_A`. For more information check the :meth:`diffuser methode <qrisp.quantum_backtracking.QuantumBacktrackingTree.qstep_diffuser>`.

        Parameters
        ----------
        ctrl : List[Qubit], optional
            A list of qubits, the step operator should be controlled on. The default is [].
        """
        
        self.qstep_diffuser(even = self.max_depth%2, ctrl=ctrl)
        self.qstep_diffuser(even = not self.max_depth%2, ctrl=ctrl)
        
    def estimate_phase(self, precision):
        r"""
        Performs :meth:`quantum phase estimation <qrisp.QPE>` on the :meth:`quantum step operator <qrisp.quantum_backtracking.QuantumBacktrackingTree.quantum_step>`.
        
        If executed with sufficient precision, the phase estimation will yield a QuantumFloat, where the probability of the 0 component indicates the presence of a node where the ``accept`` function yielded ``True``.
        
        If the probability is higher than 3/8 :math:`\Rightarrow` A solution exists.
        
        If the probability is less than 1/4 :math:`\Rightarrow` No solution exists.
        
        Otherwise :math:`\Rightarrow` Increase precision.
        
        In general, the required precision is proportional to
        
        .. math::
            
            \frac{\text{log}_2(Tn)}{2} + \beta
            
        Where :math:`T` is the amount of nodes, that would be visited by a classical algorithm, :math:`n` is the maximum depth and :math:`\beta` is a universal constant.
        

        Parameters
        ----------
        precision : int
            The precision to perform the quantum phase estimation with.

        Returns
        -------
        qpe_res : :ref:`QuantumFloat`
            The QuantumFloat containing the result of the phase estimation.

        """
        
        qpe_res = QuantumFloat(precision, -precision, qs = self.qs)

        h(qpe_res)

        for i in range(qpe_res.size):
            with IterationEnvironment(self.qs, 2**i, precompile = True):
                self.quantum_step(ctrl = [qpe_res[i]])
                
        QFT(qpe_res, inv=True)
        
        return qpe_res

    
    def init_phi(self, path):
        r"""
        Initializes the normalized version of the state :math:`\ket{\phi}`.
        
        .. math::
            
            \ket{\phi} = \sqrt{n}\ket{r} + \sum_{x \neq r, \\ x \rightsquigarrow x_0} (-1)^{l(x)} \ket{x}

        Where :math:`x \rightsquigarrow x_0` means that :math:`x` is on the path from :math:`r` to :math:`x_0` (including :math:`x_0`).
        
        If :math:`x_0` is a marked node, this state is invariant under the quantum step operator.
        
        Parameters
        ----------
        path : List
            The list of branches specifying the path to :math:`x_0`.

        Examples
        --------
        
        We set up a backtracking tree of depth 3, where the marked element is the 111 node.
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def accept(tree):
                return (tree.branch_qa[0] == 1) & (tree.branch_qa[1] == 1) & (tree.branch_qa[2] == 1)
            
            
            tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        
        Initialize :math:`\ket{\phi}` and evaluate the statevector:
        
        >>> tree.init_phi([1,1,1])
        >>> print(tree.qs.statevector())
        (1.0*sqrt(2)*|0>**5 - 0.816496014595032*|1>*|0>**2*|1>*|0> + 0.816496014595032*|1>**2*|0>*|2>*|0> - 0.816496014595032*|1>**3*|3>*|0>)/2
        
        Perform the quantum step and evaluate the statevector again:
        
        >>> tree.quantum_step()
        >>> print(tree.qs.statevector())
        (1.0*sqrt(2)*|0>**5 - 0.816489994525909*|1>*|0>**2*|1>*|0> + 0.816489994525909*|1>**2*|0>*|2>*|0> - 0.816489994525909*|1>**3*|3>*|0>)/2
        
        We see that the node (as expected) is invariant under the quantum step operator.
        """
        
        h_state = {}
        h_state[self.max_depth] = (self.max_depth)**0.5

        for i in range(1, len(path)+1):
            h_state[self.max_depth - i] = (-1)**(i)

        self.h[:] = h_state

        for i in range(1, len(path)+1):
            with self.h == self.max_depth - i:
                for j in range(i):
                    self.branch_qa[j].encode(path[::-1][j], permit_dirtyness = True)
                    
    def init_node(self, path):
        """
        Initializes the state of a given node.

        Parameters
        ----------
        path : List
            List of the branch labels indicating the path from the root to the node.

        Examples
        --------
        
        We initialize a backtracking tree in the 101 node.
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def accept(tree):
                return QuantumBool()
            
            tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
            
            tree.init_node([1,0,1])

        """
        
        self.h[:] = self.max_depth - len(path)
        if len(path):
            self.branch_qa[:len(path)] = path[::-1]
    
    def subtree(self, new_root):
        """
        Returns the subtree of a given node.

        Parameters
        ----------
        new_root : list
            The path from the root of self to the root of the subtree.

        Returns
        -------
        QuantumBacktrackingTree
            The subtree starting at the specified root.
        
        Examples
        --------
        
        We initiate a QuantumBacktrackingTree with trivial reject
        function and create a subtree starting at an accepted node-
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def accept(tree):
                height_cond = (tree.h == 2)
                return height_cond

            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
        
        Create and initiate the parent tree.
        
        >>> depth = 5
        >>> tree = QuantumBacktrackingTree(depth, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        >>> tree.init_node([])
        >>> print(accept(tree))
        {False: 1.0}
        
        We now create the subtree, where the new root has height two, ie. the accept
        function returns ``True``.
        
        >>> subtree = tree.subtree([0,1,0])
        >>> subtree.init_node([])
        >>> print(accept(subtree))
        {True: 1.0}

        """
        return Subtree(self, new_root)
    
    def copy(self):
        """
        Returns a copy of self. Copy means a QuantumBacktrackingTree with identical
        depth, accept/reject functions etc. but with freshly allocated QuantumVariables.

        Returns
        -------
        QuantumBacktrackingTree
            Another instance with the same depth/accept/reject etc.

        """
        return Subtree(self, [])
    
    def find_solution(self, precision, cl_accept = None, measurement_kwargs = {}):
        """
        Determines a path to a solution.

        Parameters
        ----------
        precision : integer
            The precision to perform the quantum phase estimation(s) with.
        cl_accept : function, optional
            A classical version of the accept function of self. Needs to 
            receive a list to indicate a path and returns a bool wether the 
            node is accepted. By default, the accept function of self will be
            evaluated on a simulator.
        measurement_kwargs : dictionary
            A dictionary to give keyword arguments that specify how measurements
            are evaluated. The default is {}.

        Returns
        -------
        List
            A list indicating the path to a node where the accept function
            returns True.

        Examples
        --------
        
        We create a accept function that marks the node [0,1] and a trivial 
        reject function. 
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat, mcx
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def accept(tree):
                height_cond = (tree.h == 1) # The [0,1] node has height 1
                path_cond = QuantumBool()
                mcx(list(tree.branch_qa)[:-1], path_cond, ctrl_state="10")
                return path_cond & height_cond

            @auto_uncompute    
            def reject(tree):
                return QuantumBool()


        Create backtracking tree object:

        >>> depth = 3
        >>> tree = QuantumBacktrackingTree(depth, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        
        Find solution
        
        >>> res = tree.find_solution(4)
        >>> print(res)
        [0, 1]
        
        """
        
        return find_solution(self, precision, cl_accept, measurement_kwargs=measurement_kwargs)

        
    def path_decoder(self, h, branch_qa):
        """
        Returns the path representation for a given constellation of the
        ``h`` and ``branch_qa`` variables. The path representation is a list
        indicating which branches to take starting from the root.
        This function exists because the encoding of the nodes is hardware 
        efficient but inconvenient for humans to read.

        Parameters
        ----------
        h : integer
            The integer describing the height of the node.
        branch_qa : list
            The list of branches to take to reach the root, starting from the node.

        Returns
        -------
        list
            The list of path variables to take to reach the node, starting 
            from the root.

        Examples
        --------
        
        We create a QuantumBacktrackingTree, initiate a node and retrieve the path.
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat, multi_measurement
            from qrisp.quantum_backtracking import QuantumBacktrackingTree

            @auto_uncompute    
            def accept(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
        >>> depth = 5
        >>> tree = QuantumBacktrackingTree(depth, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        >>> tree.init_node([1,0])
        >>> multi_measurement([tree.h, tree.branch_qa])
        {(3, OutcomeArray([0, 1, 0, 0, 0])): 1.0}
        
        Retrieve the path
        
        >>> tree.path_decoder(3, [0,1,0,0,0])
        [1, 0]

        """
        
        l = self.max_depth - h
        return list(branch_qa[:l][::-1])

        
                    
    def statevector_graph(self, return_root = False):
        r"""
        Returns a NetworkX Graph representing the quantum state of the backtracking tree. 
        The nodes have an ``amplitude`` attribute, indicating the complex amplitude of that node.

        Parameters
        ----------
        return_root : bool, optional
            If set to ``True``, this method will also return the root node. The default is False.

        Returns
        -------
        networkx.DiGraph
            A graph representing the statevector.
            
        Examples
        --------
        
        We initialize a backtracking tree, initialize a :math:`\ket{\phi}` state and retrieve
        the statevector graph.
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def accept(tree):
                return (tree.branch_qa[0] == 1) & (tree.branch_qa[1] == 1) & (tree.branch_qa[2] == 1)
        
            
        Create backtracking tree and initialize :math:`\ket{\phi}`.
        
        >>> tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        >>> tree.init_phi([1,1,1])
        >>> statevector_graph = tree.statevector_graph()
        >>> print(statevector_graph.nodes())
        [QBTNode(path = [], amplitude = (0.7071057-2e-08j)), QBTNode(path = [0], amplitude = 0j), QBTNode(path = [1], amplitude = (-0.40824768-1e-08j)), QBTNode(path = [0, 0], amplitude = 0j), QBTNode(path = [0, 1], amplitude = 0j), QBTNode(path = [1, 0], amplitude = 0j), QBTNode(path = [1, 1], amplitude = (0.4082477+4e-08j)), QBTNode(path = [0, 0, 0], amplitude = 0j), QBTNode(path = [0, 0, 1], amplitude = 0j), QBTNode(path = [0, 1, 0], amplitude = 0j), QBTNode(path = [0, 1, 1], amplitude = 0j), QBTNode(path = [1, 0, 0], amplitude = 0j), QBTNode(path = [1, 0, 1], amplitude = 0j), QBTNode(path = [1, 1, 0], amplitude = 0j), QBTNode(path = [1, 1, 1], amplitude = (-0.4082477+0j))]
        >>> statevector_graph, root = tree.statevector_graph(return_root = True)
        >>> print(root)
        QBTNode(path = [], amplitude = (0.7071057-2e-08j))

        """
        
        from networkx import DiGraph
        
        sv_function = self.qs.statevector("function")
        
        res_graph = DiGraph()
        
        root = QBTNode(self, [])
        
        root.amplitude = sv_function(root.sv_specifier())
        
        res_graph.add_node(root)
        
        last_layer = [root]
        
        
        for i in range(self.max_depth):
            
            next_layer = []
            
            for parent_node in last_layer:
                
                for j in range(2**self.branch_qa[0].size):
                        
                    child_node_path = list(parent_node.path) + [self.branch_qa[0].decoder(j)]

                    child_node = QBTNode(self, child_node_path)
                    
                    child_node.amplitude = sv_function(child_node.sv_specifier())
                    
                    res_graph.add_node(child_node)
                    res_graph.add_edge(parent_node, child_node, label = child_node_path[-1])
                    
                    next_layer.append(child_node)
                    
            last_layer = next_layer
        
        if return_root:
            return res_graph, root
        return res_graph
    
    def visualize_statevector(self, pos = None):
        """
        Visualizes the statevector graph.

        Parameters
        ----------
        pos : dict, optional
            A dictionary indicating the positional layout of the nodes. For more information visit 
            `this page <https://networkx.org/documentation/stable/reference/generated/networkx.drawing.nx_pylab.draw.html#networkx.drawing.nx_pylab.draw>`_. 
            By default is suitable will be generated.

        Examples
        --------
        
        We initialize a backtracking tree and visualize:
            
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            import matplotlib.pyplot as plt
            
            @auto_uncompute    
            def reject(tree):
                return QuantumBool()
            
            @auto_uncompute    
            def accept(tree):
                return (tree.branch_qa[0] == 1) & (tree.branch_qa[1] == 1) & (tree.branch_qa[2] == 1)
            
            
        >>> tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        >>> tree.visualize_statevector()
        >>> plt.show()
        
        .. image:: ./root_state_plot.png
            :width: 200
            :alt: Root statevector plot
            :align: left
        
        >>> tree.init_phi([1,1,1])
        >>> tree.visualize_statevector()
        
        .. image:: ./phi_state_plot.png
            :width: 200
            :alt: Root statevector plot
            :align: left
        

        """
        
        G, root = self.statevector_graph(return_root = True)
        
        def tree_layout(G, node, depth, theta_parent, res_dic = {}):
            
            r = depth + 1
            delta_theta = 2*np.pi/self.degree**(depth+1)
            theta_start = theta_parent - 2*np.pi/self.degree**(depth)/4
            
            children = list(G.neighbors(node))
            
            for i in range(len(children)):
                
                theta = theta_start + i*delta_theta
                
                res_dic[children[i]] = (r*np.sin(theta), r*np.cos(theta))
                
                tree_layout(G, children[i], depth+1, theta, res_dic)
                
            return res_dic
            
        
        pos=tree_layout(G, root, 0, 0)
        pos[root] = (0,0)

        import colorsys
        def complex_to_color(cnumber):
            
            
            angle = np.angle(cnumber)
            radius = np.abs(cnumber)
            
            # Normalize the angle to the range [0, 2*pi)
            angle = (angle +np.pi*5/2)% (2 * np.pi)
        
            # Map the angle to the hue component of the color
            hue = angle / (2*np.pi)
        
            # Map the radius to the saturation and value components of the color
            saturation = 1
            value = 1
        
            # Convert the HSV components to RGB
            hsv_color = (hue, saturation, value)
            rgb_color = colorsys.hsv_to_rgb(*hsv_color)
            
            from scipy.special import expit
            
            intensity = expit((radius-0.2)*10)
            
            
            # Convert the RGB components to hexadecimal format
            hex_color = '#{:02x}{:02x}{:02x}'.format(
                int(rgb_color[0] * 255*intensity),
                int(rgb_color[1] * 255*intensity),
                int(rgb_color[2] * 255*intensity)
            )
        
            return hex_color

        colors = [complex_to_color(node.amplitude) for node in G.nodes()]

        nx.draw(G, pos)
        nx.draw_networkx_nodes(G, pos, node_color = colors)

        edge_labels = dict([((n1, n2), l)
                            for n1, n2, l in G.edges(data = "label")])

        nx.draw_networkx_edge_labels(G, pos=pos, edge_labels=edge_labels)
    
    def statevector(self):
        """
        Returns a SymPy statevector object representing the state of the tree 
        with decoded node labels.

        Returns
        -------
        state : sympy.Expr
            A SymPy quantum state representing the statevector of the tree.

        Examples
        --------
        
        We create a QuantumBacktrackingTree with and investigate the action of the 
        :meth:`quantum step diffuser <qrisp.quantum_backtracking.QuantumBacktrackingTree.qstep_diffuser>`
        
        ::
            
            from qrisp import auto_uncompute, QuantumBool, QuantumFloat
            from qrisp.quantum_backtracking import QuantumBacktrackingTree
            
            @auto_uncompute    
            def accept(tree):
                height_cond = (tree.h == 1) # The [0,1] node has height 1
                path_cond = QuantumBool()
                mcx(list(tree.branch_qa)[:-1], path_cond, ctrl_state="10")
                return path_cond & height_cond

            @auto_uncompute    
            def reject(tree):
                height_cond = (tree.h == 2) # The [1] node has height 2
                path_cond = QuantumBool()
                mcx(list(tree.branch_qa)[0], path_cond, ctrl_state="1")
                return path_cond & height_cond

        
        Create tree and initialize a node where neither accept nor reject are True.
        
        >>> tree = QuantumBacktrackingTree(3, QuantumFloat(1, name = "branch_qf*"), accept, reject)
        >>> tree.init_node([0,0])
        
        Evaluate statevector
        
        >>> print(tree.statevector())
        1.0*|[0, 0]>
        >>> tree.qstep_diffuser(even = False)
        >>> print(tree.statevector())
        -0.666660010814667*|[0, 0, 0]> - 0.666660010814667*|[0, 0, 1]> + 0.333330005407333*|[0, 0]>
        
        We see that the :meth:`quantum step diffuser <qrisp.quantum_backtracking.QuantumBacktrackingTree.qstep_diffuser>`
        moves the state to the children of the [0,0] node (ie. [0,0,0] and [0,0,1]).
        
        We now investigate how it behaves on nodes that are accepted/rejected:
            
        Initiate a new tree
        
        >>> tree = tree.copy()
        >>> tree.init_node([0,1])
        >>> tree.qstep_diffuser(even = False)
        >>> tree.statevector()
        1.0*|[0, 1]>
        
        As expected, the accepted node is invariant.
        
        To investigate the rejected node, we create another copy:
            
        >>> tree = tree.copy()
        >>> tree.init_node([1])
        >>> tree.qstep_diffuser(even = True)
        >>> tree.statevector()
        -0.999989986419678*|[1]>
        
        As expected, the node has eigenvalue -1 (up to numerical precision).
        
        If you are unsure why these statevectors are eigenvector please check 
        `the paper <https://arxiv.org/abs/1509.02374>`_.
        
        """
        
        sv_function = self.qs.statevector("function", decimals = 10)
        
        #Internal qvs are the quantum variables that specify a backtrackingtree node
        internal_qvs = [self.h, self.branch_workspace] + list(self.branch_qa)
        #External qvs are any quantum variables that are also registered in the QuantumSession
        #but don't specify a node
        external_qvs = list(self.qs.qv_list)
        
        #Remove the internal qvs from the external qv_list        
        for qv in internal_qvs:
            for i in range(len(external_qvs)):
                if hash(external_qvs[i]) == hash(qv):
                    external_qvs.pop(i)
                    break
        
        #Get a list of possible labels for each qv
        
        internal_qv_labels = []
        for qv in internal_qvs:
            label_list = []
            for i in range(2**qv.size):
                label_list.append(qv.decoder(i))
            internal_qv_labels.append(label_list)
        
        external_qv_labels = []
        for qv in external_qvs:
            label_list = []
            for i in range(2**qv.size):
                label_list.append(qv.decoder(i))
            external_qv_labels.append(label_list)
        
        #This retrieves a list of all possible constellations of labels
        internal_label_product = list(product(*internal_qv_labels))
        external_label_product = list(product(*external_qv_labels))
        
        #This will be the sympy object that is returned
        res_state = 0

        #Go through all internal label consteallations (ie. node states)        
        for internal_label_const in internal_label_product[::-1]:
            
            #Get the path to that node state
            path = self.path_decoder(internal_label_const[0], internal_label_const[2:])
            
            #Create a label dic for the sv_function
            internal_label_dic = {internal_qvs[i] : internal_label_const[i] for i in range(len(internal_qvs))}
            
            #If there are no external qvs, we can simply call the sv_function
            #with the label dic                        
            if len(external_qvs) == 0:
                
                amplitude = sv_function(internal_label_dic)
                
                if abs(amplitude) < 1E-5:
                    continue
                
                #Add the corresponding ket                
                res_state  += np.round(amplitude, 5) * OrthogonalKet(str(path))
            
            
            #If there are external qvs we do a similar procedure to go through
            #all label constellations
            else:
                
                for external_label_const in external_label_product:
                    
                    
                    #Set up the external label dic
                    external_label_dic = {external_qvs[i] : external_label_const[i] for i in range(len(external_qvs))}
                    
                    #Integrate the internal label dic
                    external_label_dic.update(internal_label_dic)
                    
                    #Retrieve the amplitude
                    amplitude = sv_function(external_label_dic)
                    
                    if abs(amplitude) < 1E-5:
                        continue
                    
                    external_ket_expr = 1
                    #Generate the ket expression for the external qvs                    
                    for label in external_label_const:
                        external_ket_expr *= OrthogonalKet(label)
                    
                    #Add the corresponding state
                    res_state += amplitude * OrthogonalKet(str(path)) * external_ket_expr
            
        return res_state 
        
        
        
"""
This function realizes the operator U_x, which has the property

U_x |x> = |psi_x>

For more details on these objects, check the details of the 
paper (https://arxiv.org/abs/1509.02374)or the beginning of this file.

The general idea to implement this operator are the following two steps:
    
    1. Manipulatre l such that |l> -> 1/N(|l> + c*|l+1>) with suitable N,c \in R
    2. Manipulate branch_qa controlled on l+1 to incorporate the new branches
    
The value of the constant c depends on wether x is the root or a terminal node.

For terminal nodes, c = 0.    
For the root c = n**0.5*d_x**0.5
Otherwise c = d_x**0.5

Where d_x is the degree of the node.

"""             

def psi_prep(x, even = True):
    
    #Determine c
    c = x.degree**0.5
    
    #The step |h> -> 1/N(|h> + c*|h-1>) will be performed by a ry gate
    phase = -np.arctan(c)*2
    root_phase = -np.arctan((c*np.sqrt(x.max_depth)))*2
    
    #We distinguish wether h is odd. This is because if h is odd,
    #the ry gate on the significance 0 qubit acts different
    oddity_qb = x.h.significant(0) 
    
    
    #Distinguish the cases wether psi prepares an even node
    if not even:
        
        #Because the h attribute describes the height of the tree, 
        #the root node can have even or odd h depending on what the maximum
        #depth of the tree is.
        #If the maximum depth is odd, the root node is also odd.
        if x.max_depth%2:
            
            #Perform the ry rotation
            ry(phase, oddity_qb)
            
            #If x is the root (ie. h = x.max_depth), we reverse the previous 
            #ry gate and instead perform the root phase
            with control(x.h[1:], ctrl_state = x.max_depth>>1):
                ry(root_phase - phase, oddity_qb)
            
            #This step initializes the new branch_qa entry.
            with control(oddity_qb, ctrl_method = "gray", ctrl_state = "0"):
                #The QuantumVariable x.branch_workspace will always be in the |0> state
                #at this point of the algorithm, so we swap that |0> state to the first
                #entry of branch_qa and initialize using H-gates to reach uniform superposition.
                cyclic_shift(list(x.branch_qa) + [x.branch_workspace])
                
                h(x.branch_qa[0])
                
        #If the height is even, the h value of the root is also even, therefore
        #the odd case of the psi_prep function does not need to deal with it.
        #Instead it should leave the root invariant, since the state with
        #h = max_depth + 1 is non algorithmic
        else:
            
            #This control environment checks wether h is the root state
            #and only executes it's content if this is not the case
            with control(x.h[1:], ctrl_state = x.max_depth>>1, invert = True):
                
                ry(phase, oddity_qb)
                
                #Initialize branch_qa entry
                with control(oddity_qb, ctrl_method = "gray", ctrl_state = "0"):
                    cyclic_shift(list(x.branch_qa) + [x.branch_workspace])
                    h(x.branch_qa[0])
            
    else:
        
        #For the even case, the oddity qubit will be in the |0> state, so our
        #approach of simply applying an ry will not work anymore as it would
        #perform the operation |h> -> 1/N(|h> + c|h+1>) ie. it would move upward
        
        #To circumvent, we temporarily decrement h such that the oddity qubit is
        #in the |1> state.
        
        increment(x.h, -1)
        #This control environment makes sure that h = 0 nodes 
        #(after decrementation h = -1) are not subjected to an ry gate
        with control(x.h[1:], ctrl_state = -1):
            ry(-phase, oddity_qb)
        
        #Similar to the even case, we distinguish between the cases of the tree having
        #even or odd maximum depth
        if not x.max_depth%2:
            
            #Apply the ry rotation
            ry(phase, oddity_qb)
                
            #If x is the root (ie. h = x.max_depth-1), we reverse the previous 
            #ry gate and instead perform the root phase
            with control(x.h[1:], ctrl_state = (x.max_depth-1)>>1):
                ry(root_phase - phase, oddity_qb)
            
            #Initialize the new branch_qa entry
            with control(oddity_qb, ctrl_state = "0", ctrl_method = "gray"):
                
                cyclic_shift(list(x.branch_qa) + [x.branch_workspace])
                h(x.branch_qa[0])
            
        else:
            
            #Perform a similar logic as for the odd case
            with control(x.h[1:], ctrl_state = (x.max_depth-1)>>1, invert = True):
                ry(phase, oddity_qb)
            
                with control(oddity_qb, ctrl_state = "0", ctrl_method = "gray"):
                    
                    cyclic_shift(list(x.branch_qa) + [x.branch_workspace])
                    h(x.branch_qa[0])
        
        #Reverse the decrementation
        increment(x.h, 1)


class Subtree(QuantumBacktrackingTree):
    
    def __init__(self, parent_tree, root_path):
        
        if len(root_path) > parent_tree.max_depth:
            raise Exception("Tried to initialise subtree with root path longer than maximum depth")
        
        QuantumBacktrackingTree.__init__(self, 
                                         parent_tree.max_depth - len(root_path), 
                                         parent_tree.branch_workspace,
                                         parent_tree.accept_function,
                                         parent_tree.reject_function
                                         )
        
        self.embedding_array = QuantumArray(qtype = self.branch_qa.qtype, shape = len(root_path), qs = self.qs)
        self.branch_qa = np.concatenate((self.branch_qa, self.embedding_array))
        
        self.root_path = root_path
        self.original_tree = parent_tree
    
    def init_node(self, path):
        
        self.h[:] = self.max_depth - len(path)
        
        path = self.root_path + path
        
        if len(path):
            self.branch_qa[:len(path)] = path[::-1]
    
    def init_phi(self, path):
        
        h_state = {}
        h_state[self.max_depth] = (self.max_depth)**0.5

        for i in range(1, len(path)+1):
            h_state[self.max_depth - i] = (-1)**(i)

        self.h[:] = h_state
        
        with self.h == self.max_depth:
            for k in range(len(self.root_path)):
                self.branch_qa[k][:] = self.root_path[::-1][k]

        for i in range(1, len(path)+1):
            with self.h == self.max_depth - i:
                for j in range(i):
                    self.branch_qa[j].encode(path[::-1][j], permit_dirtyness = True)
                    
                for k in range(len(self.root_path)):
                    self.branch_qa[k+i][:] = self.root_path[::-1][k]
                    
    def subtree(self, path):
        return self.original_tree.subtree(self.root_path + path)
        
        
        
def find_solution(tree, precision, cl_accept = None, traversed_nodes = None, measurement_kwargs = {}):
    #The idea of this function is to use the quantum algorithm to check wether
    #a the subtree of a given node contains a solution and then recursively call
    #this function on that subtree.
    
    
    #If there is no classical accept function given, we create a copy of the original
    #tree and evaluate the quantum accept function on that node via the simulator
    if cl_accept is None:
        def cl_accept(path):
            if isinstance(tree, Subtree):
                copied_tree = tree.original_tree.copy()
            else:
                copied_tree = tree.copy()
            copied_tree.init_node(path)
            accept_qbl = copied_tree.accept()
            mes_res = accept_qbl.get_measurement()
            return mes_res == {True : 1}
            
    
    #The first step is to check wether the current root is a solution
    if isinstance(tree, Subtree):
        path = tree.root_path
    else:
        path = []

    if cl_accept(path):
        return []
    elif tree.max_depth == 0:
        return None
    
    #This list keeps track of which nodes have already been checked for solutions
    if traversed_nodes is None:
        traversed_nodes = []

    #Initialize the root node
    tree.init_node([])
    
    #Perform quantum phase estimation
    qpe_res = tree.estimate_phase(precision)
    
    #Retrieve the measurement results
    mes_res = multi_measurement([qpe_res, tree.h, tree.branch_qa], **measurement_kwargs)
    
    #We will first check wether there is a solution    
    #The s variable will contain the probability to measure
    #the qpe_res == 0 branch.
    s = 0
    #This list will contain the possible branches
    new_branches = []
    
    for k, v in mes_res.items():
        #k[0] is the value of qpe_res
        if k[0] == 0:
            #If the measurement result is part of the qpe == 0 branch, add the
            #probability to s
            s += v
            
            new_branches.append(k)
    #If the probability is less then 0.25, there is no solution
    if s <= 0.25:
        return None
    
    #If the probability is between 0.25 and 0.375, the qpe needs more precision
    if s <= 0.375:
        raise Exception("Executed find solution method of quantum backtracking algorithm with insufficient precision")
    
    
    #To find the next node to check we will use a heuristic.
    #After measurement of the 0 branch, the tree is collapsed to a state which 
    #also contains the |phi> state. The phi state is a superposition of nodes 
    #leading to the desired solution.
    #We assume that the outcome with the smallest tree.h value is the state 
    #corresponding to |phi>. This proved to be the case in every situation we tested.
    #If this assumption for whichever reason is not correct, the solution will still
    #be found because of the recursive nature of this algorithm.
    
    #Sort for the value of tree.h
    new_branches.sort(key = lambda x : x[1])
    
    for b in new_branches:
        
        #Get the path to the new node
        new_path = tree.path_decoder(b[1], b[2])
        
        if tuple(path + new_path) in traversed_nodes or len(new_path) == 0:
            continue
        
        #Generate the subtree        
        subtree = tree.subtree(new_path)
        
        #Recursive call
        sub_sol = find_solution(subtree, precision, cl_accept, traversed_nodes)
        
        #If a solution has been found, concatenate the pathes
        if sub_sol is not None:
            solution = path + new_path + sub_sol
            break
        else:
            traversed_nodes.append(tuple(path + new_path))
        
    else:
        raise Exception("Executed find solution method of quantum backtracking algorithm with insufficient precision")

    return solution



class QBTNode:
    
    def __init__(self, tree, path, amplitude = None):
        
        self.h = tree.max_depth - len(path)
        self.path = path
        self.tree = tree
        self.amplitude = amplitude
    
    def __hash__(self):
        return hash(str(self.path))
    
    def sv_specifier(self):
        amplitude_state_specifyer = {self.tree.h : self.tree.max_depth - len(self.path),
                                     self.tree.branch_workspace : self.tree.branch_workspace.decoder(0)}
    
        path = list(self.path)
        if isinstance(self.tree, Subtree):
            path = self.tree.root_path + path
    
        for k in range(len(self.tree.branch_qa)):
            if k < len(path):
                amplitude_state_specifyer[self.tree.branch_qa[k]] = path[::-1][k]
            else:
                amplitude_state_specifyer[self.tree.branch_qa[k]] = 0
        
        
        return amplitude_state_specifyer
    
    def __str__(self):
        return "QBTNode(path = " + str(self.path) + ", amplitude = " + str(self.amplitude) + ")"
    
    def __repr__(self):
        return str(self)
