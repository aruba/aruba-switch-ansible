# Fills hosts.yml and host_vars

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import os
import io
import csv
import sys

# Main Script
branch_nr = str(sys.argv[1])
branch = "branch" + branch_nr
path_to_csv = "mac_ip" + branch_nr + ".csv"
path_to_host_vars = "../host_vars/"
path_to_inventory = "../inventory/"

# Get CSV Data
if os.path.exists(path_to_csv) and os.path.getsize(path_to_csv) > 0:
    with io.open(path_to_csv, newline='') as file:
        tmp_csv_data = list(csv.reader(file))
else:
    raise EnvironmentError('The file with the path "%s" does not exists or is empty! Please add a .csv file for MAC,IP and Hostname of Switches to configure.' % path_to_csv)

# Build Host_vars .yml for each csv entry
mac_list = []
for csv_list in tmp_csv_data:
    new_mac = "sw-" + str(csv_list[0]).replace(":", "-")
    mac_list.append(new_mac + "\n")
    # Overwrites existing files automatically
    with io.open(path_to_host_vars+new_mac+".yml", 'w') as outfile:
        outfile.write(u"ip"+": " + '"' + str(csv_list[1]) + '"\n')
        outfile.write(u"hostname"+": " + '"' + str(csv_list[2]) + '"\n')
        outfile.write(u"sw_mac"+": " + '"' + str(csv_list[0]) + '"\n')
# Fill Hosts.yml with correct sw_mac strings
if os.path.exists(path_to_inventory+'hosts.yml') and os.path.getsize(path_to_inventory+'hosts.yml') > 0:
    with io.open(path_to_inventory+'hosts.yml') as file:
        file_content = file.readlines()
    firstHalf = file_content[:file_content.index('[' + branch + '_switches]\n') + 1]
    secondHalf = file_content[file_content.index('[' + branch + '_cxs]\n'):]
    new_file_content = firstHalf + mac_list + ["\n"] + secondHalf
    with io.open(path_to_inventory+'hosts.yml', 'w') as outfile:
        for line in new_file_content:
            outfile.write(line.decode('unicode-escape'))
else:
    raise EnvironmentError('The file with the path "%s" does not exists or is empty! Please add a .csv file for MAC,IP and Hostname of Switches to configure.' % (path_to_inventory+'hosts.yml'))



