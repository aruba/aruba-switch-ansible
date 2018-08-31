#!/bin/bash
array=( ./aruba_task_lists/ ./filter_plugins/ ./lookup_plugins/ ./library/ ./arubaos_switch_config.yml ./arubaos_switch_firmware.yml ./config_generator.yml ./ztp_start.yml ./ztp_undo.yml ./aoscx_module_config_example.yml ./aoss_module_config_example.yml )
basename "$PWD"
chown awx -R $PWD/
for i in "${array[@]}"
do
    chmod 755 -R ${i}
done

