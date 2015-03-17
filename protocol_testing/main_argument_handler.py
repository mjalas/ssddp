import getopt
from sys import argv, exit


class MainArgumentHandler(object):

    def __init__(self):
        pass

    @staticmethod
    def handle_arguments():
        try:
            opts, args = getopt.getopt(argv[1:], "hp:", ["help", "port="])

        except getopt.GetoptError:
            MainArgumentHandler.usage()
            exit(2)

        # Default values

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                MainArgumentHandler.usage()
                exit()
            elif opt in ("-f", "--file"):
                file = arg

        # Return
        return file

    @staticmethod
    def usage():
        print("Usage:\n -f <file_name>\tto use specific test configuration file\n -h\tto display help")

