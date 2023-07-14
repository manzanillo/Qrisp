"""
/********************************************************************************
* Copyright (c) 2023 the Qrisp authors
*
* This program and the accompanying materials are made available under the
* terms of the Eclipse Public License 2.0 which is available at
* http://www.eclipse.org/legal/epl-2.0.
*
* This Source Code may also be made available under the following Secondary
* Licenses when the conditions for such availability set forth in the Eclipse
* Public License, v. 2.0 are satisfied: GNU General Public License, version 2 
* or later with the GNU Classpath Exception which is
* available at https://www.gnu.org/software/classpath/license.html.
*
* SPDX-License-Identifier: EPL-2.0 OR GPL-2.0-or-later WITH Classpath-exception-2.0
********************************************************************************/
"""


def test_quantum_arithmetic():
    import numpy as np
    from qrisp import h, multi_measurement, q_div, QuantumFloat

    def test_arithmetic_helper(qf_0, qf_1, operation):
        qf_0 = qf_0.duplicate()
        qf_1 = qf_1.duplicate()

        h(qf_0)
        h(qf_1)

        if operation == "add":
            qf_res = qf_0 + qf_1
        elif operation == "sub":
            qf_res = qf_0 - qf_1
        elif operation == "mul":
            qf_res = qf_0 * qf_1
        elif operation == "div":
            qf_res = q_div(qf_0, qf_1, prec=3)

        mes_res = multi_measurement([qf_0, qf_1, qf_res])

        for a, b, c in mes_res.keys():
            if operation == "add":
                assert a + b == c
            elif operation == "sub":
                assert a - b == c
            elif operation == "mul":
                assert a * b == c
            elif operation == "div":
                if b == 0:
                    continue
                assert abs(a / b - c) < 2 ** (-3)

        statevector = qf_res.qs.statevector("array")
        angles = np.angle(
            statevector[
                np.abs(statevector) > 1 / 2 ** ((qf_0.size + qf_1.size) / 2 + 1)
            ]
        )

        # Test correct phase behavior
        assert np.sum(np.abs(angles)) < 0.1

    a = QuantumFloat(3, -1, signed=True)
    b = QuantumFloat(5, 1, signed=False)

    for operation in ["add", "sub", "mul", "div"]:
        print(operation)
        test_arithmetic_helper(a, b, operation)

    a = QuantumFloat(2, 1, signed=True)
    b = QuantumFloat(3, 0, signed=True)

    for operation in ["add", "sub", "mul", "div"]:
        test_arithmetic_helper(a, b, operation)

    # Test tensordot
    from qrisp import QuantumFloat, QuantumArray, tensordot, OutcomeArray

    qf = QuantumFloat(3, 0, signed=False)
    q_tensor_0 = QuantumArray(qf, shape=(4, 4))
    q_tensor_0[:] = np.eye(4)
    q_tensor_0 = q_tensor_0.reshape(2, 2, 2, 2)
    q_tensor_1 = QuantumArray(qf, shape=(2, 2))
    q_tensor_1[:] = [[0, 1], [1, 0]]
    res = tensordot(q_tensor_0, q_tensor_1, (-1, 0))

    assert res.get_measurement() == {
        OutcomeArray(
            [[[[0, 1], [0, 0]], [[1, 0], [0, 0]]], [[[0, 0], [0, 1]], [[0, 0], [1, 0]]]]
        ): 1.0
    }

    # Test inplace multiplication
    b = QuantumFloat(5, signed=True)
    b[:] = 3
    h(b[0])
    h(b[-1])
    b *= -4
    assert b.get_measurement() == {116: 0.25, 120: 0.25, -12: 0.25, -8: 0.25}
