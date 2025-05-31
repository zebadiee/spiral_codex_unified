class KernelMIND:
    def __init__(self):
        self.state = {}

    def dispatch(self, symbol):
        return f"Dispatched: {symbol}"
