import getopt
from sys import argv, exit
from app.globals import LISTENING_PORT


class ArgumentHandler(object):
    def __init__(self):

        try:
            opts, args = getopt.getopt(argv[1:], "hp:", ["help", "port="])

        except getopt.GetoptError:
            self.usage()
            exit(2)

        # Default values
        port = LISTENING_PORT

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                self.usage()
                exit()
            elif opt in ("-p", "--port"):
                port = arg

        # Return
        return port

    def usage(self):
        print("-")
