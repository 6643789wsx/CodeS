from functools import reduce

from .string_distance import StringDistance


def default_insertion_cost(char):
    return 1.0


def default_deletion_cost(char):
    return 1.0


def default_substitution_cost(char_a, char_b):
    return 1.0


class WeightedLevenshtein(StringDistance):
    def __init__(
        self,
        substitution_cost_fn=default_substitution_cost,
        insertion_cost_fn=default_insertion_cost,
        deletion_cost_fn=default_deletion_cost,
    ):
        self.substitution_cost_fn = substitution_cost_fn
        self.insertion_cost_fn = insertion_cost_fn
        self.deletion_cost_fn = deletion_cost_fn

    def distance(self, s0, s1):
        if s0 is None:
            raise TypeError("Argument s0 is NoneType.")
        if s1 is None:
            raise TypeError("Argument s1 is NoneType.")
        if s0 == s1:
            return 0.0
        if len(s0) == 0:
            return reduce(lambda cost, char: cost + self.insertion_cost_fn(char), s1, 0)
        if len(s1) == 0:
            return reduce(lambda cost, char: cost + self.deletion_cost_fn(char), s0, 0)

        v0, v1 = [0.0] * (len(s1) + 1), [0.0] * (len(s1) + 1)

        v0[0] = 0
        for i in range(1, len(v0)):
            v0[i] = v0[i - 1] + self.insertion_cost_fn(s1[i - 1])

        for i in range(len(s0)):
            s0i = s0[i]
            deletion_cost = self.deletion_cost_fn(s0i)
            v1[0] = v0[0] + deletion_cost

            for j in range(len(s1)):
                s1j = s1[j]
                cost = 0
                if s0i != s1j:
                    cost = self.substitution_cost_fn(s0i, s1j)
                insertion_cost = self.insertion_cost_fn(s1j)
                v1[j + 1] = min(
                    v1[j] + insertion_cost, v0[j + 1] + deletion_cost, v0[j] + cost
                )
            v0, v1 = v1, v0

        return v0[len(s1)]
