# AOS Switch Filter - Build Request Bodies for AOS-Switch Requests in Ansible


# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Python imports

# Ansible import
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native, to_text


def json_type_converter(current_dict, typelist):
    """
    This filter fill allow you to build JSON Bodies with Data types of booleans and integers.
    If you enter values which are not in the dict, nothing will happen. This allows you to use this function even for dynamic bodies.
    :param current_dict: the current dict in which strings are that shall be booleans or integers
    :param typelist: a list of list where by each list has a dict key at index 0 and either "int" or "boolean" at index 1.
    :return: current_dict with correct types, best directly transfered into module
    """
    for tuple in typelist:
        if tuple[0] in current_dict:
            type = tuple[1]
            if type == "boolean":
                current_dict[tuple[0]] = bool(current_dict[tuple[0]])
            elif type == "int":
                current_dict[tuple[0]] = int(current_dict[tuple[0]])
            else:
                raise AnsibleParserError(
                    'You entered the not valid type %s for the key %s . Only "int" or "boolean" is allowed.' % (to_text(type),to_text(type[0])))

    return current_dict

def to_int(input_string):
    """
    Turn string into int
    :param input_string
    :return: int of String
    """
    return int(input_string)

class FilterModule(object):

    def filters(self):
        return {
            # Put Body creation
            'json_type_converter': json_type_converter,
            'to_int': to_int

        }
