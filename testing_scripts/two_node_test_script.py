import time


from protocol_testing.protocol_tester import BaseProtocolTester
from testing_scripts.log_file_handler import LogFileHandler

base_log_file = "test_logs/two_node_test"
config_file = "test_configurations/two_nodes.json"


def main():
    log_file = LogFileHandler.create_log_file(base_log_file)
    tester = BaseProtocolTester(2, log_file, __file__)
    try:
        # Setup nodes for the test
        tester.setup_nodes_from_config_file(config_file)
        # Start nodes in turn and check measurements.
        sender_name = tester.get_random_remote_name()
        tester.start_node(sender_name, 0)

        sender_name = tester.get_new_random_remote_name()
        tester.start_node(sender_name, 1)

        time.sleep(10)

        tester.end_test(no_prompt=True)
    except KeyboardInterrupt:
        tester.end_test(no_prompt=True)

if __name__ == '__main__':
    main()
