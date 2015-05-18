import socket
import sys
import os
import time
from datetime import datetime

from protocol_testing.ui_printer import TestUIPrinter
from node.node_creation_type import NodeCreationType
from protocol_testing.protocol_tester import TEST_BUFFER_SIZE
from app.ssddp import SSDDP
from protocol_testing.config_test_file import ConfigurationNode


class NodeProcessCreator(object):
    """
    Helper class for creating node processes for testing purposes.
    """
    def __init__(self):
        self.ui_printer = TestUIPrinter()
        self.remotes = {}

    def init_nodes_from_config_nodes(self, config_nodes):
        failed_count = 0
        success_count = 0
        for config_node in config_nodes:
            self.ui_printer.display(config_node.name)
            child, parent = socket.socketpair()
            pid = os.fork()
            if pid:
                failed_count, success_count = self.handle_parent_part(child, parent, config_node, failed_count,
                                                                      success_count)
            else:
                self.handle_child_part(child, config_node, parent)
                exit()

        if failed_count == len(config_nodes):
            self.ui_printer.all_nodes_init_failed()
            for sock in self.remotes.values():
                sock.close()
            exit(0)
        else:
            self.ui_printer.nodes_initialized(success_count)

    def handle_parent_part(self, child, parent, config_node, failed_count, success_count):
        self.ui_printer.display("Created node " + config_node.name + ".")
        child.close()
        self.remotes[config_node.name] = parent
        # parent.settimeout(8)
        response = parent.recv(TEST_BUFFER_SIZE).decode('UTF-8')
        self.ui_printer.received_message_from_child(response)
        if response == NodeCreationType.FAILED:
            failed_count += 1
        else:
            success_count += 1
        return failed_count, success_count

    def handle_child_part(self, child, config_node, parent):
        self.ui_printer.created_node(config_node.name)
        parent.close()
        result = self.create_node_process(config_node, child)
        self.ui_printer.result(result)
        if result == NodeCreationType.FAILED:
            child.sendall(bytes(result, 'UTF-8'))
            child.close()

    def create_node_process(self, config_node, command_sock):
        if not isinstance(config_node, ConfigurationNode):
            raise ValueError("No ConfigurationNode given")
        try:
            ssddp_node = SSDDP(name=config_node.name, services=config_node.services, external_command_input=command_sock,
                       remote_run=True)
            ssddp_node.start()
            return NodeCreationType.SUCCESS
        except AttributeError as e:
            self.ui_printer.display(e.args)
        return NodeCreationType.FAILED