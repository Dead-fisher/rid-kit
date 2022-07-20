from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.run_select import RunSelect



with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = RunSelect()
op_out = op.execute(OPIO({
    "culster_selection_index": Path("test_select/cls_sel.ndx"),
    "culster_selection_data": Path("test_select/cls_sel.out"),
    "model_list": [
        Path("test_exploration/graph.000.pb"),
        Path("test_exploration/graph.001.pb"),
        Path("test_exploration/graph.002.pb")
    ],
    "trust_lvl_1": 0.20,
    "trust_lvl_2": 0.30,
    "numb_cluster_threshold": 3,
    "xtc_traj": Path("000/traj_comp.xtc"),
    "topology": Path("000/conf.gro"),
    "dt": 0.02,
    "slice_mode": "gmx"
}))

print(op_out)