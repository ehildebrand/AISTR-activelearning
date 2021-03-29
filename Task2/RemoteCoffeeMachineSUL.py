from telnetlib import Telnet
from typing import List, Iterable

from stmlearn.suls import SUL


class RemoteCoffeeMachineSUL(SUL):
    def __init__(self, host, port):
        self.tn = Telnet(host, port)

    # Inputs is a list of inputs to send over telnet
    # You should make this function return the last
    # output the coffee machine sends back to you
    def process_input(self, inputs: Iterable[str]) -> str:
        # Implement this
        raise NotImplementedError()

    def reset(self) -> None:
        # And this
        raise NotImplementedError()

    def get_alphabet(self) -> Iterable[str]:
        # Also this
        raise NotImplementedError()
