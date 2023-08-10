# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.connectivity_edge import ConnectivityEdge
from openapi_server.models.qubit import Qubit
from openapi_server import util

from openapi_server.models.connectivity_edge import ConnectivityEdge  # noqa: E501
from openapi_server.models.qubit import Qubit  # noqa: E501

class BackendStatus(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, name=None, online=None, qubit_list=None, elementary_ops=None, connectivity_map=None):  # noqa: E501
        """BackendStatus - a model defined in OpenAPI

        :param name: The name of this BackendStatus.  # noqa: E501
        :type name: str
        :param online: The online of this BackendStatus.  # noqa: E501
        :type online: bool
        :param qubit_list: The qubit_list of this BackendStatus.  # noqa: E501
        :type qubit_list: List[Qubit]
        :param elementary_ops: The elementary_ops of this BackendStatus.  # noqa: E501
        :type elementary_ops: List[int]
        :param connectivity_map: The connectivity_map of this BackendStatus.  # noqa: E501
        :type connectivity_map: List[ConnectivityEdge]
        """
        self.openapi_types = {
            'name': str,
            'online': bool,
            'qubit_list': List[Qubit],
            'elementary_ops': List[int],
            'connectivity_map': List[ConnectivityEdge]
        }

        self.attribute_map = {
            'name': 'name',
            'online': 'online',
            'qubit_list': 'qubit_list',
            'elementary_ops': 'elementary_ops',
            'connectivity_map': 'connectivity_map'
        }

        self._name = name
        self._online = online
        self._qubit_list = qubit_list
        self._elementary_ops = elementary_ops
        self._connectivity_map = connectivity_map

    @classmethod
    def from_dict(cls, dikt) -> 'BackendStatus':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BackendStatus of this BackendStatus.  # noqa: E501
        :rtype: BackendStatus
        """
        return util.deserialize_model(dikt, cls)

    @property
    def name(self):
        """Gets the name of this BackendStatus.


        :return: The name of this BackendStatus.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this BackendStatus.


        :param name: The name of this BackendStatus.
        :type name: str
        """
        if name is None:
            raise ValueError("Invalid value for `name`, must not be `None`")  # noqa: E501

        self._name = name

    @property
    def online(self):
        """Gets the online of this BackendStatus.


        :return: The online of this BackendStatus.
        :rtype: bool
        """
        return self._online

    @online.setter
    def online(self, online):
        """Sets the online of this BackendStatus.


        :param online: The online of this BackendStatus.
        :type online: bool
        """
        if online is None:
            raise ValueError("Invalid value for `online`, must not be `None`")  # noqa: E501

        self._online = online

    @property
    def qubit_list(self):
        """Gets the qubit_list of this BackendStatus.


        :return: The qubit_list of this BackendStatus.
        :rtype: List[Qubit]
        """
        return self._qubit_list

    @qubit_list.setter
    def qubit_list(self, qubit_list):
        """Sets the qubit_list of this BackendStatus.


        :param qubit_list: The qubit_list of this BackendStatus.
        :type qubit_list: List[Qubit]
        """

        self._qubit_list = qubit_list

    @property
    def elementary_ops(self):
        """Gets the elementary_ops of this BackendStatus.


        :return: The elementary_ops of this BackendStatus.
        :rtype: List[int]
        """
        return self._elementary_ops

    @elementary_ops.setter
    def elementary_ops(self, elementary_ops):
        """Sets the elementary_ops of this BackendStatus.


        :param elementary_ops: The elementary_ops of this BackendStatus.
        :type elementary_ops: List[int]
        """

        self._elementary_ops = elementary_ops

    @property
    def connectivity_map(self):
        """Gets the connectivity_map of this BackendStatus.


        :return: The connectivity_map of this BackendStatus.
        :rtype: List[ConnectivityEdge]
        """
        return self._connectivity_map

    @connectivity_map.setter
    def connectivity_map(self, connectivity_map):
        """Sets the connectivity_map of this BackendStatus.


        :param connectivity_map: The connectivity_map of this BackendStatus.
        :type connectivity_map: List[ConnectivityEdge]
        """

        self._connectivity_map = connectivity_map
