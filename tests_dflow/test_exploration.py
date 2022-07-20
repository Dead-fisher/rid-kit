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
from rid.superop.exploration import Exploration
from rid.op.prep_exploration import PrepExplore
from rid.op.run_exploration import RunExplore


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

exploration_op = Exploration(
    "exploration",
    PrepExplore,
    RunExplore,
    prep_config,
    run_config)

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

explore = Step("explore",
        exploration_op,
        artifacts={
            # "models": models,
            "topology": top,
            "confs": confs
        },
        parameters={
            "trust_lvl_1" : 2.0,
            "trust_lvl_2": 3.0,
            "task_names" : ["000", "001"],
            "block_tag" : "iter-000000",
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
wf = Workflow("exploration")
wf.add(explore)
wf.submit()