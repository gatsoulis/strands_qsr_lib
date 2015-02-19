# -*- coding: utf-8 -*-
"""Example that shows how to implement QSR makers.

:Author: Yiannis Gatsoulis <y.gatsoulis@leeds.ac.uk>
:Organization: University of Leeds
:Date: 10 September 2014
:Version: 0.1
:Status: Development
:Copyright: STRANDS default
:Notes: future extension to handle polygons, to do that use matplotlib.path.Path.contains_points
        although might want to have a read on the following also...
        http://matplotlib.1069221.n5.nabble.com/How-to-properly-use-path-Path-contains-point-td40718.html
"""

from __future__ import print_function, division
from qsrlib_qsrs.qsr_abstractclass import QSR_Abstractclass
from qsrlib_io.world_qsr_trace import *


class QSR_SG1(QSR_Abstractclass):
    """Make default QSRs and provide an example for others"""
    def __init__(self):
        self.qsr_type = "sg1"  # must be the same that goes in the QSR_Lib.__const_qsrs_available
        # qsrs 1-4 are called pairs, space, or type A and operate on pairs of objects
        # qsrs 5-6 are called singles, motion or type B and operate on individual objects
        self.all_possible_relations = ["1", "2", "3", "4", "5", "6"]
        self.meaningful_mapping = {"1": "disconnected", "2": "distancing", "3": "approaching", "4": "stationary",
                                   "5": "moving", "6": "stationary"}

    def custom_help(self):
        """Write your own help message function"""
        # TODO custom_help
        print("to be filled in later")

    def custom_checks(self, input_data):
        """Write your own custom checks on top of the default ones


        :return: error code, error message (integer, string), use 10 and above for error code as 1-9 are reserved by system
        """
        return 0, ""

    def make(self, *args, **kwargs):
        """Make the QSRs

        :param args: not used at the moment
        :param kwargs:
                        - input_data: World_Trace
        :return: World_QSR_Trace
        """
        input_data = kwargs["input_data"]
        include_missing_data = kwargs["include_missing_data"]
        ret = World_QSR_Trace(qsr_type=self.qsr_type)
        sorted_timestamps = input_data.get_sorted_timestamps()

        for i in range(1, len(sorted_timestamps)):
            t = sorted_timestamps[i]
            tp = sorted_timestamps[i-1]
            world_state = input_data.trace[t]
            # timestamp = world_state.timestamp # got to be same as t
            singles = world_state.objects.keys()
            pairs = self.__return_all_possible_combinations(singles)
            data = self.__return_2t_step_data(world_state=world_state,
                                              t=t, tp=tp,
                                              for_whom={"singles": singles, "pairs": pairs})


        # for t in input_data.get_sorted_timestamps():
        #     world_state = input_data.trace[t]
        #     timestamp = world_state.timestamp
        #     pairs = self.__return_all_possible_combinations(world_state.objects.keys())
        #     if pairs:
        #         for p in pairs:
        #             between = str(p[0]) + "," + str(p[1])
        #             bb1 = world_state.objects[p[0]].return_bounding_box_2d()
        #             bb2 = world_state.objects[p[1]].return_bounding_box_2d()
        #             qsr = QSR(timestamp=timestamp, between=between, qsr=self.__compute_qsr(bb1, bb2))
        #             ret.add_qsr(qsr, timestamp)
        #     else:
        #         if include_missing_data:
        #             ret.add_empty_world_qsr_state(timestamp)
        return ret

    def __return_2t_step_data(self, world_state, t, tp, for_whom):
        print(for_whom)
        return None

    # custom functions follow
    def __return_all_possible_combinations(self, objects_names):
        if len(objects_names) < 2:
            return []
        ret = []
        for i in objects_names:
            for j in objects_names:
                if i != j:
                    ret.append([i, j])
        return ret

    def __compute_qsr(self, bb1, bb2):
        count_occluded_points = 0
        for i in range(0, len(bb2), 2):
            if self.__is_point_in_rectangle([bb2[i], bb2[i+1]], bb1):
                count_occluded_points += 1
        results = {0: "dc", 1: "po", 2: "o"} # pythonic case
        ret = results[count_occluded_points]
        return ret

    def __is_point_in_rectangle(self, p, r, d=0.):
        return p[0] >= r[0]-d and p[0] <= r[2]+d and p[1] >= r[0]-d and p[1] <= r[3]+d
