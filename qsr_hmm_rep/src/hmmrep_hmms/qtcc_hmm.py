#!/usr/bin/env python

from hmmrep_hmms.qtc_hmm_abstractclass import QTCHMMAbstractclass
import numpy as np


class QTCCHMM(QTCHMMAbstractclass):

    def __init__(self):
        super(QTCCHMM, self).__init__()
        self.num_possible_states = 83

    def _create_transition_matrix(self, size, **kwargs):
        """Creates a Conditional Neighbourhood Diagram as a basis for the HMM"""

        qtc = []

        for i in xrange(1, 4):
            for j in xrange(1, 4):
                for k in xrange(1, 4):
                    for l in xrange(1, 4):
                        qtc.append([i-2, j-2, k-2, l-2])

        return super(QTCCHMM, self)._create_transition_matrix(size=size, qtc=qtc)

    def _symbol_to_qsr(self, symbols):
        ret = []
        for s in symbols:
            qtc = []
            q = 3**np.array(range(3,-1,-1))
            for c in s[1:-1]:

                rc = np.array([c-1])
                f = np.array([np.floor(rc[0]/q[0])])
                r = np.fmod(rc[0],q[0])

                for i in range(1, len(q)):
                    rc = np.append(rc, rc[i-1] - f[i-1] * q[i-1])
                    f = np.append(f, np.floor(rc[i]/q[i]))
                    r = np.append(r, np.fmod(rc[i],q[i]))

                f -= 1
                qtc.append(f.tolist())

            ret.append(self._qtc_num_to_str(qtc))

        return ret