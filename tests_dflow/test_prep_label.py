from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.prep_label import PrepLabel
import numpy as np


with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

ats = np.loadtxt("test_label/cv_init_57.out")

op = PrepLabel()
op_out = op.execute(OPIO({
    "topology": Path("test_label/topol.top"),
    "conf": Path("test_label/conf_57.gro"),
    "gmx_config": jdata["LabelMDConfig"],
    "cv_config": jdata["CV"],
    "task_id": 1,
    "kappas": jdata["LabelMDConfig"]["kappas"],
    "at": Path("test_label/cv_init_57.out")
}))

print(op_out)