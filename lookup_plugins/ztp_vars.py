# ZTP Lookup Plugin
# Collects a list of data which are needed for the ZTP process

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

# Python imports
import io
import requests
import urllib3
import os
from datetime import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DOCUMENTATION = """
    lookup: ztp_vars
    short_description: collects vars needed for ztp process
"""

# Ansible imports
from ansible.errors import AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native, to_text
from ansible.plugins.lookup import LookupBase


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        if 5 < len(terms):
            returntype = terms[5]
        else:
            returntype = ""

        data = self.get_data(terms[0], terms[1], terms[2], terms[3], terms[4], returntype)
        return data

    def get_data(self, switch_list, ip, username, password, site, returntype):
        """
        Collects ZTP Data
        :param switch_list: list of switches that are in the branch
        :param ip: ip of one ztp cx switch
        :param username: username of cx switch
        :param password: password of cx switch
        :param returntype: Which list shall be returned by the function
        :return: List of dicts filled with ZTP vars for each connected Switch
        """

        # reformat switch_data
        switch_data = {}
        for switch_tuple in switch_list:
            switch_data[switch_tuple[0]] = [switch_tuple[1], switch_tuple[2], False]

        self.switch_data = switch_data
        # Set API Parameter
        self.base_url = "https://{0}/rest/v1/".format(ip)
        self.session = self.login(username, password)
        data = []
        try:
            lldp_info = self.fetch_lldp_info().json()

            # check if not lldp_info is not empty
            if not lldp_info:
                self._display.warning("LLDP Info of CX Switch is empty, skipping ztp vars declaration")
                return []

            data, done_list = self.filter_data(lldp_info)

            # check if data is not empty
            if not data:
                self._display.warning(
                    "Data Info of CX Switch is empty, skipping ztp vars declaration."
                    " This mean non of the mac addresses in the switch list and lldp information where matching.")
                data = []
            else:
                data = self.get_lag(data)

            # Build log file
            skip_list = self.build_logfile(site)

            # Decided on which list to return
            if returntype == "skip":
                return skip_list
            elif returntype == "done":
                return done_list
            else:
                return data

        finally:
            self.logout()

    def login(self, username, password):
        """
        Function handles login for REST API of the Switch
        :param username: The switch account username for authentication
        :param password: The switch account password authentication
        :return: Session object
        """
        # Create Session Object
        session = requests.Session()
        # Authenticate Session Object
        response = session.post(self.base_url + "login",
                                params={"username": username, "password": password}, verify=False,
                                timeout=2)
        if response.status_code != 200:
            raise AnsibleParserError('Login Request Failed with Status Code %s .' % to_text(str(response.status_code)))
        else:
            return session

    def logout(self):
        """
        Session will be closed
        :return: True/False
        """
        session = self.session
        response = session.post(self.base_url + "logout", verify=False)
        if response.status_code != 200:
            raise AnsibleParserError('Logout Request Failed with Status Code %s .' % to_text(str(response.status_code)))

    def fetch_lldp_info(self):
        """
        Fetches LLDP Neighbor Information
        :return: JSOn Object of LLDP Information
        """
        response = self.session.get(self.base_url + "system/interfaces/*/lldp_neighbors?depth=1", verify=False,
                                    timeout=2)
        if response.status_code != 200:
            raise AnsibleParserError(
                'LLDP Get Request Failed with Status Code %s .' % to_text(str(response.status_code)))
        else:
            return response

    def filter_data(self, lldp_info):
        """
        Filters LLDP Info for Data that is in Switch list
        :param lldp_info: dict containing lldp neighbor info
        :return: filtered list
        """

        data_filtered_list = []
        done_list = []
        # Filter LLDP Info
        for neighbor in lldp_info:
            mac = neighbor['chassis_id']
            tmp_ip = neighbor['neighbor_info']['mgmt_ip_list']
            # Filter if mac is in switch data and current ip of neighbor is unequal to switch ip
            if (mac in self.switch_data) and (tmp_ip != self.switch_data[mac][0]):
                data_filtered = {'mac': mac.replace(":", "-"), 'static_ip': self.switch_data[mac][0],
                                 'hostname': self.switch_data[mac][1], 'tmp_ip': tmp_ip,
                                 'interface': neighbor['interface'][0]}
                data_filtered_list.append(data_filtered)
                self.switch_data[mac][2] = True
            elif (mac in self.switch_data) and (tmp_ip == self.switch_data[mac][0]):
                data_filtered = {'mac': mac.replace(":", "-"), 'static_ip': self.switch_data[mac][0],
                                 'hostname': self.switch_data[mac][1]}
                done_list.append(data_filtered)
                self.switch_data[mac][2] = True

        return data_filtered_list, done_list

    def get_lag(self, data):
        """
        Get LAG information for each interface
        :param data: data object with filtered data
        :return: data object with additional information
        """
        response = self.session.get(self.base_url + "system/ports/*?attributes=interfaces,name", verify=False,
                                    timeout=2)
        if response.status_code != 200:
            raise AnsibleParserError(
                'Port Get Request Failed with Status Code %s .' % to_text(str(response.status_code)))
        if not response.json():
            raise AnsibleParserError('Port Request returns Empty Object. This means no LAG is configured')

        # reformat response
        lag_dict = {}
        for port in response.json():
            if "lag" in port['name']:
                for intf in port['interfaces']:
                    lag_dict[intf] = port['name']

        if not lag_dict:
            raise AnsibleParserError('No Lag configured on Switch')

        # Match Lag to data_set
        for data_set in data:
            if data_set['interface'] in lag_dict:
                data_set['lag'] = lag_dict[data_set['interface']]
            else:
                raise AnsibleParserError('No Lag configured for interface %s' % to_text(data_set['interface']))

        return data

    def build_logfile(self, site):
        """
        Logs which switches were used for configuration
        :param site: site name for variables
        """
        # Get all Switches which did not match LLDP Info
        skip_list = []
        done_list = []
        for key in self.switch_data:
            if not self.switch_data[key][2]:
                skip_list.append([key, self.switch_data[key][0], self.switch_data[key][1]])
            else:
                done_list.append([key, self.switch_data[key][0], self.switch_data[key][1]])
        # Build Log file
        if not os.path.exists("./ztp_logs/"):
            os.makedirs("./ztp_logs/")
        with io.open("./ztp_logs/" + site + ".txt", 'w') as outfile:
            outfile.write((datetime.now().strftime("%I:%M%p on %B %d, %Y") + "\n").decode('unicode-escape'))
            outfile.write(u"\n *****The following switches got skipped in this run***** \n")
            for switch in skip_list:
                outfile.write(u"MAC:" + str(switch[0]).decode('unicode-escape') + ", IP: " + str(switch[1]).decode(
                    'unicode-escape') + ", Hostname: " + str(switch[2]).decode('unicode-escape') + "\n")
            outfile.write(
                u"\n *****The following switches got configured or are already configured with a static ip**** \n")
            for switch in done_list:
                outfile.write(u"MAC:" + str(switch[0]).decode('unicode-escape') + ", IP: " + str(switch[1]).decode(
                    'unicode-escape') + ", Hostname: " + str(switch[2]).decode('unicode-escape') + "\n")
        return skip_list
