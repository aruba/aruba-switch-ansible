# Ansible Aruba Switching Automation Workflow GitHub 
Welcome to the Aruba Switching Automation Workflow GitHub for automation with Ansible!
This repository uses [Ansible tasks lists](https://github.com/aruba/aruba-switch-ansible/tree/master/aruba_task_lists), [SSH modules](https://github.com/aruba/aruba-switch-ansible/tree/master/library), and the [Aruba Switching Ansible Modules](https://github.com/aruba/aruba-ansible-modules)
 to configure ArubaOS-Switch and ArubaOS-CX devices.

## Prerequisites
This project has been tested on Ubuntu 18.04 and CentOS 7 Linux OS but it can be used on any Linux based system.

### Installations
* The project requires to have **Python2.7** or **Python3.5** and at least **Ansible 2.5** installed on your System. See [Ansible Documentation](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html) for more information on Ansible installation.
* This project requires following Python Libraries to be installed. 
    * **Names: "requests", "urllib3", "paramiko"**
* This project requires [Aruba Switching Ansible Modules](https://github.com/aruba/aruba-ansible-modules) to be installed

### Module Installation
* [Modules Installer and Documentation](https://github.com/aruba/aruba-ansible-modules)

    
## Workflows
This project currently holds the following Workflow Documentation. Please click on each link to see further information about the Workflow.

#### Inventory Set Up
See the documented steps on how to set up your inventory to use the workflows in this project here: [Project Inventory Set Up](https://github.com/aruba/aruba-switch-ansible/wiki/Project-Inventory-Set-Up)
    
## Workflows
This project currently holds the following Workflow Documentation. Please click on each link to see further information about the Workflow.

* [ArubaOS-CX Module Configuration Example](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-CX-Module-Configuration-Example)
* [ArubaOS-CX Task Configuration Example](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-CX-Task-Configuration-Example) 
* [ArubaOS-Switch and ArubaOS-CX Config Generation](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-Switch-and-ArubaOS-CX-Config-Generation)
* [ArubaOS-Switch Firmware Upgrade Example](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-Switch-Firmware-Upgrade-Example)
* [ArubaOS-Switch Module Configuration Example](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-Switch-Module-Configuration-Example)
* [ArubaOS-Switch Task Configuration Example](https://github.com/aruba/aruba-switch-ansible/wiki/ArubaOS-Switch-Task-Configuration-Example)
* [Zero Touch Provisioning (ZTP) Workflow](https://github.com/aruba/aruba-switch-ansible/wiki/Zero-Touch-Provisioning-(ZTP)-Workflow)


##### Ansible Tower
* [Ansible Tower Integration](https://github.com/aruba/aruba-switch-ansible/wiki/Ansible-Tower-Integration)



## Project Structure
```bash
├───aruba_task_lists                # Ansible Task Lists
│   ├───aos_cx                          # Task Lists for ArubaOS-CX
│   ├───aos_switch                      # Task Lists for ArubaOS-Switch
│   └───ztp                             # Task Lists for the ZTP Solution
├───config                          # Place for generated switch configs
├───files                           # Place for any additional files that are used in tasks
├───filter_plugins                  # Ansible default directory for custom filter plugins
├───group_vars                      # Branch related variables 
├───host_vars                       # Host related variables
├───images                          # Directory for images in Wiki
├───inventory                       # System related variables
├───inventory_creation_scipts       # Scripts to create parts of the inventory from sources i.e. csv
├───library                         # Ansible default directory for custom modules
├───lookup_plugins                  # Ansible default directory for custom lookup plugins
├───templates                       # Place to hold Jinja templates for config generation
├───vault                           # Vault directory to save certain variables encrypted 
└───ztp_logs                        # Directory for additional logs that get created in the ZTP Solution
└───ansible.cfg                     # Ansible configuration
└───arubaoscx_module_config_example.yml # Playbook for example usage of ArubaOS-CX Modules.
└───arubaoscx_tasks_config_example.yml  # Playbook for ArubaOS-CX Task List Configuration Example Workflow
└───arubaoss_firmware_example.yml       # Playbook for ArubaOS-Switch Firmware Upgrade Example Workflow
└───arubaoss_module_config_example.yml  # Playbook for example usage of ArubaOS-Switch Modules.
└───arubaoss_tasks_config_example.yml   # Playbook for ArubaOS-Switch Task List Configuration Example Workflow
└───config_generator.yml            # Playbook for ArubaOS-Switch and ArubaOS-CX Config Generation Workflow
└───ztp_start.yml                   # Playbook for Zero Touch Provisioning (ZTP) Workflow
```
  
