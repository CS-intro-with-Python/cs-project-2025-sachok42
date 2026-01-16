from Set import Set

def intersection(set1, set2) -> Set:
    res = set()
    for item in set1:
        if item in set2:
            res.add(item)
    return Set(res)

def are_neighbors(set1, set2) -> bool:
    if abs(len(set1) - len(set2)) == 1 and\
        len(intersection(set1, set2)) == min(len(set1), len(set2)):
        return True
    return False
