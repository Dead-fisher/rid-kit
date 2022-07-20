from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )
from context import rid
import json
from pathlib import Path
from rid.op.calc_mf import CalcMF

with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = CalcMF()
op_out = op.execute(OPIO({
    "plm_out": Path("001/plm.out"),
    "kappas": jdata["LabelMDConfig"]["kappas"],
    "at": Path("cv_init_57.out"),
    "tail": 0.9,
    "angular_mask": [1, 1],
}))

print(op_out)
