import time


def start_node(tester, node_at_index, node_count, seconds_to_wait=3):
    sender_name = tester.node_names[node_at_index]
    print("Starting node '{0}'".format(sender_name))
    tester.start_node(sender_name, node_count)
    print("Node '{0}' started".format(sender_name))
    print("Waiting {0} seconds for broadcast test".format(seconds_to_wait))
    time.sleep(seconds_to_wait)
