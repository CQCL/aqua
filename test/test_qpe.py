# -*- coding: utf-8 -*-

# Copyright 2018 IBM RESEARCH. All Rights Reserved.
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
from parameterized import parameterized
from scipy.linalg import expm
from scipy import sparse
from qiskit import Aer
from qiskit.transpiler import PassManager

from test.common import QiskitAquaTestCase
from qiskit_aqua import Operator, QuantumInstance
from qiskit_aqua.utils import decimal_to_binary
from qiskit_aqua.algorithms.classical import ExactEigensolver
from qiskit_aqua.algorithms.components.iqfts import Standard
from qiskit_aqua.algorithms.components.initial_states import Custom
from qiskit_aqua.algorithms.single_sample import QPE

X = np.array([[0, 1], [1, 0]])
Y = np.array([[0, -1j], [1j, 0]])
Z = np.array([[1, 0], [0, -1]])
I = np.array([[1, 0], [0, 1]])
h1 = X + Y + Z + I
qubitOp_simple = Operator(matrix=h1)


pauli_dict = {
    'paulis': [
        {"coeff": {"imag": 0.0, "real": -1.052373245772859}, "label": "II"},
        {"coeff": {"imag": 0.0, "real": 0.39793742484318045}, "label": "IZ"},
        {"coeff": {"imag": 0.0, "real": -0.39793742484318045}, "label": "ZI"},
        {"coeff": {"imag": 0.0, "real": -0.01128010425623538}, "label": "ZZ"},
        {"coeff": {"imag": 0.0, "real": 0.18093119978423156}, "label": "XX"}
    ]
}
qubitOp_h2_with_2_qubit_reduction = Operator.load_from_dict(pauli_dict)


class TestQPE(QiskitAquaTestCase):
    """QPE tests."""

    @parameterized.expand([
        [qubitOp_simple],
        [qubitOp_h2_with_2_qubit_reduction],
    ])
    def test_qpe(self, qubitOp):
        self.algorithm = 'QPE'
        self.log.debug('Testing QPE')

        self.qubitOp = qubitOp

        exact_eigensolver = ExactEigensolver(self.qubitOp, k=1)
        results = exact_eigensolver.run()

        w = results['eigvals']
        v = results['eigvecs']

        self.qubitOp.to_matrix()
        np.testing.assert_almost_equal(
            self.qubitOp.matrix @ v[0],
            w[0] * v[0]
        )
        np.testing.assert_almost_equal(
            expm(-1.j * sparse.csc_matrix(self.qubitOp.matrix)) @ v[0],
            np.exp(-1.j * w[0]) * v[0]
        )

        self.ref_eigenval = w[0]
        self.ref_eigenvec = v[0]
        self.log.debug('The exact eigenvalue is:       {}'.format(self.ref_eigenval))
        self.log.debug('The corresponding eigenvector: {}'.format(self.ref_eigenvec))

        num_time_slices = 50
        n_ancillae = 9
        state_in = Custom(self.qubitOp.num_qubits, state_vector=self.ref_eigenvec)
        iqft = Standard(n_ancillae)

        qpe = QPE(self.qubitOp, state_in, iqft, num_time_slices, n_ancillae,
                  paulis_grouping='random', expansion_mode='suzuki', expansion_order=2)

        backend = Aer.get_backend('qasm_simulator')
        quantum_instance = QuantumInstance(backend, shots=100, pass_manager=PassManager())

        # run qpe
        result = qpe.run(quantum_instance)
        # self.log.debug('transformed operator paulis:\n{}'.format(self.qubitOp.print_operators('paulis')))

        # report result
        self.log.debug('measurement results:          {}'.format(result['measurements']))
        self.log.debug('top result str label:         {}'.format(result['top_measurement_label']))
        self.log.debug('top result in decimal:        {}'.format(result['top_measurement_decimal']))
        self.log.debug('stretch:                      {}'.format(result['stretch']))
        self.log.debug('translation:                  {}'.format(result['translation']))
        self.log.debug('final eigenvalue from QPE:    {}'.format(result['energy']))
        self.log.debug('reference eigenvalue:         {}'.format(self.ref_eigenval))
        self.log.debug('ref eigenvalue (transformed): {}'.format(
            (self.ref_eigenval + result['translation']) * result['stretch'])
        )
        self.log.debug('reference binary str label:   {}'.format(decimal_to_binary(
            (self.ref_eigenval.real + result['translation']) * result['stretch'],
            max_num_digits=n_ancillae + 3,
            fractional_part_only=True
        )))

        np.testing.assert_approx_equal(self.ref_eigenval.real, result['energy'], significant=2)


if __name__ == '__main__':
    unittest.main()
