class InterruptException(Exception):
    def __init__(self, state, value, resumable=True, ns=None):
        super().__init__(str(value))
        self.state = state
        self.value = value
        self.resumable = resumable
        self.ns = ns