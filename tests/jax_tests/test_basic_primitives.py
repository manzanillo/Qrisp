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

from qrisp import *
from jax import make_jaxpr

def test_basic_primitives():

    def test_function():
        qv = QuantumVariable(2)
        h(qv[0])
        cx(qv[0], qv[1])
        res_bl = measure(qv[0])
        return res_bl

    compare_jaxpr(make_jispr(test_function)(), 
            ['jisp.create_qubits',
             'jisp.get_qubit',
             'jisp.h',
             'jisp.get_qubit',
             'jisp.cx',
             'jisp.measure'])
    
    def test_function():
        qv = QuantumVariable(2)
        
        with QuantumEnvironment():
            h(qv[0])
            cx(qv[0], qv[1])
        
        res_bl = measure(qv[0])
        return res_bl
    
    compare_jaxpr(make_jispr(test_function)(), 
                ['jisp.create_qubits',
                 'jisp.q_env',
                 'jisp.get_qubit',
                 'jisp.measure'])    

    def test_function():
        qv = QuantumVariable(2)
        
        h(qv[0])
        cx(qv[0], qv[1])
        cx(qv[1], qv[0])
        h(qv[1])
        res_bl = measure(qv[0])
        qv.delete()
        return res_bl

    compare_jaxpr(make_jispr(test_function)(), 
                ['jisp.create_qubits',
                 'jisp.get_qubit',
                 'jisp.h',
                 'jisp.get_qubit',
                 'jisp.cx',
                 'jisp.cx',
                 'jisp.h',
                 'jisp.measure',
                 'jisp.delete_qubits'])

    def test_function(a):
        qv = QuantumVariable(2)
        
        rz(np.pi, qv[0])
        p(a, qv[0])
        res_bl = measure(qv[0])
        qv.delete()
        return res_bl

    print(make_jispr(test_function)(2.))
    compare_jaxpr(make_jispr(test_function)(2.), 
                ['jisp.create_qubits',
                 'jisp.get_qubit',
                 'jisp.rz(alpha)',
                 'jisp.p(alpha)',
                 'jisp.measure',
                 'jisp.delete_qubits'])