from dflow import (
    InputParameter,
    OutputParameter,
    Inputs,
    InputArtifact,
    Outputs,
    OutputArtifact,
    Workflow,
    Step,
    Steps,
    upload_artifact,
    download_artifact,
    argo_range,
    argo_len,
    argo_sequence,
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
from copy import deepcopy
from context import rid
from rid.op.run_train import TrainModel
from rid.utils import init_executor




run_config = {
    "template_config" : {
        "image": "dp-rid-dflow:tf262-pytorch1.11.0-cuda11.3", 
        "image_pull_policy" : "IfNotPresent"
    }, 
    "executor" : None
}


train_config = deepcopy(run_config)
train_template_config = train_config.pop('template_config')
train_executor = init_executor(train_config.pop('executor'))

with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

data = upload_artifact("test_train/data.raw", archive=None)

train = Step(
        # '{}-Train'.format(block_steps.inputs.parameters['block_tag']),
        "train",
        template=PythonOPTemplate(
            TrainModel,
            slices=Slices(
                input_parameter=["model_tag"],
                output_artifact=["model"]),
            **train_template_config,
        ),
        parameters={
            "model_tag": ["000", "001", "002"],
            "angular_mask": [1, 1],
            "train_config": jdata["Train"],
        },
        artifacts={
            "data": data,
        },
        executor = train_executor,
        with_param=argo_range(3),
        key = '{}_train'.format("iter-000"),
        **train_config,
    )

wf = Workflow("train")
wf.add(train)
wf.submit()