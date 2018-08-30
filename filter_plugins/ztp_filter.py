# ZTP Filter - Build PUT Bodies for AOS-CX Requests in Ansible

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Python Imports
from requests import get
import urllib3
import base64

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Ansible import
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.errors import AnsibleParserError


def fetch_allowed_list(path, ip):
    """
    Fetches all allowed attributes for a certain api path
    :param path: Swagger URI to resource
    :param ip: IP of the AOS-CX Switch
    :return: list of strings that represent attributes of the resource
    """
    # Get API Object
    response = get("https://{}/api/hpe-restapi.json".format(ip), verify=False)
    if response.status_code != 200:
        raise AnsibleParserError(
            'Get API Object Request Failed with Status Code %s .' % to_text(str(response.status_code)))

    # Var Dec
    tmp_object = response.json()['paths']
    allowed_list = []

    # Get all properties of the path
    if path in tmp_object:
        if "put" in tmp_object[path]:
            for parameter in tmp_object[path]['put']['parameters']:
                if parameter['name'] != "data":
                    continue
                else:
                    allowed_list = list(parameter['schema']['properties'].keys())
        else:
            raise AnsibleParserError('No Put Method exists for the path %s .' % to_text(str(path)))
    else:
        raise AnsibleParserError('No API Object exists for the path %s .' % to_text(str(path)))

    return allowed_list


def build_interface_body(current_dict, ip, change_list):
    """
    Build put body for interface and changes the description to hostname
    :param current_dict: get response json object
    :param ip: ip of AOS-CX Switch
    :param change_list: list of params, value pairs you want to change
    :return: json object (dict)
    """
    data = {}
    allowed_list = fetch_allowed_list("/system/interfaces/{id}", ip)

    # Build data object for each allowed attribute that exists in the get response
    for attribute in allowed_list:
        if attribute in current_dict:
            data[attribute] = current_dict[attribute]
    # change description to hostname
    for para, value in change_list:
        if isinstance(value, list):
            if value[0] == "sub_dict":
                if para not in data:
                    data[para] = {}
                data[para][value[1]] = value[2]
            else:
                data[para] = value
        else:
            data[para] = value
    return data


def build_vrf_body(vrf_dict, interface_uri):
    """
    Builds vrf body and removes port uri with interface id of the interface uri from the vrf port table
    :param vrf_dict: get response json object of vrf default request
    :param interface_uri: uri for an interface
    :return: json object (dict)
    """
    uri = "/rest/v1/system/ports/{}".format(interface_uri[27:])
    if uri in vrf_dict['ports']:
        vrf_dict['ports'].remove(uri)

    return vrf_dict


def build_lag_body(current_dict, ip, interface):
    """
    Builds lag body for put request and changes interface for the lag
    :param current_dict: all current lag configurations
    :param interface: interface uri
    :param ip: ip of AOS-CX Switch
    :return: json object (dict)
    """
    allowed_list = fetch_allowed_list("/system/ports/{id}", ip)
    data = {}

    # Build Put Body
    for attribute in allowed_list:
        if attribute in current_dict:
            data[attribute] = current_dict[attribute]
    # Set Interface for Lag
    data["interfaces"] = [interface]

    return data


def build_bridge_body(bridge_dict, interface_uri):
    """
    Removes interface from bridge table
    :param bridge_dict: current bridge configuration
    :param interface_uri: interface uri that shall be removed
    :return: json object (dict)
    """
    uri = "/rest/v1/system/ports/{}".format(interface_uri[27:])
    if uri in bridge_dict['ports']:
        bridge_dict['ports'].remove(uri)

    return bridge_dict


def build_vlan_body(current_dict, vlan_id):
    """
    Builds vlan body and typecasts vlan_id properly
    :param current_dict: current put body for vlan
    :param vlan_id: string of vlan id
    :return:
    """
    current_dict['vlan_id'] = int(vlan_id)
    if 'is_jumbo_enabled' in current_dict:
        current_dict['is_jumbo_enabled'] = bool(current_dict['is_jumbo_enabled'])
    return current_dict


def build_cli_batch_body(command_string):
    """
    Build the encoded Body for the cli batch AOS-Switch API
    :param command_string: string of commands split by "\n"
    :return: encoded body for post request
    """
    command_bytes = command_string.encode()
    base64_command = base64.b64encode(command_bytes)
    command_dict = {'cli_batch_base64_encoded': base64_command.decode('utf-8')}
    return command_dict


class FilterModule(object):

    def filters(self):
        return {
            # Put Body creation
            'make_interface_body': build_interface_body,
            'make_vrf_body': build_vrf_body,
            'make_lag_body': build_lag_body,
            'make_bridge_body': build_bridge_body,
            'make_vlan_body': build_vlan_body,
            'make_cli_batch_body': build_cli_batch_body

        }
