import os
import numpy as np
import unittest
from pathlib import Path
from dflow.python import (
    OP,
    OPIO,
    OPIOSign,
    Parameter
    )
from context import rid
from rid.utils import load_txt, save_txt, set_directory
from pathlib import Path
import shutil
from rid.constants import (
    plumed_output_name,
    gmx_mdrun_log,
    trr_name,
    gmx_conf_out
)

from rid.constants import sel_gro_name, cv_init_label, model_devi_name, model_devi_precision, sel_ndx_name

from rid.op.run_exploration import RunExplore
from rid.op.run_label import RunLabel
from rid.op.run_select import RunSelect

class MockedRunExplore(RunExplore):
    @OP.exec_sign_check
    def execute(
            self,
            ip : OPIO,
    ) -> OPIO:
        task_path = ip["task_path"]
        task_path.mkdir(exist_ok=True, parents=True)
        
        plm_path = task_path/plumed_output_name
        plm_path.write_text("mocked plumed file")
        mdlog_path = task_path/gmx_mdrun_log
        mdlog_path.write_text("mocked md log file")
        traj_path = task_path/trr_name
        traj_path.write_text("mocked traj file")
        conf_path = task_path/gmx_conf_out
        conf_path.write_text("mocked conf file")
        
        op_out = OPIO(
            {
                "plm_out": plm_path,
                "md_log": mdlog_path,
                "trajectory": traj_path,
                "conf_out": conf_path
            }
        )
        
        return op_out

class MockedRunSelect(RunSelect):
    @OP.exec_sign_check
    def execute(
            self,
            ip : OPIO,
    ) -> OPIO:
        task_path = ip["task_name"]
        task_path = Path(task_path)
        task_path.mkdir(exist_ok=True, parents=True)
        
        cls_sel_idx = load_txt(ip["culster_selection_index"], dtype=int)
        cls_sel_data = load_txt(ip["culster_selection_data"], dtype=float)
        
        with set_directory(task_path):
            _selected_idx = np.array([ii for ii in range(len(cls_sel_idx))], dtype=int)
            sel_idx = cls_sel_idx[_selected_idx]
            save_txt(sel_ndx_name, sel_idx, fmt="%d")
            sel_data = cls_sel_data[_selected_idx]
            gro_list = []
            cv_init_list = []
            for ii, sel in enumerate(sel_idx):
                gro_list.append(task_path.joinpath(sel_gro_name.format(idx=sel)))
                save_txt(cv_init_label.format(idx=sel), sel_data[ii])
                cv_init_list.append(task_path.joinpath(cv_init_label.format(idx=sel)))

        op_out = OPIO(
            {
               "selected_confs": gro_list,
               "selected_cv_init": cv_init_list,
               "model_devi": task_path.joinpath("cls_"+model_devi_name),
               "selected_indices": task_path.joinpath(sel_ndx_name)
            }
        )
        
        return op_out
    
class MockedRunLabel(RunLabel):
    @OP.exec_sign_check
    def execute(
            self,
            ip : OPIO,
    ) -> OPIO:
        task_path = ip["task_path"]
        task_path.mkdir(exist_ok=True,parents=True)   
        plm_path = task_path/plumed_output_name
        plm_path.write_text("mocked plumed file")
        mdlog_path = task_path/gmx_mdrun_log
        mdlog_path.write_text("mocked md log file") 
        
        op_out = OPIO(
            {
                "plm_out": ip["task_path"].joinpath(plumed_output_name),
                "md_log": ip["task_path"].joinpath(gmx_mdrun_log)
            }
        )
        return op_out
    