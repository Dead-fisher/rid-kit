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
from rid.superop.data import DataGenerator
from rid.op.prep_data import CollectData, MergeData


run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}

forces = upload_artifact(
    [
        "/mnt/vepfs/yanze/dflow_project/rid-kit/tests/002/forces.out",
        "/mnt/vepfs/yanze/dflow_project/rid-kit/tests/001/forces.out"
    ],
    archive=None
)
centers = upload_artifact(
    [
        "/mnt/vepfs/yanze/dflow_project/rid-kit/tests/002/cv_init_57.out",
        "/mnt/vepfs/yanze/dflow_project/rid-kit/tests/001/cv_init_57.out"
    ],
    archive=None
)

data_op = DataGenerator(
    "gen-data",
    CollectData,
    MergeData,
    run_config)

explore = Step(
        'GenData',
        template=data_op,
        parameters={"block_tag" : 'iter-000000'},
        artifacts={
            "forces": forces,
            "centers": centers
        },
        key = '000_gen_data',
    )

wf = Workflow("data")
wf.add(explore)
wf.submit()