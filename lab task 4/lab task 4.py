import heapq
G_EDGES = {
    'S': [('A', 1), ('B', 4), ('D', 2)],
    'A': [('C', 2)],
    'B': [('G', 3)],
    'C': [('G', 3)],
    'D': [('G', 7)],
    'G': [],
}
H_ORIG = {'S': 5, 'A': 4, 'B': 3, 'C': 2, 'D': 4, 'G': 0}


def search(h, label):
    print("==", label)
    counter = 0
    pq = [(h['S'], h['S'], counter, 0, 'S', ['S'])]
    closed = set()
    trace = []
    expansions = 0
    stale = 0

    while pq:
        f, hh, _, g, node, path = heapq.heappop(pq)

        if node in closed:            
            stale += 1
            print(f"  pop STALE {node} g={g}")
            continue

        closed.add(node)
        expansions += 1            
        trace.append(node)
        print(f"  expand {node}: g={g} h={h[node]} f={f}  path={'-'.join(path)}")

        if node == 'G':
            cost = sum(dict(G_EDGES[a])[b] for a, b in zip(path, path[1:]))
            print(f"  RESULT path={'-'.join(path)} reported g={g} "
                  f"summed={cost} trace={trace} "
                  f"expansions={expansions} stale_pops={stale}")
            return

        for nxt, c in G_EDGES[node]:    
            if nxt not in closed:
                counter += 1
                heapq.heappush(pq, (g + c + h[nxt], h[nxt], counter,
                                    g + c, nxt, path + [nxt]))

        print("    frontier after:",
              sorted([(x[0], x[1], x[4], x[3]) for x in pq]))  # (f, h, node, g)


search(H_ORIG, "A* original h")
search({k: 0 for k in H_ORIG}, "UCS (h=0)")

h_over = dict(H_ORIG)
h_over['C'] = 10                        
search(h_over, "A* with h(C)=10")