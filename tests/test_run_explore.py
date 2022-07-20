import os
import numpy as np
import unittest
from pathlib import Path
from mock import mock, patch, call
from dflow.python import (
    OP,
    OPIO,
    OPIOSign,
    Parameter
    )
from context import rid
from rid.op.run_exploration import RunExplore
from rid.utils import load_txt, save_txt, set_directory
from pathlib import Path
import shutil
from rid.constants import (
        explore_task_pattern, 
        gmx_conf_name,
        gmx_top_name,
        gmx_mdp_name, 
        plumed_input_name,
        plumed_output_name
    )
import rid.utils

class Test_MockedRunExplore(unittest.TestCase):
    def setUp(self):
        self.taskname = "000"
    
    def tearDown(self):
        ii=Path(self.taskname)
        shutil.rmtree(ii)
    
    @patch('rid.op.run_exploration.run_command')
    def test(self, mocked_run):
        mocked_run.return_value = 0, 0, 1
        op = RunExplore()
        task_path = Path(self.taskname)
        gmx_config = {"nsteps": 50, "output_freq": 1, "temperature": 300, 
                      "dt": 0.002, "output_mode": "both", "ntmpi": 1, "nt": 8, "max_warning": 0}
        op_in = OPIO(
            {
                "task_path": task_path,
                "gmx_config": gmx_config,
                "models": []
            }
            )
        op_out = op.execute(op_in)
        self.assertTrue(op_out["plm_out"])