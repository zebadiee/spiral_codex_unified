from kernel.reward_tracker import RewardTracker


class ProposalPolicy:
    def __init__(self, kernel_sym):
        self.kernel_sym = kernel_sym

    def generate_scaffold(self, x, y_star):
        return self.kernel_sym.resolve(f"generate_scaffold({x}, {y_star})")

    def generate_batch(self):
        return ["τ1", "τ2"]

    def update(self, scaffold, reward):
        pass

    def adjust(self, scaffold, reward):
        pass


class ExecutionPolicy:
    def __init__(self, kernel_mem):
        self.kernel_mem = kernel_mem

    def execute(self, x="default"):
        ritual = self.kernel_mem.query(f"ritual_for({x})") or {"ritual": f"auto({x})"}
        return ritual

    def update(self, result, reward):
        pass

    def adjust(self, result, reward):
        pass

    def load_scaffold(self, τ):
        pass


class DualLoopLearner:
    def __init__(self, kernel_sym, kernel_mem):
        self.π_propose = ProposalPolicy(kernel_sym)
        self.π_solve = ExecutionPolicy(kernel_mem)
        self.reward_tracker = RewardTracker()

    def propose_loop(self, env, training_pairs):
        for x, y_star in training_pairs:
            τ = self.π_propose.generate_scaffold(x, y_star)
            r = env.evaluate_proposal(τ)
            self.reward_tracker.log("π_propose", τ, r)
            self.π_propose.update(τ, r)

    def solve_loop(self, env, input_stream):
        for x in input_stream:
            y = self.π_solve.execute(x)
            r = env.evaluate_solution(y)
            self.reward_tracker.log("π_solve", str(y), r)
            self.π_solve.update(y, r)

    def cross_train(self, env, epochs=3):
        for _ in range(epochs):
            for τ in self.π_propose.generate_batch():
                self.π_solve.load_scaffold(τ)
                y = self.π_solve.execute()
                r = env.evaluate(y)
                self.π_propose.adjust(τ, r)
                self.π_solve.adjust(y, r)
