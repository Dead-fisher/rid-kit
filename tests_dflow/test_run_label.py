from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.run_label import RunLabel



with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = RunLabel()
op_out = op.execute(OPIO({
   "task_path": Path("001"),
   "md_config": jdata["LabelMDConfig"]
}))

print(op_out)