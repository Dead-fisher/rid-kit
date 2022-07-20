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

import json
from pathlib import Path
from typing import List

from dflow.python import upload_packages
upload_packages.append("/mnt/vepfs/yanze/dflow_project/rid-kit/rid")

from context import rid
from rid.superop.blocks import IterBlock
from rid.op.run_train import TrainModel
from rid.op.adjust_trust_level import AdjustTrustLevel
from prep_ops_for_test import exploration_op, label_op, select_op, data_op


run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}

block_op = IterBlock(
    "second-run",
    exploration_op,
    select_op,
    label_op,
    data_op,
    AdjustTrustLevel,
    TrainModel,
    run_config,
    run_config,
    upload_python_package="/mnt/vepfs/yanze/dflow_project/rid-kit/rid")

with open("JSON/rid.json", "r") as rj:
    jdata = json.load(rj)

models = upload_artifact([
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.000.pb"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.001.pb"),
            Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/graph.002.pb")], archive=None)

top = upload_artifact("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/topol.top", archive=None)
confs = upload_artifact(
            [
                Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_ala_drop/iter.000000/00.enhcMD/001/conf.gro"),
                Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_ala_drop/iter.000000/00.enhcMD/000/conf.gro")
            ],
        archive=None
    )
     
data_old = upload_artifact("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/data.old", archive=None)

block_1 = Step("second-run",
        block_op,
        artifacts={
            "models": models,
            "topology": top,
            "confs": confs,
            "data_old": data_old
        },
        parameters={
            "block_tag": "iter-000001",
            "walker_tags": ["000", "001"],
            "model_tags": ["000", "001", "002"],
            "exploration_gmx_config": jdata["ExploreMDConfig"],
            "cv_config": jdata["CV"],
            "trust_lvl_1" : [0.020, 0.030],
            "trust_lvl_2": [0.030, 0.045],
            "init_trust_lvl_1": [0.020, 0.020],
            "init_trust_lvl_2": [0.030, 0.030],
            "cluster_threshold": [ 0.05, 0.05 ],
            "angular_mask": [1, 1],
            "weights": [1, 1],
            "max_selection": 5,
            "numb_cluster_threshold": 3,
            "dt": jdata["ExploreMDConfig"]["dt"],
            "slice_mode": "gmx",
            "label_gmx_config": jdata["LabelMDConfig"],
            "kappas": jdata["LabelMDConfig"]["kappas"],
            "train_config": jdata["Train"]
            }
    )
wf = Workflow("block-2nd")
wf.add(block_1)
wf.submit()