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

#
# Autogenerated by Thrift Compiler (0.15.0)
#
# DO NOT EDIT UNLESS YOU ARE SURE THAT YOU KNOW WHAT YOU ARE DOING
#
#  options string: py
#

import sys

from thrift.protocol.TProtocol import TProtocolException
from thrift.Thrift import (
    TApplicationException,
    TException,
    TFrozenDict,
    TMessageType,
    TType,
)
from thrift.transport import TTransport
from thrift.TRecursive import fix_spec

all_structs = []


class Qubit(object):
    """
    Attributes:
     - identifier

    """

    def __init__(
        self,
        identifier=None,
    ):
        self.identifier = identifier

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.identifier = (
                        iprot.readString().decode("utf-8", errors="replace")
                        if sys.version_info[0] == 2
                        else iprot.readString()
                    )
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("Qubit")
        if self.identifier is not None:
            oprot.writeFieldBegin("identifier", TType.STRING, 1)
            oprot.writeString(
                self.identifier.encode("utf-8")
                if sys.version_info[0] == 2
                else self.identifier
            )
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class Clbit(object):
    """
    Attributes:
     - identifier

    """

    def __init__(
        self,
        identifier=None,
    ):
        self.identifier = identifier

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.identifier = (
                        iprot.readString().decode("utf-8", errors="replace")
                        if sys.version_info[0] == 2
                        else iprot.readString()
                    )
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("Clbit")
        if self.identifier is not None:
            oprot.writeFieldBegin("identifier", TType.STRING, 1)
            oprot.writeString(
                self.identifier.encode("utf-8")
                if sys.version_info[0] == 2
                else self.identifier
            )
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class Operation(object):
    """
    Attributes:
     - name
     - num_qubits
     - num_clbits
     - params
     - definition

    """

    def __init__(
        self,
        name=None,
        num_qubits=None,
        num_clbits=None,
        params=None,
        definition=None,
    ):
        self.name = name
        self.num_qubits = num_qubits
        self.num_clbits = num_clbits
        self.params = params
        self.definition = definition

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.name = (
                        iprot.readString().decode("utf-8", errors="replace")
                        if sys.version_info[0] == 2
                        else iprot.readString()
                    )
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.I32:
                    self.num_qubits = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.I32:
                    self.num_clbits = iprot.readI32()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.LIST:
                    self.params = []
                    (_etype3, _size0) = iprot.readListBegin()
                    for _i4 in range(_size0):
                        _elem5 = iprot.readDouble()
                        self.params.append(_elem5)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.STRUCT:
                    self.definition = QuantumCircuit()
                    self.definition.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("Operation")
        if self.name is not None:
            oprot.writeFieldBegin("name", TType.STRING, 1)
            oprot.writeString(
                self.name.encode("utf-8") if sys.version_info[0] == 2 else self.name
            )
            oprot.writeFieldEnd()
        if self.num_qubits is not None:
            oprot.writeFieldBegin("num_qubits", TType.I32, 2)
            oprot.writeI32(self.num_qubits)
            oprot.writeFieldEnd()
        if self.num_clbits is not None:
            oprot.writeFieldBegin("num_clbits", TType.I32, 3)
            oprot.writeI32(self.num_clbits)
            oprot.writeFieldEnd()
        if self.params is not None:
            oprot.writeFieldBegin("params", TType.LIST, 4)
            oprot.writeListBegin(TType.DOUBLE, len(self.params))
            for iter6 in self.params:
                oprot.writeDouble(iter6)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.definition is not None:
            oprot.writeFieldBegin("definition", TType.STRUCT, 5)
            self.definition.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class Instruction(object):
    """
    Attributes:
     - op
     - qubits
     - clbits

    """

    def __init__(
        self,
        op=None,
        qubits=None,
        clbits=None,
    ):
        self.op = op
        self.qubits = qubits
        self.clbits = clbits

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.op = Operation()
                    self.op.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.LIST:
                    self.qubits = []
                    (_etype10, _size7) = iprot.readListBegin()
                    for _i11 in range(_size7):
                        _elem12 = Qubit()
                        _elem12.read(iprot)
                        self.qubits.append(_elem12)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.clbits = []
                    (_etype16, _size13) = iprot.readListBegin()
                    for _i17 in range(_size13):
                        _elem18 = Clbit()
                        _elem18.read(iprot)
                        self.clbits.append(_elem18)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("Instruction")
        if self.op is not None:
            oprot.writeFieldBegin("op", TType.STRUCT, 1)
            self.op.write(oprot)
            oprot.writeFieldEnd()
        if self.qubits is not None:
            oprot.writeFieldBegin("qubits", TType.LIST, 2)
            oprot.writeListBegin(TType.STRUCT, len(self.qubits))
            for iter19 in self.qubits:
                iter19.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.clbits is not None:
            oprot.writeFieldBegin("clbits", TType.LIST, 3)
            oprot.writeListBegin(TType.STRUCT, len(self.clbits))
            for iter20 in self.clbits:
                iter20.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class QuantumCircuit(object):
    """
    Attributes:
     - qubits
     - clbits
     - data
     - init

    """

    def __init__(
        self,
        qubits=None,
        clbits=None,
        data=None,
        init=True,
    ):
        self.qubits = qubits
        self.clbits = clbits
        self.data = data
        self.init = init

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.LIST:
                    self.qubits = []
                    (_etype24, _size21) = iprot.readListBegin()
                    for _i25 in range(_size21):
                        _elem26 = Qubit()
                        _elem26.read(iprot)
                        self.qubits.append(_elem26)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.LIST:
                    self.clbits = []
                    (_etype30, _size27) = iprot.readListBegin()
                    for _i31 in range(_size27):
                        _elem32 = Clbit()
                        _elem32.read(iprot)
                        self.clbits.append(_elem32)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.data = []
                    (_etype36, _size33) = iprot.readListBegin()
                    for _i37 in range(_size33):
                        _elem38 = Instruction()
                        _elem38.read(iprot)
                        self.data.append(_elem38)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.BOOL:
                    self.init = iprot.readBool()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("QuantumCircuit")
        if self.qubits is not None:
            oprot.writeFieldBegin("qubits", TType.LIST, 1)
            oprot.writeListBegin(TType.STRUCT, len(self.qubits))
            for iter39 in self.qubits:
                iter39.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.clbits is not None:
            oprot.writeFieldBegin("clbits", TType.LIST, 2)
            oprot.writeListBegin(TType.STRUCT, len(self.clbits))
            for iter40 in self.clbits:
                iter40.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.data is not None:
            oprot.writeFieldBegin("data", TType.LIST, 3)
            oprot.writeListBegin(TType.STRUCT, len(self.data))
            for iter41 in self.data:
                iter41.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.init is not None:
            oprot.writeFieldBegin("init", TType.BOOL, 4)
            oprot.writeBool(self.init)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class ConnectivityEdge(object):
    """
    Attributes:
     - qb1
     - qb2

    """

    def __init__(
        self,
        qb1=None,
        qb2=None,
    ):
        self.qb1 = qb1
        self.qb2 = qb2

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRUCT:
                    self.qb1 = Qubit()
                    self.qb1.read(iprot)
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.STRUCT:
                    self.qb2 = Qubit()
                    self.qb2.read(iprot)
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("ConnectivityEdge")
        if self.qb1 is not None:
            oprot.writeFieldBegin("qb1", TType.STRUCT, 1)
            self.qb1.write(oprot)
            oprot.writeFieldEnd()
        if self.qb2 is not None:
            oprot.writeFieldBegin("qb2", TType.STRUCT, 2)
            self.qb2.write(oprot)
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


