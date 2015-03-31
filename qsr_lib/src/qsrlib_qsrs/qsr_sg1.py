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
import numpy as np
import sys


class QSR_SG1(QSR_Abstractclass):
    """Make default QSRs and provide an example for others"""

    def __init__(self):
        self.qsr_type = "sg1"  # must be the same that goes in the QSR_Lib.__const_qsrs_available
        # qsrs 1-4 are called pairs, space, or type A and operate on pairs of objects
        # qsrs 5-6 are called singles, motion or type B and operate on individual objects
        self.all_possible_relations = ["stationary", "moving",  # type A, on singles
                                       "same", "appoaching", "distancing",  # type B, on pairs
                                       "connected", "disconnected"]  # type C, on pairs
        # self.all_possible_relations = ["1", "2", "3", "4", "5", "6"]
        # self.meaningful_mapping = {"1": "disconnected", "2": "distancing", "3": "approaching", "4": "stationary",
        #                            "5": "moving", "6": "stationary"}

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
        world_qsr_trace = World_QSR_Trace(qsr_type=self.qsr_type)
        sorted_timestamps = input_data.get_sorted_timestamps()

        for i in range(1, len(sorted_timestamps)):
            t = sorted_timestamps[i]
            tp = sorted_timestamps[i - 1]
            world_state = input_data.trace[t]
            timestamp = world_state.timestamp # got to be same as t
            singles = world_state.objects.keys()
            pairs = self.__return_all_possible_combinations(singles)
            world_qsr_state = self.return_world_qsr_state_at_t(input_data=input_data, t=t, tp=tp,
                                                               for_whom={"singles": singles, "pairs": pairs})
            # print(type(world_qsr_state), world_qsr_state)
            world_qsr_trace.add_world_qsr_state(world_qsr_state)
            # qsr = self.return_qsr(input_data=input_data,
            #                                 t=t, tp=tp,
            #                                 for_whom={"singles": singles, "pairs": pairs})


        # for t in input_data.get_sorted_timestamps():
        # world_state = input_data.trace[t]
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
        return world_qsr_trace

    def find_single_in_nearest_past(self, s, input_data, t):
        sorted_ts = input_data.get_sorted_timestamps()
        for i in reversed(sorted_ts[:sorted_ts.index(t)]):
            world_state = input_data.trace[i]
            # try:
            #     world_state = input_data.trace[i]
            # except Exception, e:
            #     print(e, "What is going on here?", type(input_data))
            #     print(input_data.trace)
            #     sys.exit(1)
            if s in world_state.objects:
                return world_state, i
        return None, None

    def find_pair_in_nearest_past(self, p, input_data, t):
        sorted_ts = input_data.get_sorted_timestamps()
        for i in reversed(sorted_ts[:sorted_ts.index(t)]):
            world_state = input_data.trace[i]
            if p[0] in world_state.objects and p[1] in world_state.objects:
                return world_state, i
        return None, None

    # custom functions follow
    def return_world_qsr_state_at_t(self, input_data, t, tp, for_whom, history_traceback=True):
        world_qsr_state = World_QSR_State(timestamp=t)
        world_state_t = input_data.trace[t]
        world_state_tp = input_data.trace[tp]
        for s in for_whom["singles"]:
            try:
                data = (world_state_t.objects[s], world_state_tp.objects[s])
            except KeyError:
                if history_traceback:
                    world_state_tp_temp, tp_temp = self.find_single_in_nearest_past(s, input_data, t)
                    # print("a: tracing back in history")
                    # if world_state_tp_temp:
                    try:
                        data = (world_state_t.objects[s], world_state_tp_temp.objects[s])
                    # else:
                    except AttributeError:
                        # print("a: No history found")
                        continue
                else:
                    continue
            between = str(s)
            qsr_a = QSR(timestamp=t, between=between, qsr=self.return_type_a_qsr(data=data, error_tolerance=0.0), qsr_type="a")
            world_qsr_state.add_qsr(qsr=qsr_a)

        for p in for_whom["pairs"]:
            try:
                data = (world_state_t.objects[p[0]], world_state_t.objects[p[1]],
                        world_state_tp.objects[p[0]], world_state_tp.objects[p[1]])
            except KeyError:
                world_state_tp_temp, tp_temp = self.find_pair_in_nearest_past(p, input_data, t)
                # print("bc: tracing back in history")
                # if world_state_tp_temp:
                try:
                    data = (world_state_t.objects[p[0]], world_state_t.objects[p[1]],
                            world_state_tp_temp.objects[p[0]], world_state_tp_temp.objects[p[1]])
                # else:
                except AttributeError:
                    # print("bc: No history found")
                    continue
            between = str(p[0]) + "," + str(p[1])
            qsr_b_str = self.return_type_b_qsr(data=data, error_tolerance=0.0)
            data = (world_state_t.objects[p[0]], world_state_t.objects[p[1]])
            qsr_c_str = self.return_type_c_qsr(data=data, error_tolerance=0.0)
            qsr_bc_str = str(qsr_b_str) + "," + str(qsr_c_str)
            qsr_bc = QSR(timestamp=t, between=between, qsr=qsr_bc_str, qsr_type="bc")
            world_qsr_state.add_qsr(qsr=qsr_bc)

        return world_qsr_state

    # "stationary", "moving",  # type A, on singles
    def return_type_a_qsr(self, data, error_tolerance=0.0):
        vx = np.abs(data[0].x - data[1].x)
        vy = np.abs(data[0].y - data[1].y)
        # vz = np.abs(data[0].z - data[1].z) # TODO need to take care nan values

        if vx > error_tolerance or vy > error_tolerance:
            return "+"  # "moving"
        else:
            return "0"  # "stationary"

    # "same", "appoaching", "distancing",  # type B, on pairs
    def return_type_b_qsr(self, data, error_tolerance=0.0):
        # TODO need to sort out nan values, like .z
        d_now = np.sqrt(np.square(data[0].x - data[1].x) + np.square(data[0].y - data[1].y))
        d_prev = np.sqrt(np.square(data[2].x - data[3].x) + np.square(data[2].y - data[3].y))
        d = d_now - d_prev
        if d > error_tolerance:
            return "+"  # distancing"
        elif d < -error_tolerance:
            return "-"  # approaching"
        else:
            return "0"  # same"

    # "connected", "disconnected"]  # type C, on pairs
    def return_type_c_qsr(self, data, error_tolerance=0.0):
        bb1 = data[0].return_bounding_box_2d()
        bb2 = data[1].return_bounding_box_2d()
        count_occluded_points = 0
        for i in range(0, len(bb2), 2):
            if self.__is_point_in_rectangle([bb2[i], bb2[i + 1]], bb1):
                count_occluded_points += 1
        if count_occluded_points == 0:
            return "0"  # "disconnected"
        else:
            return "+"  # "connected"

    def __is_point_in_rectangle(self, p, r, d=0.):
        return p[0] >= r[0] - d and p[0] <= r[2] + d and p[1] >= r[0] - d and p[1] <= r[3] + d

    def __return_all_possible_combinations(self, objects_names):
        if len(objects_names) < 2:
            return []
        ret = []
        for i in objects_names:
            for j in objects_names:
                if i != j:
                    ret.append([i, j])
        return ret
