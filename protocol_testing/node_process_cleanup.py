import subprocess
from subprocess import Popen, PIPE, check_output


class NodeProcessCleanUp(object):
    """
        Helper class for cleaning up node processes in case all did not shutdown on exit.
    """

    def __init__(self, script_name, print_results=False):
        self.script_name = script_name
        self.tmp_file = "node_ps.txt"
        self.print_result = print_results

    def get_node_pids(self):
        command = 'ps aux | grep "two_node_test.py -f protocol_testing/test_config.json" >> ' + self.tmp_file
        output = check_output(command, shell=True)
        result = output.decode('UTF-8')
        if self.print_result:
            print(result)
        return len(result) > 0

    def kill_nodes(self):
        with open(self.tmp_file, 'r') as f:
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
                        if pid not in found_pids and parameter.endswith("two_node_test.py"):
                            if self.print_result:
                                print("Killing: " + cmd + "--" + parameter + ", pid: " + pid)
                            found_pids.append(pid)
                            command = "kill {0}".format(pid)
                            process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
                            output = process.communicate()[0]
                            if self.print_result:
                                print(output.decode('UTF-8'))

    def check_status(self):
        if self.print_result:
            print('\n')
        ps_command = "ps aux"
        grep_command = 'grep "/two_node_test.py -f protocol_testing/test_config.json"'
        command = ps_command + " | " + grep_command
        output = check_output(command, shell=True)
        if self.print_result:
            print(output.decode('UTF-8'))