class BackendStatus(object):
    """
    Attributes:
     - name
     - online
     - qubit_list
     - elementary_ops
     - connectivity_map

    """

    def __init__(
        self,
        name=None,
        online=None,
        qubit_list=None,
        elementary_ops=None,
        connectivity_map=None,
    ):
        self.name = name
        self.online = online
        self.qubit_list = qubit_list
        self.elementary_ops = elementary_ops
        self.connectivity_map = connectivity_map

    def read(self, iprot):
        if (
            iprot._fast_decode is not None
            and isinstance(iprot.trans, TTransport.CReadableTransport)
            and self.thrift_spec is not None
        ):
            iprot._fast_decode(self, iprot, [self.__class__, self.thrift_spec])
            return
        iprot.readStructBegin()
        while True:
            (fname, ftype, fid) = iprot.readFieldBegin()
            if ftype == TType.STOP:
                break
            if fid == 1:
                if ftype == TType.STRING:
                    self.name = (
                        iprot.readString().decode("utf-8", errors="replace")
                        if sys.version_info[0] == 2
                        else iprot.readString()
                    )
                else:
                    iprot.skip(ftype)
            elif fid == 2:
                if ftype == TType.BOOL:
                    self.online = iprot.readBool()
                else:
                    iprot.skip(ftype)
            elif fid == 3:
                if ftype == TType.LIST:
                    self.qubit_list = []
                    (_etype45, _size42) = iprot.readListBegin()
                    for _i46 in range(_size42):
                        _elem47 = Qubit()
                        _elem47.read(iprot)
                        self.qubit_list.append(_elem47)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 4:
                if ftype == TType.LIST:
                    self.elementary_ops = []
                    (_etype51, _size48) = iprot.readListBegin()
                    for _i52 in range(_size48):
                        _elem53 = Operation()
                        _elem53.read(iprot)
                        self.elementary_ops.append(_elem53)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            elif fid == 5:
                if ftype == TType.LIST:
                    self.connectivity_map = []
                    (_etype57, _size54) = iprot.readListBegin()
                    for _i58 in range(_size54):
                        _elem59 = ConnectivityEdge()
                        _elem59.read(iprot)
                        self.connectivity_map.append(_elem59)
                    iprot.readListEnd()
                else:
                    iprot.skip(ftype)
            else:
                iprot.skip(ftype)
            iprot.readFieldEnd()
        iprot.readStructEnd()

    def write(self, oprot):
        if oprot._fast_encode is not None and self.thrift_spec is not None:
            oprot.trans.write(
                oprot._fast_encode(self, [self.__class__, self.thrift_spec])
            )
            return
        oprot.writeStructBegin("BackendStatus")
        if self.name is not None:
            oprot.writeFieldBegin("name", TType.STRING, 1)
            oprot.writeString(
                self.name.encode("utf-8") if sys.version_info[0] == 2 else self.name
            )
            oprot.writeFieldEnd()
        if self.online is not None:
            oprot.writeFieldBegin("online", TType.BOOL, 2)
            oprot.writeBool(self.online)
            oprot.writeFieldEnd()
        if self.qubit_list is not None:
            oprot.writeFieldBegin("qubit_list", TType.LIST, 3)
            oprot.writeListBegin(TType.STRUCT, len(self.qubit_list))
            for iter60 in self.qubit_list:
                iter60.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.elementary_ops is not None:
            oprot.writeFieldBegin("elementary_ops", TType.LIST, 4)
            oprot.writeListBegin(TType.STRUCT, len(self.elementary_ops))
            for iter61 in self.elementary_ops:
                iter61.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        if self.connectivity_map is not None:
            oprot.writeFieldBegin("connectivity_map", TType.LIST, 5)
            oprot.writeListBegin(TType.STRUCT, len(self.connectivity_map))
            for iter62 in self.connectivity_map:
                iter62.write(oprot)
            oprot.writeListEnd()
            oprot.writeFieldEnd()
        oprot.writeFieldStop()
        oprot.writeStructEnd()

    def validate(self):
        return

    def __repr__(self):
        L = ["%s=%r" % (key, value) for key, value in self.__dict__.items()]
        return "%s(%s)" % (self.__class__.__name__, ", ".join(L))

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not (self == other)


