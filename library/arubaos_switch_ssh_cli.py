#!/usr/bin/python

import paramiko
import time
import socket
import re
import os

DOCUMENTATION = '''
---
module: arubaos_switch_ssh_cli

short_description: Executes CLI commands via SSH on ArubaOS-Switches

description:
    - "Executes CLI commands via SSH on ArubaOS-Switches"

'''

EXAMPLES = '''
    - name: Enroll SSL for Switch
      arubaos_switch_ssh_cli:
        ip: "ip of siwtch"
        user: "username for authentication"
        password: "password for authentication"
        # Commands as a list
        command_list: ["conf t","crypto pki enroll-self-signed certificate-name ztpcert key-type rsa key-size 1024 subject common-name ztp_cert","web-management ssl"]
      
    - name: Check current Firmware Version
      arubaos_switch_ssh_cli:
        ip: "ip of siwtch"
        user: "username for authentication"
        password: "password for authentication"
        # command, can also be a list with mode changes
        show_command: ["show flash"]
      register: ssh_output
    
    - name: Upgrade Firmware via SSH CLI
      arubaos_switch_ssh_cli:
        ip: "ip of siwtch"
        user: "username for authentication"
        password: "password for authentication"
        # path_to_swi, boot_image and enable_sftp have to be given at once otherwise the module will fail.
        path_to_swi: "../WC_16_06_0006.swi"
        boot_image: "primary"
        enable_sftp: False # If True is given, the system will enable ssh filetransfer and disable tftp | If False is given the system has to have ssh filetransfer enable otherwise the module will stop
        state: "downgrade" # pass "downgrade" to downgrade switch or "current" to stay at same version, default is "upgrade"
      register: module_result

    
'''

RETURN = '''
cli_output:
    description: Output of CLI after each command
    type: list of strings
message:
    description: The output message that the sample module generates
'''

from ansible.module_utils.basic import AnsibleModule


