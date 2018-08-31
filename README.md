# Ansible Aruba Switching Automation Workflow GitHub 
Welcome to the Aruba Switching GitHub for automation with Ansible workflows.
This repository provides different examples on how to use Ansible for automation of ArubaOS-Switch and ArubaOS-CX Switches. 

## Preparation for automation server
This project can be used on any Linux based system but we highly recommend CentOS in case of an automation server. 

### Installations
* The project requires to have **Python2.7** and at least **Ansible 2.5** installed on your System. See [Ansible Documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for more information on Ansible installation.
* This project requires following Python Libraries to be installed. See  [Python 2 Package Installation Documentation](https://docs.python.org/2/installing/index.html) for more information on Python package installation. 
    * **Names: "requests", "urllib3", "paramiko"**
    * Example: python -m pip install requests (Proxy Setup needed if Proxy exists, Python pip needed)

### Module Integration
* [Modules Integration and Documentation](https://github.com/aruba/aruba_switch_ansible/wiki/Module-Integration)

    
## Workflows
This project currently holds the following Workflow Documentation. Please click on each link to see further information about the Workflow.


##### General Workflows
* [Create custom Workflow with existing task](https://github.hpe.com/switchautomation/arubaos-switch-ansible/wiki/Create-custom-Workflow-with-existing-task)
* [ArubaOS-Switch Modules Example](https://github.hpe.com/switchautomation/arubaos-switch-ansible/wiki/ArubaOS-Switch-Modules-Examples)
* [ArubaOS-CX Modules Example](https://github.hpe.com/switchautomation/arubaos-switch-ansible/wiki/ArubaOS-CX-Modules-Examples)


##### Specific Workflows
* [Zero Touch Provisioning (ZTP) Solution for an ArubaOS-Switch and ArubaOS-CX environment](https://github.com/aruba/aruba_switch_ansible/wiki/Zero-Touch-Provisioning-(ZTP)-Solution) 
* [ArubaOS-Switch Configuration Automation](https://github.com/aruba/aruba_switch_ansible/wiki/ArubaOS-Switch-Configuration-Automation)
* [ArubaOS-Switch Firmware Upgrade Automation](https://github.com/aruba/aruba_switch_ansible/wiki/ArubaOS-Switch-Firmware-Upgrade-Automation)
* [ArubaOS-Switch and ArubaOS-CX Config Generation](https://github.com/aruba/aruba_switch_ansible/wiki/ArubaOS-Switch-and-ArubaOS-CX-Config-Generation)

##### Ansible Tower Integration
* [Ansible Tower Branch](https://github.com/aruba/aruba_switch_ansible/tree/ansible-tower-support)


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
├───inventory                       # System related variables
├───inventory_creation              # Additional files to create parts of the inventory
├───library                         # Ansible default directory for custom modules
├───lookup_plugins                  # Ansible default directory for custom lookup plugins
├───templates                       # Place to hold Jinja templates for config generation
├───vault                           # Vault directory to save certain variables encrypted 
├───wiki_docu                       # Files for documentation on the GitHub Wiki
└───ztp_logs                        # Directory for additional logs that get created in the ZTP Solution
└───ansible.cfg                     # Ansible configuration
└───arubaos_switch_config.yml       # Playbook for ArubaOS-Switch Configuration Automation Workflow
└───arubaos_switch_firmware.yml     # Playbook for ArubaOS-Switch Firmware Upgrade Automation Workflow
└───config_generator.yml            # Playbook for ArubaOS-Switch and ArubaOS-CX Config Generation Workflow
└───ztp_start.yml                   # Playbook for Zero Touch Provisioning (ZTP) Solution Workflow
└───aoss_module_config_example.yml  # Playbook for example usage of AOS-Switch Modules inside this project. 
└───aoscx_module_config_example.yml # Playbook for example usage of AOS-CX Modules inside this project. 
```
  
