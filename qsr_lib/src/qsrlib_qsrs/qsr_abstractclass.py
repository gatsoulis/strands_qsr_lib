# -*- coding: utf-8 -*-
"""Provides the abstract class of the QSR makers.

:Author: Yiannis Gatsoulis <y.gatsoulis@leeds.ac.uk>
:Organization: University of Leeds
:Date: 10 September 2014
:Version: 0.1
:Status: Development
:Copyright: STRANDS default
"""

from __future__ import print_function, division
import abc
import yaml
import os


class QSR_Abstractclass(object):
    """Abstract class for the QSR makers"""
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._unique_id = ""  # must be the same that goes in the QSRlib.__qsrs_registration
        self.all_possible_relations = []

    def help(self):
        self.custom_help()

    def check_input(self, input_data):
        error, msg = self.custom_checks(input_data)
        return error, msg

    def get(self, *args, **kwargs):
        error_code, error_msg = self.check_input(input_data=kwargs["input_data"])
        if error_code > 0:
            print("ERROR:", error_msg)
            self.help()
            print("\nFailed to compute QSRs")
            return False
        return self.make(*args, **kwargs)

    def check_qsrs_for_data_exist(self, objects_names, qsrs_for):
        if not objects_names:
            error_found = True if qsrs_for else False
            return [], error_found
        if not isinstance(qsrs_for, (list, tuple)):
            raise TypeError("qsrs_for must be a list or tuple")
        qsrs_for_ret, error_found = [], False
        for p in qsrs_for:
            if isinstance(p, str):
                if p in objects_names:
                    qsrs_for_ret.append(p)
            elif isinstance(p, (list, tuple)):
                tuple_data_exists = True
                for o in p:
                    if o not in objects_names:
                        tuple_data_exists = False
                        error_found = True
                        break
                if tuple_data_exists:
                    qsrs_for_ret.append(p)
            else:
                raise TypeError("Elements of 'qsrs_for' must be strings and/or lists/tuples")
        qsrs_for_ret, error_found = self.custom_checks_for_qsrs_for(qsrs_for_ret, error_found)
        return qsrs_for_ret, error_found

    @abc.abstractmethod
    def custom_help(self):
        return

    @abc.abstractmethod
    def custom_checks(self, input_data):
        return 0, ""

    @abc.abstractmethod
    def custom_checks_for_qsrs_for(self, qsrs_for, error_found):
        """Custom checks of the qsrs_for field.
        Hint: If you have to iterate over the qsrs_for make sure you do it on a copy of it or there might be dragons,
        e.g.:
         for p in list(qsrs_for):
            if p is not valid:
                qsrs_for.remove(p)
                error_found = True

        :param qsrs_for: list of strings and/or tuples for which QSRs will be computed
        :param error_found: if an error was found in the qsrs_for that violates the QSR rules
        :return: qsrs_for, error_found
        """

        return qsrs_for, error_found

    @abc.abstractmethod
    def make(self, *args, **kwargs):
        """Abstract method that needs to be implemented by the QSR makers

        :param args: not really used at the moment
        :param kwargs:
                    - "input_data": Input_Data_Block
        :return:
        """
        return

    def set_from_config_file(self, path):
        try:
            import rospkg
        except ImportError:
            raise ImportError("Module rospkg not found; setting from config file works for now only within the ROS eco-system")
        if path is None:
            path = os.path.join(rospkg.RosPack().get_path("qsr_lib"), "cfg/defaults.yml")
        else:
            path_ext = os.path.splitext(path)[1]
            if path_ext != ".yml" and path_ext != ".yaml":
                print("ERROR (qsr_abstractclass.py/set_from_config_file): Only yaml files are supported")
                raise ValueError
        with open(path, "r") as f:
            document = yaml.load(f)
        self.custom_set_from_config_file(document)

    @abc.abstractmethod
    def custom_set_from_config_file(self, document):
        return

    def handle_future(self, future, v, k):
        return {k: v} if future else v
