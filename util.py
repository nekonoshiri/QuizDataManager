def Pass():
    pass


def find(pred, itr, throw = False):
    for item in itr:
        if pred(item):
            return item
    if throw:
        raise ValueError('not found')


def findIndex(pred, itr, throw = False):
    ix = 0
    for item in itr:
        if pred(item):
            return ix
        ix += 1
    if throw:
        raise ValueError('not found')


def findIndices(pred, itr):
    ixList = []
    ix = 0
    for item in itr:
        if pred(item):
            ixList.append(ix)
        ix += 1
    return ixList
