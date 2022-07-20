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


from pathlib import Path
from typing import List
from context import rid
from rid.superop.exploration import Exploration
from rid.op.prep_exploration import PrepExplore
from rid.op.run_exploration import RunExplore
from rid.superop.label import Label
from rid.op.prep_label import PrepLabel
from rid.op.run_label import RunLabel
from rid.op.calc_mf import CalcMF
from rid.superop.selector import Selector
from rid.op.prep_select import PrepSelect
from rid.op.run_select import RunSelect
from rid.superop.data import DataGenerator
from rid.op.prep_data import CollectData, MergeData
from rid.superop.blocks import IterBlock, InitBlock
from rid.op.run_train import TrainModel
from rid.op.adjust_trust_level import AdjustTrustLevel


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

label_op = Label(
    "label",
    PrepLabel,
    RunLabel,
    CalcMF,
    prep_config,
    run_config)

select_op = Selector(
    "select",
    PrepSelect,
    RunSelect,
    prep_config,
    run_config)

data_op = DataGenerator(
    "gen-data",
    CollectData,
    MergeData,
    run_config)

init_block_op = InitBlock(
    "init-block",
    exploration_op,
    select_op,
    label_op,
    data_op,
    TrainModel,
    run_config,
)

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
    upload_python_package="/mnt/vepfs/jiahao/rid-kit/rid")