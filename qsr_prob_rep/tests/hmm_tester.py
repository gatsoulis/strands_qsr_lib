#!/usr/bin/env python
PKG = 'qsr_prob_rep'
NAME = 'hmm_tester'

import rospy
import sys
import unittest
from roslib.packages import find_resource
from qsrrep_ros.ros_client import ROSClient
from qsrrep_lib.rep_io import HMMRepRequestCreate, HMMRepRequestSample, HMMRepRequestLogLikelihood
import json
import hashlib


class TestHMM(unittest.TestCase):
    QTCB_SAMPLE_TEST_HMM  = find_resource(PKG, 'qtcb_sample_test.hmm')[0]
    QTCC_SAMPLE_TEST_HMM  = find_resource(PKG, 'qtcc_sample_test.hmm')[0]
    QTCBC_SAMPLE_TEST_HMM = find_resource(PKG, 'qtcbc_sample_test.hmm')[0]
    QTCB_PASSBY_LEFT_HMM  = find_resource(PKG, 'qtcb_passby_left.hmm')[0]
    QTCC_PASSBY_LEFT_HMM  = find_resource(PKG, 'qtcc_passby_left.hmm')[0]
    QTCBC_PASSBY_LEFT_HMM = find_resource(PKG, 'qtcbc_passby_left.hmm')[0]
    RCC3_TEST_HMM         = find_resource(PKG, 'rcc3_test.hmm')[0]
    QTCB_QSR              = find_resource(PKG, 'qtcb.qsr')[0]
    QTCC_QSR              = find_resource(PKG, 'qtcc.qsr')[0]
    QTCBC_QSR             = find_resource(PKG, 'qtcbc.qsr')[0]
    RCC3_QSR              = find_resource(PKG, 'rcc3.qsr')[0]

    correct_samples = {
        "qtcb": [[u'--', u'0-', u'+-', u'+0', u'++']],
        "qtcc": [[u'--+-', u'--0-', u'----', u'0---', u'+---', u'+0--', u'++--', u'---']],
        "qtcbc": [[u'--', u'----', u'0---', u'+---', u'+0--', u'++--', u'++']]
    }

    correct_hashsum = {
        "qtcb": "3fb65b50d0f7631a300132e8bca9ca13",
        "qtcc": "dbf1529cb0b0c90aaebbe7eafe0e9b05",
        "qtcbc": "0a3acf7b48c4c1155931442c86317ce4",
        "rcc3": "6d5bcc6c44d9b1120c738efa1994a40a"
    }

    correct_loglikelihoods ={
        "qtcb": -2.16887,
        "qtcc": -6.07188,
        "qtcbc": -2.23475,
        "rcc3": -4.15914
    }


    def __init__(self, *args):
        super(TestHMM, self).__init__(*args)

        rospy.init_node(NAME)

        self.r = ROSClient()

    def _create_hmm(self, qsr_file, qsr_type):
        with open(qsr_file, 'r') as f: qsr_seq = json.load(f)
        _, d = self.r.call_service(
            HMMRepRequestCreate(
                qsr_seq=qsr_seq,
                qsr_type=qsr_type
            )
        )
        return d

    def _create_sample(self, hmm_file, qsr_type):
        with open(hmm_file, 'r') as f: hmm = f.read()
        _, s = self.r.call_service(
            HMMRepRequestSample(
                qsr_type=qsr_type,
                xml=hmm,
                max_length=10,
                num_samples=1
            )
        )
        return s

    def _calculate_loglikelihood(self, hmm_file, qsr_file, qsr_type):
        with open(qsr_file, 'r') as f: qsr_seq = json.load(f)
        with open(hmm_file, 'r') as f: hmm = f.read()
        q, l = self.r.call_service(
            HMMRepRequestLogLikelihood(
                qsr_type=qsr_type,
                xml=hmm,
                qsr_seq=qsr_seq
            )
        )
        return round(l, 5)

    def _to_strings(self, array):
        return [x.values()[0] for x in array]

    def test_qtcb_create(self):
        res = self._create_hmm(self.QTCB_QSR, 'qtcb')
        self.assertEqual(hashlib.md5(res).hexdigest(), self.correct_hashsum["qtcb"])

    def test_qtcb_sample(self):
        res = self._create_sample(self.QTCB_SAMPLE_TEST_HMM, 'qtcb')
        self.assertEqual(res, self.correct_samples["qtcb"])

    def test_qtcb_loglikelihood(self):
        res = self._calculate_loglikelihood(self.QTCB_PASSBY_LEFT_HMM, self.QTCB_QSR, 'qtcb')
        self.assertEqual(res, self.correct_loglikelihoods["qtcb"])

    def test_qtcc_create(self):
        res = self._create_hmm(self.QTCC_QSR, 'qtcc')
        self.assertEqual(hashlib.md5(res).hexdigest(), self.correct_hashsum["qtcc"])

    def test_qtcc_sample(self):
        res = self._create_sample(self.QTCC_SAMPLE_TEST_HMM, 'qtcc')
        self.assertEqual(res, self.correct_samples["qtcc"])

    def test_qtcc_loglikelihood(self):
        res = self._calculate_loglikelihood(self.QTCC_PASSBY_LEFT_HMM, self.QTCC_QSR, 'qtcc')
        self.assertEqual(res, self.correct_loglikelihoods["qtcc"])

    def test_qtcbc_create(self):
        res = self._create_hmm(self.QTCBC_QSR, 'qtcbc')
        self.assertEqual(hashlib.md5(res).hexdigest(), self.correct_hashsum["qtcbc"])

    def test_qtcbc_sample(self):
        res = self._create_sample(self.QTCBC_SAMPLE_TEST_HMM, 'qtcbc')
        self.assertEqual(res, self.correct_samples["qtcbc"])

    def test_qtcbc_loglikelihood(self):
        res = self._calculate_loglikelihood(self.QTCBC_PASSBY_LEFT_HMM, self.QTCBC_QSR, 'qtcbc')
        self.assertEqual(res, self.correct_loglikelihoods["qtcbc"])

    def test_rcc3_create(self):
        res = self._create_hmm(self.RCC3_QSR, 'rcc3')
        self.assertEqual(hashlib.md5(res).hexdigest(), self.correct_hashsum["rcc3"])

    def test_rcc3_sample(self):
        res = self._create_sample(self.RCC3_TEST_HMM, 'rcc3')
        self.assertTrue(type(res) == list and len(res) > 0)

    def test_rcc3_loglikelihood(self):
        res = self._calculate_loglikelihood(self.RCC3_TEST_HMM, self.RCC3_QSR, 'rcc3')
        self.assertEqual(res, self.correct_loglikelihoods["rcc3"])


if __name__ == '__main__':
    import rostest
    rostest.rosrun(PKG, NAME, TestHMM, sys.argv)
