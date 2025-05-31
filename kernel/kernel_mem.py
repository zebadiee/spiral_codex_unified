class KernelMEM:
    def __init__(self):
        self.store = {}

    def get(self, key):
        return self.store.get(key, f"No memory for {key}")

    def set(self, key, value):
        self.store[key] = value

    def all(self):
        return self.store
