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
"""
The Variational Quantum Eigensolver algorithm.
See https://arxiv.org/abs/1304.3061
"""

import time
import logging

import numpy as np
from qiskit import QuantumCircuit, ClassicalRegister

from qiskit_aqua import QuantumAlgorithm, AlgorithmError
from qiskit_aqua import get_optimizer_instance, get_variational_form_instance, get_initial_state_instance
from .vqe import VQE
logger = logging.getLogger(__name__)


class VQETK(VQE):
    """
    The Variational Quantum Eigensolver algorithm.
    See https://arxiv.org/abs/1304.3061
    """
    VQE_CONFIGURATION = VQE.VQE_CONFIGURATION.copy()
    VQE_CONFIGURATION['name'] = 'VQETK'
    VQE_CONFIGURATION['description'] = 'VQETK Algorithm'

    # VQE_CONFIGURATION = {
    #     'name': 'VQETK',
    #     'description': 'VQETK Algorithm',
    #     'input_schema': {
    #         '$schema': 'http://json-schema.org/schema#',
    #         'id': 'vqe_schema',
    #         'type': 'object',
    #         'properties': {
    #             'operator_mode': {
    #                 'type': 'string',
    #                 'default': 'matrix',
    #                 'oneOf': [
    #                     {'enum': ['matrix', 'paulis', 'grouped_paulis']}
    #                 ]
    #             },
    #             'initial_point': {
    #                 'type': ['array', 'null'],
    #                 "items": {
    #                     "type": "number"
    #                 },
    #                 'default': None
    #             }
    #         },
    #         'additionalProperties': False
    #     },
    #     'problems': ['energy', 'ising'],
    #     'depends': ['optimizer', 'variational_form', 'initial_state'],
    #     'defaults': {
    #         'optimizer': {
    #             'name': 'L_BFGS_B'
    #         },
    #         'variational_form': {
    #             'name': 'RYRZ'
    #         },
    #         'initial_state': {
    #             'name': 'ZERO'
    #         }
    #     }
    # }

    