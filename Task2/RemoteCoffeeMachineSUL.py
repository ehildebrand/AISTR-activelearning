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
        output = ''
        for i in inputs:
            self.tn.write((i + '\n').encode('ascii'))
            bytes = self.tn.read_until('\n'.encode('ascii'))
            output = bytes.decode('ascii').replace('\n', '')
        print(output)
        return output

    def reset(self) -> None:
        self.tn.write('reset\n'.encode('ascii'))

    def get_alphabet(self) -> Iterable[str]:
        return ["choose_capuccino", "choose_black", "pay", "make_coffee"]
