from app.ssddp import SSDDP
from protocol_testing.main_argument_handler import MainArgumentHandler

if __name__ == "__main__":
    argument_handler = MainArgumentHandler()
    file = argument_handler.handle_arguments()
    node1 = SSDDP("node1")
    node1.start()
    node2 = SSDDP("node2")
    node2.start()


