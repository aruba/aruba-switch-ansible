#!/usr/bin/python

import paramiko
import time
import re

DOCUMENTATION = '''
---
module: arubaos_cx_ssh_cli

short_description: Executes CLI commands via SSH on ArubaOS-CX devices.
description:
    - "Executes CLI commands via SSH on ArubaOS-CX devices. Supports show commands. Does not support commands with a prompt."

'''

EXAMPLES = '''
    - name: Associate LAG to int via CLI
      arubaos_cx_ssh_cli:
        ip: "ip of siwtch"
        user: "username for authentication"
        password: "password for authentication"
        # Commands as a list
        commands: ["conf t","int 1/1/16","lag 94"]

'''

RETURN = '''
cli_output:
    description: Output of CLI after each command
    type: list of strings
message:
    description: The output message that the module generates
'''

from ansible.module_utils.basic import AnsibleModule


# Class for SSH CLI
class CliUser:

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
        # AOS-CX specific
        self.get_prompt()

    def execute_command(self, command_list):
        """
        Execute command and returns output
        :param command_list: list of commands
        :return: output of show command
        """
        prompt = re.compile(r'\r\n' + re.escape(self.prompt.replace('#', '')) + '.*# ')
        hostname = re.compile(r'^ho[^ ]*')

        # RFC 1123 Compliant Regex (See https://stackoverflow.com/questions/106179/regular-expression-to-match-dns-hostname-or-ip-address)
        validhostname = re.compile(r'^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$')

        # Clear Buffer
        self.out_channel()

        cli_output = []
        for command in command_list:
            # Check if command wants to change hostname and if so it will also change the prompt regex
            if hostname.search(command):
                new_hostname = command.split(" ")[-1]
                if validhostname.search(new_hostname):
                    self.prompt = new_hostname+"#"
                    prompt = re.compile(r'\r\n' + re.escape(new_hostname) + '.*# ')
                else:
                    self.module.fail_json(
                        msg='To be compliant with RFC 1123, the hostname must contain only letters, '
                            'numbers and hyphens, and must not start or end with a hyphen. Can not change Hostname!')

            self.in_channel(command)
            count = 0
            text = ''
            fail = True
            while count < 45:
                time.sleep(2)
                curr_text = self.out_channel()
                text += curr_text
                if prompt.search(curr_text):
                    fail = False
                    break
                count += 1
            if fail:
                self.module.fail_json(msg='Unable to read CLI Output in given Time')
            # Reformat text
            text = text.replace('\r', '').rstrip('\n')
            # Delete command and end prompt from output
            text_lines = text.split('\n')[1:-1]
            cli_output.append('\n'.join(text_lines))

        return cli_output

    def get_prompt(self):
        """
        Additional needed Setup for Connection
        """
        # Set prompt
        count = 0
        fail = True
        self.in_channel("")
        while count < 45:
            time.sleep(2)
            curr_text = self.out_channel()
            if '#' in curr_text:
                fail = False
                break
            count += 1
        if fail:
            self.module.fail_json(msg='Unable to read CLI Output in given Time')

        # Set prompt
        count = 0
        self.in_channel("")
        # Regex for ANSI escape chars and prompt
        text = ''
        fail = True
        while count < 45:
            time.sleep(2)
            curr_text = self.out_channel()
            text += curr_text.replace('\r', '')
            if '#' in curr_text:
                fail = False
                break
            count += 1

        if fail:
            self.module.fail_json(msg='Unable to read CLI Output in given Time for prompt')

        self.prompt = text.strip('\n').replace(' ', '')


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
        self.in_channel('end')
        self.in_channel('exit')
        self.shell_chanel.close()
        self.ssh_client.close()


def run_module():
    module_args = dict(
        ip=dict(type='str', required=True),
        user=dict(type='str', required=True),
        password=dict(type='str', required=True, no_log=True),
        commands=dict(type='list', required=True),
        port=dict(type='int', required=False, default=22),
        timeout=dict(type='int', required=False, default=60),
        look_for_keys=dict(type='bool', required=False, default=False),
        allow_agent=dict(type='bool', required=False, default=False),
        key_filename=dict(type='str', required=False, default=None),
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
        result['message'] = "Check mode not supported for this module"
        return result

    class_init = CliUser(module)
    try:
        result['cli_output'] = class_init.execute_command(module.params['commands'])
        result['changed'] = True
    finally:
        class_init.logout()

    # Return/Exit
    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
