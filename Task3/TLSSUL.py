from stmlearn.suls import SUL
from TLSAttackerMapper import TLSAttackerMapper


class TLSSUL(SUL):
    def __init__(self, mapper: TLSAttackerMapper):
        self.mapper = mapper

    def process_input(self, inputs):
        input_msges, output_msges = self.mapper.run(inputs)
        last_output = output_msges[-1]
        print("Output:", last_output)
        return last_output

    def reset(self):
        # Due to the way TLSAttacker requires us to specify a complete
        # trace at once, we cannot implement a separate reset.
        # Resets are implicitly ran after every trace.
        pass

    def get_alphabet(self):
        return sorted(list(set(self.mapper.mapping.keys())))