# Class for SSH CLI
class SwitchSSHCLI:

    def __init__(self, module):
        """
        Init all variables and starts login
        :param module: module objects itself
        """
        # Init Vars
        args = module.params
        # List of strings of CLI Commands
        paramiko_ssh_connection_args = {'hostname': args['ip'], 'port': args['port'], 'username': args['user'],
                                        'password': args['password'], 'look_for_keys': args['look_for_keys'],
                                        'allow_agent': args['allow_agent'], 'key_filename': args['key_filename'],
                                        'timeout': args['timeout']}
        self.module = module

        # Login
        self.ssh_client = paramiko.SSHClient()
        # Default AutoAdd as Policy
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to Switch via SSH
        self.ssh_client.connect(**paramiko_ssh_connection_args)
        self.prompt = ''
        # SSH Command execution not allowed, therefor using the following paramiko functionality
        self.shell_chanel = self.ssh_client.invoke_shell()
        self.shell_chanel.settimeout(8)
        # AOS-Switch specific
        self.additional_connection_setup()

    def execute_cli_command(self, command_list):
        """
        Executes the list of CLI commands
        :param command_list: List of Strings with commands
        """
        for command in command_list:
            self.in_channel(command)

    def execute_show_command(self, command_list):
        """
        Execute show command and returns output
        :param command_list: list of commands
        :return: output of show command
        """
        # Regex for ANSI escape chars, prompt and hostname command
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        prompt = re.compile(r'' + re.escape(self.prompt.replace('#', '')) + '.*#')
        hostname = re.compile(r'^ho[^ ]*')

        cli_output = []
        for command in command_list:
            if hostname.search(command):
                self.module.fail_json(
                    msg='You are not allowed to change the hostname while using show command function.')
            self.in_channel(command)
            count = 0
            text = ""
            fail = True
            while count < 45:
                time.sleep(2)
                curr_text = self.out_channel()
                text += ansi_escape.sub('', curr_text).replace('\r', '')
                if prompt.search(curr_text):
                    fail = False
                    break
                count += 1

            if fail:
                self.module.fail_json(msg='Unable to read CLI Output in given Time')

            # Format Text
            text_lines = text.split('\n')[:-1]
            # Remove Command from Output
            if text_lines:
                text_lines[0] = text_lines[0].replace(command, '', 1)
            cli_output.append('\n'.join(text_lines))
        return cli_output

    def additional_connection_setup(self):
        """
        Additional needed Setup for Connection
        """
        chanel_out = ''
        # Max Timeout ca. 1.30 Min (45 * 2)
        count = 0
        no_fail = False
        while count < 45:
            chanel_out += self.out_channel()
            if 'any key to continue' in chanel_out:
                self.in_channel("")
                no_fail = True
                break
            else:
                time.sleep(2)
            count += 1

        if not no_fail:
            self.module.fail_json(msg='Unable to connect correctly to Switch')

        # Additional Sleep
        time.sleep(1)
        # Clear buffer
        self.out_channel()

        # Set prompt
        count = 0
        self.in_channel("")
        # Regex for ANSI escape chars and prompt
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        text = ''
        while count < 45:
            time.sleep(2)
            curr_text = self.out_channel()
            text += ansi_escape.sub('', curr_text).replace('\r', '')
            if '#' in curr_text:
                fail = False
                break
            count += 1

        if fail:
            self.module.fail_json(msg='Unable to read CLI Output in given Time for prompt')

        text.strip('\n')
        self.prompt = text.replace(' ', '')

    def out_channel(self):
        """
        Clear Buffer/Read from Shell
        :return: Read lines
        """
        recv = ""
        # Loop while shell is able to recv data
        while self.shell_chanel.recv_ready():
            recv = self.shell_chanel.recv(65535)
            if not recv:
                self.module.fail_json(msg='Chanel gives no data. Chanel is closed by Switch.')
            recv = recv.decode('utf-8', 'ignore')
        return recv

    def in_channel(self, cmd):
        """
        Sends cli command to Shell
        :param cmd: the command itself
        """
        cmd = cmd.rstrip()
        cmd += '\n'
        cmd = cmd.encode('ascii', 'ignore')
        self.shell_chanel.sendall(cmd)

    def logout(self):
        """
        Logout from Switch
        :return:
        """
        self.in_channel('logout')
        count = 0
        while count < 45:
            time.sleep(2)
            curr_text = self.out_channel()
            if 'want to log out' in curr_text:
                self.in_channel("y")
            elif 'save the current' in curr_text:
                self.in_channel("n")
            try:
                self.in_channel("")
            except socket.error:
                break
            count += 1
        self.shell_chanel.close()
        self.ssh_client.close()

def check_swi_version(result, module):
    """
    Find current SWi Version of Switch
    :param version: version that you want to uplaod to (primary/secondary)
    :return: string of current version without ".swi" ending
    """
    # Init Vars
    regex = u"(?:WC|YA|YC|KB|WB|K|KB)\.[0-9]{2}\.[0-9]{2}\.[0-9]{4}"

    # Find correct version
    matches = re.findall(regex, result)
    if module.params['boot_image'] == "primary":
        current_version = matches[0].replace(".", "_")
        return current_version
    elif module.params['boot_image'] == "secondary":
        current_version = matches[1].replace(".", "_")
        return current_version



def pre_upgrade_firmware(module):
    """
    Checks current version vs to bet version and pre configures Switch for SFTP if argument for it is true
    :param module: the module
    :return: True if current version equal to to be version | False if SFTP configuration is fine and versions are different
    """
    # Init Vars
    to_be_version = os.path.split(module.params['path_to_swi'])[1][:-4]

    # Login and execute CLI Command
    class_init = SwitchSSHCLI(module)
    logout = False
    try:
        # Get Current Flash Output
        result = class_init.execute_show_command(["show flash"])[0].replace(" ", "")

        # Check Current vs to be version
        current_version = check_swi_version(result, module)

        # Version Handling
        state = module.params['state']

        if state == "upgrade" and current_version >= to_be_version:
            class_init.logout()
            logout = True
            return [True, "Switch shall be upgraded but to be version is lower than or equal to current version. Unable to upgrade.", False, True]

        if state == "downgrade" and current_version <= to_be_version:
            class_init.logout()
            logout = True
            return [True, "Switch shall be downgraded but to be version is higher than or equal to current version. Unable to downgrade.", False, True]

        # Enable SFTP for Switch or Check if it is enabled
        if module.params['enable_sftp']:
            class_init.execute_cli_command(['conf t', 'ip ssh filetransfer'])
        else:
            output = class_init.execute_show_command(['show run | include ip ssh'])
            if "ip ssh filetransfer" != output[0]:
                class_init.logout()
                logout = True
                module.fail_json(
                    msg='Ip ssh filetransfer is not enabled, SFTP no possible. Please configure it on the Switch CLI via "ip ssh filetransfer"' )
    finally:
        if not logout:
            class_init.logout()
    return [False]


