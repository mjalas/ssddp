import time

from testing_scripts.testing_script_helpers import start_node
from protocol_testing.protocol_tester import BaseProtocolTester
from testing_scripts.log_file_handler import LogFileHandler

base_log_file = "test_logs/three_node_test"
config_file = "test_configurations/three_nodes.json"


def main():
    log_file = LogFileHandler.create_log_file(base_log_file)
    node_count = 1
    tester = BaseProtocolTester(2, log_file, __file__)
    try:
        # Setup nodes for the test
        tester.setup_nodes_from_config_file(config_file)
        # Start nodes in turn and check measurements.
        start_node(tester, 0, 0)
        start_node(tester, 1, 1)
        start_node(tester, 2, 2)

        time.sleep(10)

        tester.end_test(no_prompt=True)
    except KeyboardInterrupt:
        tester.end_test(no_prompt=True)

if __name__ == '__main__':
    main()

