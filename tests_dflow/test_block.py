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
from rid.superop.blocks import FirstRunBlock
from rid.op.run_train import TrainModel

from prep_ops_for_test import exploration_op, label_op, select_op, data_op


run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}

block_op = FirstRunBlock(
    "first-run",
    exploration_op,
    select_op,
    label_op,
    data_op,
    TrainModel,
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

block_1 = Step("first-run",
        block_op,
        artifacts={
            # "models": None,
            "topology": top,
            "confs": confs
        },
        parameters={
            "block_tag": "iter-000000",
            "walker_tags": ["000", "001"],
            "model_tags": ["000", "001", "002"],
            "exploration_gmx_config": jdata["ExploreMDConfig"],
            "cv_config": jdata["CV"],
            "trust_lvl_1" : [0.02, 0.02],
            "trust_lvl_2": [0.03, 0.03],
            "cluster_threshold": [0.1, 0.1],
            "angular_mask": [1, 1],
            "weights": [1, 1],
            "numb_cluster_upper": 5,
            "numb_cluster_lower": 3,
            "max_selection": 5,
            "dt": jdata["ExploreMDConfig"]["dt"],
            "slice_mode": "gmx",
            "label_gmx_config": jdata["LabelMDConfig"],
            "kappas": jdata["LabelMDConfig"]["kappas"],
            "train_config": jdata["Train"]
            }
    )
wf = Workflow("block")
wf.add(block_1)
wf.submit()