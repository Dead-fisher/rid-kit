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
from rid.superop.label import Label
from rid.op.prep_label import PrepLabel
from rid.op.run_label import RunLabel
from rid.op.calc_mf import CalcMF


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

label_op = Label(
    "label",
    PrepLabel,
    RunLabel,
    CalcMF,
    prep_config,
    run_config)


top = upload_artifact("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_exploration/topol.top", archive=None)
confs = upload_artifact(
            [
                Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_label/conf_57.gro"),
                Path("/mnt/vepfs/yanze/dflow_project/rid-kit/tests/test_label/conf_67.gro")
            ],
        archive=None
    )
 

label = Step("label",
        label_op,
        artifacts={
            "topology": top,
            "confs": confs,
            "at": ats
        },
        parameters={
            "task_names" : ["000", "001"],
            "angular_mask": [1, 1],
            "kappas": [500, 500],
            "gmx_config" : {
                "nsteps": 1000,
                "output_freq": 10,
                "temperature": 300,
                "dt": 0.002,
                "output_mode": "both",
                "ntmpi": 1,
                "nt": 8,
                "max_warning": 0
            },
            "cv_config" : {
                "mode": "torsion",
                "selected_resid": [1,2],
                "cv_file":""
            }
        }
    )

wf = Workflow("label")
wf.add(label)
wf.submit()