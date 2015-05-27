import sys
import os
import socket
import select
import time
import json
from sys import exit
import logging

from app.globals import NodeCommand


class TestCommandHandler(object):
    """
    A class for handling commands in protocol testing.
    """

    def __init__(self, printer, ):
        self.command_list = []
        self.logger = logging.getLogger("Tester")
        self.printer = printer

    def display(self, message):
        self.printer.display(message)

    def handle_input(self, input_line):
        # print(input_line)
        if input_line == "exit" or input_line == "quit":
            return NodeCommand.EXIT
        if input_line == "cmd" or input_line.startswith("cmd"):
            return self.handle_command(input_line)
        if input_line == "echo":
            return NodeCommand.ECHO

    def handle_command(self, input_line):
        parameters = input_line.split(' ')
        if parameters[0].strip() == "cmd":
            if len(parameters) == 1:
                return NodeCommand.INCOMPLETE_COMMAND
            if parameters[1].strip() == NodeCommand.DESCRIBE:
                return NodeCommand.DESCRIBE
            elif parameters[1].strip() == NodeCommand.DISPLAY:
                return NodeCommand.DISPLAY
            elif parameters[1].strip() == NodeCommand.HELP:
                return NodeCommand.HELP

    def usage(self):
        self.display("Type cmd --help to get list of commands.")
        self.display("To end test use: 'exit' or 'quit'")

    @staticmethod
    def command_usage():
        return "cmd <command>"

    def choices(self):
        self.display("Valid input formats:")
        self.display("1. {0}".format(self.command_usage()))
        self.display("2. exit")



