from more_itertools.more import first

from functions import intersection

class SetSystem:
    def __init__(self, sets: list):
        self.sets = sets
        self.intersections = {}

    def all_intersections(self):
        taken_array = [1 for _ in range(len(self.sets))]
        while sum(taken_array) != 0:
            for i in range(len(taken_array)):
                if taken_array[i] == 1:
                    taken_array[i] = 0
                    for j in range(i - 1):
                        taken_array[j] = 1
            first = True
            sets_involved = []
            res = None
            for i in range(len(taken_array)):
                if taken_array[i] == 1:
                    if first:
                        first = False
                        res = self.sets[i]
                    else:
                        res = intersection(res, self.sets[i])
                    sets_involved.append(self.sets[i].name)
            self.intersections[sets_involved] = res

