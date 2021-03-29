from telnetlib import Telnet
from stmlearn.suls import SUL


class RemoteCoffeeMachineSUL(SUL):
    def __init__(self, host, port):
        self.tn = Telnet(host, port)

    def process_input(self, inputs):
        # Implement this
        raise NotImplementedError()

    def reset(self):
        # And this
        raise NotImplementedError()

    def get_alphabet(self):
        # Also this
        raise NotImplementedError()
