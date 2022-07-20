

adjust_lvl = Step(
        "adjust-level",
        template=PythonOPTemplate(
            adjust_lvl_op,
            python_packages = upload_python_package,
            slices=Slices(
                input_parameter=["trust_lvl_1", "trust_lvl_2", "numb_cluster", "init_trust_lvl_1", "init_trust_lvl_2"],
                output_parameter=["adjust_trust_lvl_1", "adjust_trust_lvl_2"]),
            **adjust_lvl_template_config,
        ),
        parameters={
            "trust_lvl_1": block_steps.inputs.parameters["trust_lvl_1"],
            "trust_lvl_2": block_steps.inputs.parameters["trust_lvl_2"],
            "init_trust_lvl_1": block_steps.inputs.parameters["init_trust_lvl_1"],
            "init_trust_lvl_2": block_steps.inputs.parameters["init_trust_lvl_2"],
            "numb_cluster": selection.outputs.parameters["numb_cluster"],
            "numb_cluster_threshold": block_steps.inputs.parameters["numb_cluster_threshold"],
            "adjust_amplifier": block_steps.inputs.parameters["adjust_amplifier"], 
            "max_level_multiple": block_steps.inputs.parameters["max_level_multiple"]
        },
        artifacts={},
        with_param=argo_range(argo_len(block_steps.inputs.parameters["trust_lvl_1"])),
        executor = adjust_lvl_executor,
        key = '{}_adjust_level'.format(block_steps.inputs.parameters['block_tag']),
        **adjust_lvl_config,
    )
    block_steps.add(adjust_lvl)