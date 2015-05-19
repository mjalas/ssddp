
from app.globals import NodeCommand
from protocol_testing.protocol_tester import BaseProtocolTester

log_file = "two_node_test.log"
config_file = "test_configurations/two_nodes.json"


def main():

    tester = BaseProtocolTester(2, log_file, __file__)
    # Setup nodes for the test
    tester.setup_nodes_from_config_file(config_file)
    # Start nodes in turn and check measurements.
    #sender_name = tester.get_random_remote_name()
    node_count = 1
    #tester.start_node(sender_name, node_count)
    node_count += 1




    tester.end_test()


if __name__ == '__main__':
    main()
