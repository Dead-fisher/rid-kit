from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.run_exploration import RunExplore



with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = RunExplore()
op_out = op.execute(OPIO({
    "task_path": Path("000"),
    "md_config": jdata["ExploreMDConfig"]
}))

print(op_out)