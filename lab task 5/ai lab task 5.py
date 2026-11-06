#Task 2: Code with a leaf-evaluation counter
import itertools

TREE = [[[3,5],[6,9]], [[1,2],[0,-1]]]

class Counter: n = 0

def minimax(node, is_max, trace=None):
    if not isinstance(node, list):
        Counter.n += 1                       # leaf-evaluation counter
        if trace is not None: trace.append(node)
        return node
    vals = [minimax(c, not is_max, trace) for c in node]
    return max(vals) if is_max else min(vals)

def alphabeta(node, is_max, alpha, beta, trace=None):
    if not isinstance(node, list):
        Counter.n += 1                       # leaf-evaluation counter
        if trace is not None: trace.append(node)
        return node
    if is_max:
        best = float('-inf')
        for c in node:
            best = max(best, alphabeta(c, False, alpha, beta, trace))
            alpha = max(alpha, best)
            if alpha >= beta: break          # beta cut-off
        return best
    best = float('inf')
    for c in node:
        best = min(best, alphabeta(c, True, alpha, beta, trace))
        beta = min(beta, best)
        if alpha >= beta: break              # alpha cut-off
    return best

def run(tree):
    Counter.n = 0; t1 = []
    v1 = minimax(tree, True, t1); c1 = Counter.n
    Counter.n = 0; t2 = []
    v2 = alphabeta(tree, True, float('-inf'), float('inf'), t2); c2 = Counter.n
    return v1, c1, t1, v2, c2, t2

#Task 3: Reordering branches
import itertools, copy
# Assumed tree (depth 3, root = MAX, then MIN, then MAX, then leaves):
# leaves left to right: 3 5 6 9 1 2 0 -1
TREE = [[[3,5],[6,9]], [[1,2],[0,-1]]]

class Counter: n = 0

def minimax(node, is_max, trace=None):
    if not isinstance(node, list):
        Counter.n += 1                       # leaf-evaluation counter
        if trace is not None: trace.append(node)
        return node
    vals = [minimax(c, not is_max, trace) for c in node]
    return max(vals) if is_max else min(vals)

def alphabeta(node, is_max, alpha, beta, trace=None):
    if not isinstance(node, list):
        Counter.n += 1                       # leaf-evaluation counter
        if trace is not None: trace.append(node)
        return node
    if is_max:
        best = float('-inf')
        for c in node:
            best = max(best, alphabeta(c, False, alpha, beta, trace))
            alpha = max(alpha, best)
            if alpha >= beta: break          # beta cut-off
        return best
    best = float('inf')
    for c in node:
        best = min(best, alphabeta(c, True, alpha, beta, trace))
        beta = min(beta, best)
        if alpha >= beta: break              # alpha cut-off
    return best

def run(tree):
    Counter.n = 0; t1 = []
    v1 = minimax(tree, True, t1); c1 = Counter.n
    Counter.n = 0; t2 = []
    v2 = alphabeta(tree, True, float('-inf'), float('inf'), t2); c2 = Counter.n
    return v1, c1, t1, v2, c2, t2

print("Original order:", run(TREE))

# Reordering experiment: swap the two children at each of the 7 internal nodes (2^7 = 128 orderings)
def swap_at(tree, mask, idx=[0]):
    pass
def build(tree, bits):
    it = iter(bits)
    def rec(n):
        if not isinstance(n, list): return n
        kids = [rec(c) for c in n]
        if next(it): kids.reverse()
        return kids
    return rec(tree)
results = []
for bits in itertools.product([0,1], repeat=7):
    t = build(TREE, bits)
    v1,c1,t1,v2,c2,t2 = run(t)
    assert v1 == v2 == 5 and c1 == 8
    results.append((c2, bits, t, t2))
counts = sorted(set(r[0] for r in results))
print("alpha-beta leaf counts over all 128 orderings:", counts)
for c in counts:
    print(c, "leaves:", sum(1 for r in results if r[0]==c), "orderings")
best = min(results, key=lambda r:r[0]); worst = max(results, key=lambda r:r[0])
print("BEST ", best[0], best[2], "evaluated order:", best[3])
print("WORST", worst[0], worst[2], "evaluated order:", worst[3])
# a simple human reorder: put right MIN branch first at root
t = [TREE[1], TREE[0]]; print("Root swap only:", run(t))