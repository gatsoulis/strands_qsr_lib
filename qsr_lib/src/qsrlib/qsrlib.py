# -*- coding: utf-8 -*-
"""QSRlib module.

"""

from __future__ import print_function, division
from datetime import datetime
from qsrlib_io.world_trace import World_Trace
from qsrlib_utils.utils import merge_world_qsr_traces
from qsrlib_qsrs import *


class QSRlib_Response_Message(object):
    """The response message of QSRlib containing the QSRs and time processing information.

    """
    def __init__(self, qsrs, req_made_at, req_received_at, req_finished_at):
        """Constructor.

        :param qsrs: The computed QSRs in World_QSR_Trace format.
        :type qsrs: World_QSR_Trace
        :param req_made_at: Time the request was made.
        :param req_received_at: Time the request was received.
        :param req_finished_at: Time the request was finished.
        :return:
        """
        self.qsrs = qsrs
        """World_QSR_Trace: Holds the QSRs."""

        self.req_made_at = req_made_at
        """datetime.datetime : Time the request was made."""

        self.req_received_at = req_received_at
        """datetime.datetime : Time the request was received in QSRlib."""

        self.req_finished_at = req_finished_at
        """datetime.datetime : Time the QSRlib finished processing the request."""


class QSRlib_Request_Message(object):
    """Input to QSRlib request calls containing all the necessary data."""
    def __init__(self, which_qsr, input_data, dynamic_args={}, req_made_at=None):
        """Constructor.

        :param which_qsr: The name(s) of the wanted QSR(s) to be computed.
        :type which_qsr: str or list
        :param input_data: The input data.
        :type input_data: World_Trace
        :param dynamic_args: User args passed dynamically during the request.
        :type dynamic_args: dict
        :param req_made_at: Time the request was made.
        :type req_made_at: datetime.datetime
        :return:
        """
        self.which_qsr = which_qsr
        """str or list: The name(s) of the wanted QSR(s) to be computed."""

        if isinstance(input_data, World_Trace):
            self.input_data = input_data
            """World_Trace: The input data."""
        else:
            raise TypeError("input_data must be of type 'World_Trace'")

        self.dynamic_args = dynamic_args
        """ dict: User args passed dynamically during the request."""

        self.made_at = req_made_at if req_made_at else datetime.now()
        """datetime.datetime (`datetime.datetime.now()`): Time the request was made."""


class QSRlib(object):
    """The LIB"""
    def __init__(self, help=False):
        """Constructor.

        `qsrs_registry` is a tuple where the developers have registered the class names of the QSR, and is found in
        `qsrlib_qsrs.__init__.py`.

        :param help: Print helpful message at start.
        :type help: bool
        :return:
        """
        self.__qsrs_registry = self.__check_and_activate_qsrs(qsrs_registry)
        """dict: The registry of the QSRs, a mapping between their unique names and their classes."""

        if help:
            self.help()

    @staticmethod
    def __check_and_activate_qsrs(qsrs_registry):
        """Checks for uniqueness of the QSRs _unique_id and their corresponding class names and then return a dictionary
        with the unique IDs as keys and their corresponding objects.

        :param qsrs_registry: Where developers have registered the QSRs (see constructor source).
        :type qsrs_registry: tuple
        :return: A dictionary with the QSRs _unique_id as keys and an object of their corresponding classes.
        :rtype: dict
        """
        if len(set(qsrs_registry)) != len(qsrs_registry):
            raise KeyError("Repeated class name found")
        qsrs = {}
        for class_name in qsrs_registry:
            o = class_name()
            if o._unique_id in qsrs:
                raise KeyError("Non unique QSR ID <%s> found while processing class <%s> which was mapped to class <%s>"
                               % (o._unique_id, o.__class__.__name__, qsrs[o._unique_id].__class__.__name__))
            else:
                qsrs[o._unique_id] = o
        return qsrs

    # todo turn this into a property get method
    def get_qsrs_registry(self):
        """Getter method.

        :return: The `self.__qsrs_registry` containing the mapping of the unique names of the QSRs and their corresponding generated objects.
        :rtype: dict
        """
        return self.__qsrs_registry

    def help(self):
        """stdout help message about QSRlib"""
        self.__print_qsrs_available()

    def __print_qsrs_available(self):
        """Print the names of the QSRs."""
        print("Supported QSRs are:")
        for i in sorted(self.__qsrs_registry):
            print("-", i)

    def request_qsrs(self, req_msg):
        """Main function of the QSRlib that does all the magic; returns the computed requested QSRs.

        :param req_msg: A request message containing the necessary data and other options.
        :type req_msg: QSRlib_Request_Message
        :return: Response message containing the computed requested QSRs and other information.
        :rtype: QSRlib_Response_Message
        """
        req_received_at = datetime.now()
        world_qsr_traces = []

        # which_qsrs should always be iterable, even it is only a string, to enable the loop
        which_qsrs = req_msg.which_qsr if isinstance(req_msg.which_qsr, (list, tuple)) else [req_msg.which_qsr]
        for which_qsr in which_qsrs:
            world_qsr_traces.append(self.__qsrs_registry[which_qsr].get_qsrs(input_data=req_msg.input_data,
                                                                             dynamic_args=req_msg.dynamic_args))
        if world_qsr_traces:
            # If the input was a list of QSRs, merge the results
            if isinstance(req_msg.which_qsr, (list, tuple)):
                world_qsr_trace = merge_world_qsr_traces(world_qsr_traces, ",".join(req_msg.which_qsr))
            elif len(world_qsr_traces) == 1:  # Just take the first because the list will only contain that one element
                world_qsr_trace = world_qsr_traces[0]
            else:
                raise RuntimeError("this should never have occured; file an issue for the developers to fix")
        else:
            world_qsr_trace = None

        qsrlib_response = QSRlib_Response_Message(qsrs=world_qsr_trace,
                                                  req_made_at=req_msg.made_at,
                                                  req_received_at=req_received_at,
                                                  req_finished_at=datetime.now())

        return qsrlib_response
