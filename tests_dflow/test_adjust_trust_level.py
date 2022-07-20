from dflow.python import (
    OP,
    OPIO,
    OPIOSign
    )
from context import rid
from rid.op.adjust_trust_level import AdjustTrustLevel



op = AdjustTrustLevel()
op_out = op.execute(OPIO({
    "trust_lvl_1": 2.5,
    "trust_lvl_2": 3.5,
    "init_trust_lvl_1": 2.0,
    "init_trust_lvl_2": 3.0,
    "number_of_cluster": 20,
    "number_of_cluster_threshold": 15,
    "amplifier": 1.5,  # 1.5 by default
    "max_level_multiple": 8  # 8 by default
}))

print(op_out)

op_out = op.execute(OPIO({
    "trust_lvl_1": 2.5,
    "trust_lvl_2": 3.5,
    "init_trust_lvl_1": 2.0,
    "init_trust_lvl_2": 3.0,
    "number_of_cluster": 10,
    "number_of_cluster_threshold": 15,
    "amplifier": 1.5,  # 1.5 by default
    "max_level_multiple": 8  # 8 by default
}))

print(op_out)


op_out = op.execute(OPIO({
    "trust_lvl_1": 25,
    "trust_lvl_2": 35,
    "init_trust_lvl_1": 2.0,
    "init_trust_lvl_2": 3.0,
    "number_of_cluster": 10,
    "number_of_cluster_threshold": 15,
    "amplifier": 1.5,  # 1.5 by default
    "max_level_multiple": 8  # 8 by default
}))

print(op_out)