#!/bin/env python3

import os
import subprocess
from subprocess import Popen, PIPE, check_output

filename = "node_ps.txt"


def get_node_pids():
    os.remove(filename)

    command = 'ps aux | grep "network_initializer.py" >> ' + filename
    output = check_output(command, shell=True)
    print(output.decode('UTF-8'))


def kill_nodes(execute=True):
    with open(filename, 'r') as f:
        found_pids = []
        for line in f:
            # print(line)
            if line:
                # print(line)
                data = line.split()
                # print(data)
                pid = data[1]
                cmd = data[10]
                #print(cmd)
                if cmd.strip() == "python3":
                    script_name = data[11]
                    if pid not in found_pids:
                        #print(script_name)
                        if "network_initializer.py" in script_name:
                            if execute:
                                print("Killing: " + cmd + "--" + script_name + ", pid: " + pid)
                            else:
                                print("Will kill: " + cmd + "--" + script_name + ", pid: " + pid)
                            found_pids.append(pid)
                            command = "kill {0}".format(pid)
                            # print(command)
                            if execute:
                                process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                                output = process.communicate()[0]
                                print(output.decode('UTF-8'))


def check_status():
    print('\n')
    ps_command = "ps aux"
    grep_command = 'grep "network_initializer.py"'
    command = ps_command + " | " + grep_command
    output = check_output(command, shell=True)
    print(output.decode('UTF-8'))


def main():
    get_node_pids()
    kill_nodes(False)
    user_input = input("Kill nodes [y/n]:")
    if user_input == 'y':
        print("here")
        kill_nodes()
    check_status()
    print(__file__)


if __name__ == '__main__':
    main()


