from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.prep_select import PrepSelect



with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = PrepSelect()
op_out = op.execute(OPIO({
    "plm_out": Path("test_select/plm.out"),
    "cluster_threshold":1.3,
    "angular_mask":[1,1],
    "weights" : [1,1],
    "numb_cluster_upper" : 5,
    "numb_cluster_lower" : 3,
    "max_selection" : 5
}))

print(op_out)