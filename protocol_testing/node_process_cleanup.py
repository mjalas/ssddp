import subprocess
from subprocess import Popen, PIPE, check_output
import os


class NodeProcessCleanUp(object):
    """
        Helper class for cleaning up node processes in case all did not shutdown on exit.
    """

    def __init__(self, script_name, print_results=False):
        self.script_name = script_name
        self.tmp_file = "node_ps.txt"
        self.dirname = os.path.dirname(os.path.abspath(__file__))
        self.abspath = self.dirname + "/" + self.tmp_file
        self.print_result = print_results
        self.project_path = str.join("/", self.dirname.split("/")[:-1])

    def get_node_pids(self):
        # command = 'ps aux | grep "/home/spacy/aalto/protocol/2015-group1/" >> ' + self.abspath
        # print(self.abspath)
        # print(self.dirname)
        command = 'ps aux | grep "' + self.dirname + '" >> ' + self.abspath
        output = check_output(command, shell=True)
        result = output.decode('UTF-8')
        if self.print_result:
            print(result)
        return len(result) > 0

    def kill_nodes(self, script_filename, execute=True):
        tmp = script_filename.split('.')
        if len(tmp) > 1:
            script_filename = tmp[len(tmp)-1]
        if ".py" not in script_filename:
            script_filename += ".py"
        print("Cleaning up processes for script: " + script_filename)
        with open(self.abspath, 'r') as f:
            found_pids = []
            for line in f:
                if line:
                    # print(line)
                    data = line.split()
                    #print(data)
                    pid = data[1]
                    cmd = data[10]
                    if cmd.strip() == "/usr/bin/python3.4":
                        parameter = data[11]
                        if pid not in found_pids and parameter.endswith(script_filename):
                            found_pids.append(pid)
                            if execute:
                                print("Killing: " + cmd + "  " + parameter + ", pid: " + pid)
                                command = "kill {0}".format(pid)
                                process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                                output = process.communicate()[0]
                                if self.print_result:
                                    print(output.decode('UTF-8'))
                            else:
                                print("Will kill following: " + cmd + "  " + parameter + ", pid: " + pid)

    @staticmethod
    def check_status():
        print('\n')
        ps_command = "ps aux"
        grep_command = 'grep "/home/spacy/aalto/protocol/2015-group1/"'
        command = ps_command + " | " + grep_command
        output = check_output(command, shell=True)
        print(output.decode('UTF-8'))
