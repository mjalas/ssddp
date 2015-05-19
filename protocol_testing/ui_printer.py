from protocol_testing.test_printer import TestPrinter


class BaseUIPrinter(object):
    """
    Base logger class
    """
    def __init__(self, log_file, display=True, debug=False, log_messages=False):
        self.debug = debug
        self.display_outputs = display
        self.printer = TestPrinter(log_file)
        self.log_messages = log_messages

    def display(self, message):
        if self.display_outputs:
            self.printer.display(message)

    def log(self, message, append=True):
        self.printer.log(message, append)


class TestUIPrinter(BaseUIPrinter):
    """
    Class that can be used to log test runs.
    """

    def __init__(self, log_file, display=True, debug=False, log_messages=True):
        super().__init__(log_file, display, debug, log_messages)

    def init_input_list(self, start=True):
        if start:
            self.display('Initializing input list.')
        else:
            self.display("Input list initialized.")

    def setup_complete(self):
        self.display("Test setup complete.")

    def start_testing(self):
        self.display("Starting testing stage.")

    def ending_test(self):
        self.display("Ending test...")

    def end_test(self):
        self.display("Test ended!")

    def setup_test(self):
        self.display("Setting up test.")

    def echo_node_waiting(self):
        self.display("Echo node waiting for command...")

    def config_not_found(self):
        self.display("Configuration file not found! Please check that file exists or path is correct!")

    def config_missing(self):
        self.display("No configuration file was given.")

    def available_command_parameters(self):
        self.display("Available command parameters:")

    def shutdown_sent_success(self):
        self.display("Successfully sent shutdown command!")

    def shutdown_sent_failed(self):
        self.display("Shutdown command failed!")

    def no_sockets(self):
        self.display("no sockets")

    def cleanup_started(self):
        self.display("Clean up stage started!")

    def letting_nodes_shutdown(self):
        self.display("Letting nodes shutdown..")

    def nodes_still_running(self):
        self.display("Found nodes still running...")

    def choice_not_available(self, choice):
        self.display("Choice '" + choice + "' not available")

    def cleanup_complete(self):
        self.display("Clean up completed!")

    def echo_received(self, message):
        self.display("Echo: {0}\n".format(message))

    def show_node_enumeration(self, number,  name_description):
        self.display("{0}. {1}".format(number, name_description))

    def option_not_valid(self):
        self.display("Not a valid option")

    def node_names_not_available(self):
        self.display("No node names available")

    def nodes_peers(self):
        self.display("Nodes peers:")

    def nodes_available(self):
        self.display("Nodes available:")

    def communication_wait(self):
        self.display("Waiting couple of seconds for communication to complete..")

    def created_node(self, name):
        self.display("Created node " + name + ".")

    def received_message_from_child(self, message):
        self.display("Received message from child: " + message)

    def received_message_from_parent(self, message):
        self.display("Received message from parent: " + message)

    def result(self, result):
        self.display("Result: " + result)

    def all_nodes_init_failed(self):
        self.display("All node initialization failed!\nEnding test!")

    def nodes_initialized(self, count):
        self.display("Initialized {0} nodes.".format(count))

    def read_command(self, command):
        self.display("Read command: " + command)

    def add_command_parameter(self):
        self.display("Add command parameter!")

    def command_parameters(self):
        self.display("Command parameters:")

    def user_interrupted_test(self):
        self.display("User interrupted test!")

    def new_line(self):
        self.display("\n")

    def show_key_value_pair(self, key, value):
        self.display("{0}: {1}".format(key, value))

    def successfully_started_node(self, node_name):
        self.display("Successfully started node '{0}'".format(node_name))

    def failed_to_start_node(self, node_name):
        self.display("Failed to start node '{0}'".format(node_name))