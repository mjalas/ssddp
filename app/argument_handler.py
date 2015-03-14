import getopt
from sys import argv, exit
from app.globals import LISTENING_PORT


class ArgumentHandler(object):

    def __init__(self):
        pass

    @staticmethod
    def handle_arguments():
        try:
            opts, args = getopt.getopt(argv[1:], "hp:", ["help", "port="])

        except getopt.GetoptError:
            ArgumentHandler.usage()
            exit(2)

        # Default values
        port = LISTENING_PORT

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                ArgumentHandler.usage()
                exit()
            elif opt in ("-p", "--port"):
                port = arg

        # Return
        return port

    @staticmethod
    def usage():
        print("Usage:\n -p <port>    to use specific port\n -h    to display help")
