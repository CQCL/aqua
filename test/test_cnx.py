# -*- coding: utf-8 -*-

# Copyright 2018 IBM.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================

import unittest
import numpy as np
from itertools import combinations, chain
from parameterized import parameterized
import qiskit
from qiskit import QuantumCircuit, QuantumRegister
from qiskit import execute as q_execute
from test.common import QiskitAquaTestCase


class TestCNX(QiskitAquaTestCase):
    @parameterized.expand([
        [1, 1],
        [2, 1],
        [3, 1],
        [4, 2],
    ])
    def test_cnx(self, num_controls, num_ancillae):
        c = QuantumRegister(num_controls, name='c')
        o = QuantumRegister(1, name='o')
        a = QuantumRegister(num_ancillae, name='a')
        allsubsets = list(chain(
            *[combinations(range(num_controls), ni) for ni in range(num_controls + 1)]))
        for subset in allsubsets:
            qc = QuantumCircuit(o, c, a)
            for idx in subset:
                qc.x(c[idx])
            qc.cnx(
                [c[i] for i in range(num_controls)],
                [a[i] for i in range(num_ancillae)],
                o[0]
            )
            for idx in subset:
                qc.x(c[idx])

            vec = np.asarray(q_execute(qc, qiskit.Aer.get_backend(
                'statevector_simulator')).result().get_statevector(qc, decimals=16))
            vec_o = [0, 1] if len(subset) == num_controls else [1, 0]
            np.testing.assert_almost_equal(
                vec,
                np.array(vec_o + [0] *
                         (2 ** (num_controls + num_ancillae + 1) - 2))
            )


if __name__ == '__main__':
    unittest.main()