def upgrade_firmware(module):
    """
    Upgrades Firmware via CLI SFTP Put
    """
    # Inital Vars
    to_be_version = os.path.split(module.params['path_to_swi'])[1][:-4]

    tmp_list = pre_upgrade_firmware(module)
    if tmp_list[0]:
        return tmp_list[1], tmp_list[2],tmp_list[3]




    # Check if File path name is correct
    path_to_swi = os.path.abspath(module.params['path_to_swi'])
    if not os.path.exists(path_to_swi):
        module.fail_json(
            msg='Path to SWI is pointing to non existing directory or file. Path was: {}. '.format(path_to_swi))

    # Create swCfgPath for Switch
    fwPathPrefix = "/os/"
    swCfgPath = fwPathPrefix + module.params['boot_image']
    try:
        t = paramiko.Transport((module.params['ip'], 22))
        t.connect(username=module.params['user'], password=module.params['password'])
        sftp = paramiko.SFTPClient.from_transport(t)
        sftp.put(path_to_swi, swCfgPath, confirm=False)
        sftp.close()
        t.close()
    except Exception as error:
        try:
            sftp.close()
        except NameError:
            pass
        try:
            t.close()
        except NameError:
            pass
        module.fail_json(msg='Ran into exception: {}. Paramiko..'.format(error))

    # Check up to 10 times if current version was successfully uploaded
    class_init = SwitchSSHCLI(module)
    logout = False
    try:
        retries = 0
        while retries != 10:
            # Get current Version
            result = class_init.execute_show_command(["show flash"])[0].replace(" ", "")
            current_version = check_swi_version(result, module)
            # Check if current version is new current version
            if current_version == to_be_version:
                class_init.logout()
                logout = True
                return "{} was successful".format(module.params['state']), True, False
            time.sleep(3)
    finally:
        if not logout:
            class_init.logout()
    return "Unable to check if upload was successful", True, True


def run_module():
    module_args = dict(
        ip=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        command_list=dict(type='list', required=False),
        show_command=dict(type='list', required=False),
        port=dict(type='int', required=False, default=22),
        timeout=dict(type='int', required=False, default=60),
        look_for_keys=dict(type='bool', required=False, default=False),
        allow_agent=dict(type='bool', required=False, default=False),
        key_filename=dict(type='str', required=False, default=None),
        path_to_swi=dict(type='str', required=False, default=None),
        boot_image=dict(type='str', required=False, default='primary', choices=['primary', 'secondary']),
        enable_sftp=dict(type='bool', required=False, default=False),
        state=dict(type='str', required=False, default='upgrade', choices=['upgrade', 'downgrade', 'current'])
    )

    result = dict(
        changed=False,
        cli_output=[],
        message=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False,
    )

    if module.check_mode:
        result['message'] = "Check mode currently not supported for this module"
        return result

    # Main Logic
    result['changed'] = False
    if module.params['path_to_swi']:
        if module.params['state'] == "current":
            result['message'] = "Switch version shall not be changed. Aborting Upgrade. State is 'current'"
            result['changed'] = False
            result['upload_not_completed'] = True
        else:
            result['message'], result['changed'], result['upload_not_completed'] = upgrade_firmware(module)

    class_init = SwitchSSHCLI(module)
    try:
        if module.params['command_list']:
            class_init.execute_cli_command(module.params['command_list'])
            result['changed'] = True

        if module.params['show_command']:
            result['cli_output'] = class_init.execute_show_command(module.params['show_command'])
    finally:
        class_init.logout()

    # Return/Exit
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