all_structs.append(Qubit)
Qubit.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRING,
        "identifier",
        "UTF8",
        None,
    ),  # 1
)
all_structs.append(Clbit)
Clbit.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRING,
        "identifier",
        "UTF8",
        None,
    ),  # 1
)
all_structs.append(Operation)
Operation.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRING,
        "name",
        "UTF8",
        None,
    ),  # 1
    (
        2,
        TType.I32,
        "num_qubits",
        None,
        None,
    ),  # 2
    (
        3,
        TType.I32,
        "num_clbits",
        None,
        None,
    ),  # 3
    (
        4,
        TType.LIST,
        "params",
        (TType.DOUBLE, None, False),
        None,
    ),  # 4
    (
        5,
        TType.STRUCT,
        "definition",
        [QuantumCircuit, None],
        None,
    ),  # 5
)
all_structs.append(Instruction)
Instruction.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRUCT,
        "op",
        [Operation, None],
        None,
    ),  # 1
    (
        2,
        TType.LIST,
        "qubits",
        (TType.STRUCT, [Qubit, None], False),
        None,
    ),  # 2
    (
        3,
        TType.LIST,
        "clbits",
        (TType.STRUCT, [Clbit, None], False),
        None,
    ),  # 3
)
all_structs.append(QuantumCircuit)
QuantumCircuit.thrift_spec = (
    None,  # 0
    (
        1,
        TType.LIST,
        "qubits",
        (TType.STRUCT, [Qubit, None], False),
        None,
    ),  # 1
    (
        2,
        TType.LIST,
        "clbits",
        (TType.STRUCT, [Clbit, None], False),
        None,
    ),  # 2
    (
        3,
        TType.LIST,
        "data",
        (TType.STRUCT, [Instruction, None], False),
        None,
    ),  # 3
    (
        4,
        TType.BOOL,
        "init",
        None,
        True,
    ),  # 4
)
all_structs.append(ConnectivityEdge)
ConnectivityEdge.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRUCT,
        "qb1",
        [Qubit, None],
        None,
    ),  # 1
    (
        2,
        TType.STRUCT,
        "qb2",
        [Qubit, None],
        None,
    ),  # 2
)
all_structs.append(BackendStatus)
BackendStatus.thrift_spec = (
    None,  # 0
    (
        1,
        TType.STRING,
        "name",
        "UTF8",
        None,
    ),  # 1
    (
        2,
        TType.BOOL,
        "online",
        None,
        None,
    ),  # 2
    (
        3,
        TType.LIST,
        "qubit_list",
        (TType.STRUCT, [Qubit, None], False),
        None,
    ),  # 3
    (
        4,
        TType.LIST,
        "elementary_ops",
        (TType.STRUCT, [Operation, None], False),
        None,
    ),  # 4
    (
        5,
        TType.LIST,
        "connectivity_map",
        (TType.STRUCT, [ConnectivityEdge, None], False),
        None,
    ),  # 5
)
fix_spec(all_structs)
del all_structs
