from dflow import (
    Workflow,
    Step,
    upload_artifact
)
from dflow.python import (
    PythonOPTemplate,
    OP,
    OPIO,
    OPIOSign,
    Artifact,
    Slices
)
from dflow.python import upload_packages
upload_packages.append("/mnt/vepfs/yanze/dflow_project/rid-kit/rid")

from pathlib import Path
from typing import List
from context import rid
from rid.superop.selector import Selector
from rid.op.prep_select import PrepSelect
from rid.op.run_select import RunSelect


prep_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}
run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}

select_op = Selector(
    "label",
    PrepSelect,
    RunSelect,
    prep_config,
    run_config)

models = upload_artifact([
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.000.pb"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.001.pb"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.002.pb")], 
            archive=None
        )
conf = upload_artifact(
        [Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/000/conf.gro"),
        Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/001/conf.gro")],
        archive=None
    )
xtc_trajs = upload_artifact(
        [
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/000/traj_comp.xtc"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/001/traj_comp.xtc")
        ],
        archive=None
    )
plm_outs = upload_artifact(
        [
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/000/plm.out"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/001/plm.out")
        ],
        archive=None
    )

select1 = Step("select",
        select_op,
        artifacts={
            "models": models,
            "plm_out": plm_outs,
            "xtc_traj": xtc_trajs,
            "topology": conf
        },
        parameters={
            "trust_lvl_1" : [0.20, 0.2],
            "trust_lvl_2": [0.30, 0.3],
            "cluster_threshold": [0.1, 0.1],
            "angular_mask": [1, 1],
            "weights": [1, 1],
            "numb_cluster_upper": 5,
            "numb_cluster_lower": 3,
            "max_selection": 5,
            "dt": 0.02,
            "slice_mode": "gmx",
            "if_make_threshold": False,
            "task_names": ["000", "001"],
            "block_tag": "iter-00001",
        }
    )

wf = Workflow("select")
wf.add(select1)
wf.submit()