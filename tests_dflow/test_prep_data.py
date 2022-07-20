from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )
from context import rid
import json
from pathlib import Path
from rid.op.prep_data import CollectData, MergeData

with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = CollectData()
op_out = op.execute(OPIO({
    "forces": [Path("001/forces.out"), Path("002/forces.out")],
    "centers": [Path("001/cv_init_57.out"), Path("002/cv_init_57.out")]
}))

print(op_out)

op = MergeData()
op_out = op.execute(OPIO({
    "data_old": Path("data.old"),
    "data_new": Path("data.new")
}))

print(op_out)
