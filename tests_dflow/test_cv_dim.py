from typing import Dict, List
from copy import deepcopy
from dflow import (
    InputParameter,
    OutputParameter,
    Inputs,
    InputArtifact,
    Outputs,
    OutputArtifact,
    Step,
    Steps,
    argo_range,
    argo_len,
    argo_sequence,
    Workflow,
    argo_range
)
from dflow.python import(
    PythonOPTemplate,
    OP,
    OPIO,
    OPIOSign,
    Artifact,
    Slices
)

class GenCVDim(OP):

    @classmethod
    def get_input_sign(cls):
        return OPIOSign()

    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "cv_dim": int
            }
        )

    @OP.exec_sign_check
    def execute(
        self,
        op_in: OPIO,
    ) -> OPIO:
        op_out = OPIO({"cv_dim": 2})
        return op_out

class ReadCVDim(OP):

    @classmethod
    def get_input_sign(cls):
        return OPIOSign({"cv_dim": int})
    @classmethod
    def get_output_sign(cls):
        return OPIOSign(
            {
                "out": int
            }
        )
    @OP.exec_sign_check
    def execute(
        self,
        op_in: OPIO,
    ) -> OPIO:
        out = op_in["cv_dim"]
        print(out)
        op_out = OPIO({"out": out})
        return op_out    
    
if __name__ == "__main__":
    gen_cv = Step(
        'gen-cv',
        template=PythonOPTemplate(
            GenCVDim,
            slices=Slices("{{item}}",
                output_parameter=["cv_dim"]
            ),
            image="python:3.8",
            image_pull_policy="IfNotPresent"
        ),
        parameters={},
        artifacts={},
        with_param=argo_range(3),
        key = 'gen',
    )

    read_cv = Step(
        'read-cv',
        template=PythonOPTemplate(
            ReadCVDim,
            slices=Slices(
                input_parameter=["cv_dim"]),
            image="python:3.8",
            image_pull_policy="IfNotPresent"
        ),
        parameters={"cv_dim": gen_cv.outputs.parameters["cv_dim"]},
        artifacts={},
        with_param=argo_range(3),
        key = 'read',
    )

    wf = Workflow("cv")
    wf.add(gen_cv)
    wf.add(read_cv)
    wf.submit()
