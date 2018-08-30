# AOS Switch Filter - Build Request Bodies for AOS-Switch Requests in Ansible


# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Python imports

# Ansible import
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.errors import AnsibleParserError

def build_bridge_body(bridge_dict, portid):
    """
    Removes interface from bridge table
    :param bridge_dict: current bridge configuration
    :param interface_uri: interface uri that shall be removed
    :return: json object (dict)
    """
    uri = "/rest/v1/system/ports/{}".format(portid)
    if uri not in bridge_dict['ports']:
        bridge_dict['ports'].append(uri)

    return bridge_dict

class FilterModule(object):

    def filters(self):
        return {
            # Put Body creation
            'add_brigde_body': build_bridge_body,
        }
