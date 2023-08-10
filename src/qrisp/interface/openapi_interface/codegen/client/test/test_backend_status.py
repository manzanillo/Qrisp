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

"""
    Cyqlone-Backend Interface

    An API specification for interfacing the high-level language Cyqlone to backend providers.  # noqa: E501

    The version of the OpenAPI document: 0.0.1
    Generated by: https://openapi-generator.tech
"""


import sys
import unittest

import openapi_client
from openapi_client.model.connectivity_edge import ConnectivityEdge
from openapi_client.model.qubit import Qubit

globals()["ConnectivityEdge"] = ConnectivityEdge
globals()["Qubit"] = Qubit
from openapi_client.model.backend_status import BackendStatus


class TestBackendStatus(unittest.TestCase):
    """BackendStatus unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testBackendStatus(self):
        """Test BackendStatus"""
        # FIXME: construct object with mandatory attributes with example values
        # model = BackendStatus()  # noqa: E501
        pass


if __name__ == "__main__":
    unittest.main()
