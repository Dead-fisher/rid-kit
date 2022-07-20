from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )

import json
from pathlib import Path
from context import rid
from rid.op.prep_exploration import PrepExplore



with open("JSON/rid.json") as jn:
    jdata = json.load(jn)

op = PrepExplore()
op_out = op.execute(OPIO({
    "models": [ Path("test_exploration/graph.000.pb"),
                Path("test_exploration/graph.001.pb"),
                Path("test_exploration/graph.002.pb") ],
    "topology": Path("test_exploration/topol.top"),
    "conf": Path("test_exploration/conf.gro"),
    "trust_lvl_1": jdata["trust_lvl_1"],
    "trust_lvl_2": jdata["trust_lvl_2"],
    "gmx_config": jdata["ExploreMDConfig"],
    "cv_config": jdata["CV"],
    "task_id": 0
}))

print(op_out)