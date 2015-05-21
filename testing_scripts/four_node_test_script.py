import time

from testing_scripts.testing_script_helpers import start_node
from protocol_testing.protocol_tester import BaseProtocolTester
from testing_scripts.log_file_handler import LogFileHandler

base_log_file = "test_logs/four_node_test"
config_file = "test_configurations/four_nodes.json"


def main():
    log_file = LogFileHandler.create_log_file(base_log_file)
    tester = BaseProtocolTester(4, log_file, __file__)
    try:
        # Setup nodes for the test
        tester.setup_nodes_from_config_file(config_file)
        print("Nodes " + str(len(tester.node_names)))
        # Start nodes in turn and check measurements.
        tester.start_remote_node(0)
        tester.start_remote_node(1)
        tester.start_remote_node(2)
        tester.start_remote_node(3)

        time.sleep(10)

    except KeyboardInterrupt:
        pass
    finally:
        tester.end_test(no_prompt=True)


if __name__ == '__main__':
    main()


