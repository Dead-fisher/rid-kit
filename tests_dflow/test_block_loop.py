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
upload_packages.append("/mnt/vepfs/jiahao/rid-kit/rid")

from context import rid
from rid.op.run_train import TrainModel
from rid.flow.loop import ReinforcedDynamics
from prep_ops_for_test import exploration_op, label_op, select_op, data_op, init_block_op, block_op

run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}

rid_op = ReinforcedDynamics(
    "ReinforcedDynamics",
    init_block_op,
    block_op,
    run_config,
    upload_python_package = "/mnt/vepfs/jiahao/rid-kit/rid"
)


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
rid_config = upload_artifact("JSON/rid.json", archive=None)

rid_steps = Step("rid-run",
        rid_op,
        artifacts={
            "topology": top,
            "confs": confs,
            "rid_config": rid_config
        },
        parameters={
            }
    )
wf = Workflow("rid-test")
wf.add(rid_steps)
wf.submit()