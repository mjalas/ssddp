import getopt
from sys import argv, exit


class MainArgumentHandler(object):

    def __init__(self):
        pass

    @staticmethod
    def handle_arguments():
        opts = None
        try:
            opts, args = getopt.getopt(argv[1:], "hf:", ["help", "file="])

        except getopt.GetoptError:
            MainArgumentHandler.usage()
            exit(2)

        # Default values
        if not opts:
            return None
        file = None
        for opt, arg in opts:
            if opt and arg:
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

