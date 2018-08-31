# Ansible Tower Branch
This is the project created for usage in Ansible Tower 2.5 or 2.6. 
Integration documentation is below. 

## Ansible Tower Integration
* [Ansible Tower Integration Documentation]()

## Project Structure
```bash
├───aruba_task_lists                # Ansible tasks
│   ├───aos_cx                          # Tasks for ArubaOS-CX
│   ├───aos_switch                      # Tasks for ArubaOS-Switch
│   └───ztp                             # Tasks for the ZTP Solution
├───config                          # Place for generated switch configs
├───files                           # Place for any additional files that are used in tasks
├───filter_plugins                  # Ansible default directory for custom filter plugins
├───group_vars                      # Branch related variables 
├───host_vars                       # Host related variables
├───library                         # Ansible default directory for custom modules
├───lookup_plugins                  # Ansible default directory for custom lookup plugins
├───templates                       # Place to hold Jinja templates for config generation
├───wiki_docu                       # Files for documentation on the GitHub Wiki
└───ztp_logs                        # Directory for additional logs that get created in the ZTP Solution
└───arubaos_switch_config.yml       # Playbook for ArubaOS-Switch Configuration Automation Workflow
└───arubaos_switch_firmware.yml     # Playbook for ArubaOS-Switch Firmware Upgrade Automation Workflow
└───config_generator.yml            # Playbook for ArubaOS-Switch and ArubaOS-CX Config Generation Workflow
└───prem.sh                         # Shell script to correctly set permissions in case of manually import of the project into Ansible Tower
└───ztp_start.yml                   # Playbook for Zero Touch Provisioning (ZTP) Solution Workflow
└───aoss_module_config_example.yml  # Playbook for example usage of AOS-Switch Modules inside this project. 
└───aoscx_module_config_example.yml # Playbook for example usage of AOS-CX Modules inside this project. 
```
  