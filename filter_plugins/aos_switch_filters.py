# AOS Switch Filter - Build Request Bodies for AOS-Switch Requests in Ansible


# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Python imports
import re

# Ansible import
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.errors import AnsibleParserError


def build_snmp_host_body(current_dict):
    """
    Builds snmp host body
    :param current_dict: current put body for snmp host
    :return: snmp host dict
    """
    if current_dict['trap_level'] == "all":
        level = "STL_ALL"
    elif current_dict['trap_level'] == "critical":
        level = "STL_CRITICAL"
    elif current_dict['trap_level'] == "debug":
        level = "STL_DEBUG"
    elif current_dict['trap_level'] == "not_info":
        level = "STL_NOT_INFO"
    else:
        level = "STL_NONE"

    snmp_dict = {
        "community": current_dict['community'],
        "host_ip": {
            "octets": current_dict['host_ip'],
            "version": "IAV_IP_V4"
        },
        "informs": bool(current_dict['informs']),
        "trap_level": level,
        "use_oobm": bool(current_dict['use_oobm'])
    }
    return snmp_dict


def keep_string(boolean):
    """
    Changes true and false back to yes and no (Jinja2 template workaroud)
    :param boolean: true or false
    :return: yes or no
    """
    if boolean:
        return "yes"
    else:
        return "no"


def find_version(serach_string, version):
    """
    Return the current SWI Version of the selected Image
    :param serach_string: string that shall be looked through
    :param version: string for one of the following (primary,secondary,primary_boot,secondary_boot)
    :return: SWI Version as string
    """
    regex = u"(?:WC|YA|YC|KB|WB|K|KB)\.[0-9]{2}\.[0-9]{2}\.[0-9]{4}"
    matches = re.findall(regex, serach_string)
    if version == "primary":
        return matches[0]
    elif version == "secondary":
        return matches[1]
    elif version == "primary_boot":
        return matches[2]
    elif version == "secondary_boot":
        return matches[3]
    else:
        raise AnsibleParserError(
            'No correct version selector entered. Choose one of the following:'
            ' primary,secondary,primary_boot,secondary_boot. You entered: %s .' % to_text(version))


class FilterModule(object):

    def filters(self):
        return {
            # Put Body creation
            'make_snmp_host_body': build_snmp_host_body,
            'keep_string': keep_string,
            'find_version': find_version
        }
