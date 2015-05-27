import time
from os import path, utime

from message.timestamp import Timestamp
from protocol_testing.base_protocol_tester import BaseProtocolTester
from testing_scripts.log_file_handler import LogFileHandler

# Test scenarios can be changed by changing file base name or config file directly.
file_base = "three_nodes"
base_log_file = "testing_scripts/test_logs/" + file_base + "_test"
config_file = "testing_scripts/test_configurations/" + file_base + ".json"
node_log_file = "node_discovery_test.log"


def main():
    log_file = LogFileHandler.create_log_file(base_log_file)
    tester = BaseProtocolTester(log_file, __file__, node_log_file)
    try:
        # Setup nodes for the test
        tester.setup_nodes_from_config_file(config_file)
        node_count = len(tester.node_names)
        node_range = range(0, node_count)

        for i in node_range:
            # Start nodes in turn and check displayed measurements.
            tester.start_remote_node(i)

        time.sleep(5)

    except KeyboardInterrupt:
        pass
    except Exception as err:  # Broad exception capture used so that cleanup is always executed. Uncomment to debug.
        print("Caught error: {0}".format(err))
    finally:
        tester.end_test(no_prompt=True)


if __name__ == '__main__':
    main()



