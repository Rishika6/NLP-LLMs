# DSA Intuitions & Rules of Thumb

A running log of non-obvious insights collected while solving problems.

---

## Graph Traversal

### BFS / DFS time complexity
- Both are **O(V + E)** with adjacency list, **O(V²)** with adjacency matrix.
- V + E is a property of *traversal itself* — any algo visiting each vertex/edge a constant number of times hits this bound.
- Space: BFS uses O(V) for queue *width*; DFS uses O(V) for recursion/stack *depth*. Prefer DFS on wide graphs, BFS on deep graphs.

### BFS: always mark visited at ENQUEUE time, not dequeue
- If you mark on dequeue, a cell can be added to the queue many times before it's processed → queue blows up, TLE.
- Rule: the moment you decide to add a neighbor, mark it visited and push it.

### BFS gives shortest path for free (unweighted graphs)
- The first time the target is popped (or enqueued), `cn` is already the minimum.
- Return immediately — no `count` variable, no `Math.min` accumulator.
- Save `min` / priority queues for Dijkstra and weighted graphs.

### Multi-source BFS pattern
- When asked "shortest distance from any of these starting cells" → seed the queue with ALL sources at distance 0, then run one BFS.
- Examples: Rotting Oranges (994), 01 Matrix (542), Walls and Gates (286), As Far from Land (1162).
- Avoids running BFS separately from each source.

### Grid BFS direction arrays
- Use parallel `drow[]` / `dcol[]` arrays and iterate with ONE loop, same index:
  ```java
  for(int i=0; i<k; i++){
      int nr = r + drow[i], nc = c + dcol[i];
  }
  ```
- A nested loop over `i` and `j` mixes row offsets from one direction with col offsets from another → invalid moves AND k² work per cell.

### Grid BFS complexity shortcut
- On an `r × c` grid with constant-degree moves (4 or 8 directions), **V = r·c** and **E = O(r·c)** (each cell has ≤ 8 neighbors).
- So grid BFS is **O(r·c)** time and **O(r·c)** space — not O(V+E) in an abstract sense, just O(cells).
- For an `n × n` grid: **O(n²)**.
- Mental model: "BFS on a grid costs one visit per cell, period."

### State-augmented BFS
- When constraints involve more than just position (e.g., remaining eliminations, collected keys), make the BFS state a tuple: `(r, c, extra_state)`.
- Visited set must key on the full state, not just `(r, c)`.
- Examples: LC 1293 (obstacles elimination), LC 864 (keys as bitmask).

### Cycle detection in undirected graphs (DFS with parent skip)
- DFS each unvisited node; if you reach a visited neighbor that **isn't your parent**, there's a cycle.
- Why it works: every undirected edge is bidirectional — without parent skip, you'd "detect a cycle" on every single edge (B sees A as visited the moment you arrive from A). Parent skip filters the trivial back-edge, leaving only real cycles.
- "Can't move back to the cell you just came from" in a grid problem is **literally the parent-skip rule** restated — recognize the disguise.
- Cycle length ≥ 4 on grids is **free**: grids are bipartite (checkerboard-color them), so every cycle has even length ≥ 4. No length tracking needed.
- Examples: LC 1559 (same-value cycle in grid), LC 261 (Graph Valid Tree), LC 684 (Redundant Connection).
- **Directed graphs use a different pattern**: 3-color DFS (white/gray/black). Parent skip does NOT generalize.

### Directed rooted-tree problems: check BOTH invariants
- A rooted tree has two invariants: every non-root has **exactly one parent**, and there are **no cycles**. An "extra edge" in a directed graph can break either or both.
- Undirected: extra edge ⇒ cycle (one failure mode) ⇒ plain DSU suffices.
- Directed: extra edge ⇒ cycle OR 2-parent node OR both (three failure modes) ⇒ DSU alone is not enough.
- Recognition: "directed graph" + "originally a rooted tree" + N edges for N nodes ⇒ scan for a 2-parent node FIRST, then run DSU on the remaining edges (skipping one of the two candidates).
- Three cases to remember:
  1. No 2-parent node → DSU finds cycle → return cycle-closing edge.
  2. 2-parent node, DSU finds no cycle when skipping the later candidate → return later candidate.
  3. 2-parent node, DSU still finds a cycle when skipping the later candidate → return earlier candidate.
- Examples: LC 685 (Redundant Connection II).

### Union-Find alternative for grid cycle problems
- Walk cells in row-major order; for each cell, only check up/left neighbors (already processed, so right/down haven't been unioned yet).
- If a same-value neighbor is already in the same component as the current cell → cycle.
- Often cleaner than DFS for "connect equal things, detect cycle" grid problems, and the same template works for LC 684, 947, 952.

### Directional edges must validate from BOTH endpoints
- When cells/nodes have *shaped* connections (street pieces, pipes, puzzle tiles, port-typed graphs), a move from A to B is valid **iff A has an opening on side X AND B has an opening on side opposite-X**.
- Write the rule as an `iff`, not a one-way implication. If you only check "A connects right," you'll happily walk into a B that has no left opening.
- Implementation pattern: pass a `from` direction into the recursion/queue; reject the neighbor if its shape doesn't include that side. Use a sentinel (e.g., `'S'`) for the start cell which has no entry direction.
- Smell test: after each recursive call, ask *"what assumption am I making about the next cell?"* Unspoken assumptions about the neighbor's shape are where bugs live.
- Examples: LC 1391 (Check if There is a Valid Path in a Grid), pipe/plumbing problems, port-typed graph traversal.

### Confidence-building habit: predict 3 cases before coding
- Before writing a line, construct on paper: a **trivial pass**, a **trivial fail**, and an **edge case** (start = end, single cell, etc.).
- If your mental model can't predict all three correctly, the intuition isn't ready — keep refining the rule.
- The act of constructing the failing case is what surfaces hidden assumptions (e.g., "what if the neighbor's shape doesn't match?").
- Then trace your *suspected-broken* case through the code by hand. Tracing the easy case proves nothing.

---

## Shortest-Path Triage

(aka "should this be BFS, Dijkstra, DP, or DFS?")

### Three questions, in order

**1. What's being optimized?**

| Asking for… | Tool |
|---|---|
| Min steps/jumps/moves (unit cost per action) | **BFS** |
| Min cost (weights ≥ 0) | **Dijkstra** |
| Min cost, weights can be negative | Bellman-Ford |
| Min cost on a **DAG** (any weights) | Topo sort + DP |
| **Count** paths / sum over paths on a DAG | DP |
| **Any** path / reachability | DFS or BFS |
| **Longest** simple path in general graph | Backtracking DFS (NP-hard) |

Trigger phrases that mean BFS: "min jumps," "min steps," "min operations," "fewest moves," "shortest transformation sequence."

**2. What's the state and what are the transitions?**

Every shortest-path problem is a graph problem in disguise. Force yourself to write:
- **State** = what uniquely identifies "where I am" (an index, a word, `(r, c, keys)`, a board config, …).
- **Transitions** = from state `s`, what's reachable in one step?

Once written, the algorithm is mechanical:
- LC 1345 (Jump Game IV): state = index `i`, transitions = `{i-1, i+1, same-value j's}`, unit cost → BFS.
- LC 127 (Word Ladder): state = word, transitions = words differing by one letter → BFS.
- LC 773 (Sliding Puzzle): state = board, transitions = swap blank with neighbor → BFS.

**3. Is memoization sound?**

Memo on state `s` works **iff** the answer at `s` doesn't depend on the path that reached `s`.

- **DAG** → no cycles → no path-dependence → memo works (this is DP).
- **General graph with cycles** + shortest path → answer at `s` depends on which nodes the current path has already used → **memo on state alone is unsound**.

BFS sidesteps the question: the first time a node is popped, its distance is provably optimal. No memoization, no path-dependence. This is why DFS+memo solves "unique paths in a grid" (DAG: right/down only) but fails Jump Game IV (cycles: `i → i+1 → i` is possible).

### Smell test
> "Does the answer at state `s` depend on which nodes my current path has already used?"
- **No** → DFS+memo is fine (DAG, or the graph is implicitly a tree).
- **Yes** → memo is broken; use BFS (unit cost) or Dijkstra (weighted).

### Common mistakes
- Reaching for DFS+memo on shortest-path-with-cycles. The function isn't well-defined without `visited` in the key; with it, the state space is `n · 2^n`.
- Using a priority queue (Dijkstra) when all edges have unit cost — works but unnecessary; BFS is simpler and faster.
- Forgetting the deduplication trick in BFS over implicit graphs (e.g., Jump Game IV's "clear the value→indices list after first expansion") — turns O(n²) into O(n).
- DFS *can* solve cyclic shortest path via exhaustive backtracking or IDDFS, but never faster than BFS. If DFS+memo "feels wrong" on a shortest-path problem, it is — switch to BFS.

---

## Prefix-Max / Suffix-Min Partitioning

(aka monotonic boundary sweep, partition into independent chunks, sortable-segments pattern)

### Recognition triggers
- Problem has a **pairwise relation with strict index ordering and value comparison** — e.g., "i < j and nums[i] > nums[j]" (inversions), or any "reachable / swappable / groupable" rule between elements at different indices.
- The relation is **symmetric** (or quietly becomes symmetric once you stare at it). If `i ↔ j` is an inversion, both directions of the rule collapse to the same condition.
- Per-index answer depends on a **contiguous region** around the index — usually phrased as "for each i, find max/min/something reachable from i."
- Brute force is "look at every pair" or "BFS/DFS the inversion graph" — both O(n²). When that's the obvious-but-too-slow approach, this pattern is the rescue.
- The boundary between regions can be phrased as **"everything left ≤ everything right"**. If you can describe a valid cut that way, you're on the pattern.

### Why it works
- Symmetric inversion-edges ⇒ undirected graph; reachability = connected components.
- Any inversion crossing position `p` glues left and right halves into one component ⇒ **components are forced to be contiguous index ranges**.
- "No edge crosses position `p`" ⇔ `max(nums[0..p]) ≤ min(nums[p+1..n-1])`. The two preprocessed arrays are the entire trick.

### Mechanical steps
1. `prefMax[i] = max(nums[0..i])`
2. `sufMin[i]  = min(nums[i..n-1])`
3. Sweep: cut between `i` and `i+1` is valid iff `prefMax[i] ≤ sufMin[i+1]`.
4. Cuts partition the array into contiguous blocks; compute the per-block aggregate (max, count, length, …) the problem asks for.
5. Don't forget to close the final block at `i = n-1`.

### Smell test for new problems
> "If I drew every pair `(i, j)` satisfying the rule as an edge, would the components be contiguous index ranges?"
- **Yes** → this pattern.
- **No** → real graph traversal (DFS/BFS/UF on the explicit graph).

### Variants & sibling problems
| Variant | Twist |
|---|---|
| LC 768 — Max Chunks To Make Sorted II | direct twin; count valid cuts |
| LC 769 — Max Chunks To Make Sorted | same, with a permutation |
| LC 915 — Partition Array into Disjoint Intervals | return earliest valid cut |
| LC 1574 — Shortest Subarray to be Removed to Make Array Sorted | two-sweep generalization |
| LC 581 — Shortest Unsorted Continuous Subarray | boundary-finding variant |
| "Max value reachable by valid jumps" (this problem) | per-index aggregate over chunk |

### Common mistakes
- Using `prefMax + sufMax` (both maxes) — wrong, you need **one of each**.
- Strict `<` vs non-strict `≤` at the boundary — depends on whether equal values form edges. Trace one example with duplicates to nail it down.
- Forgetting to close the last chunk when no cut occurs at `i = n-1`.
- Re-running BFS/DFS from each index — the O(n²) trap this pattern exists to avoid.

---

## Exchange-Argument Sorting

(aka pairwise-swap sort, greedy ordering by a derived key)

### Recognition triggers
- Each item has **two or more numbers** playing different roles (one "spent/consumed", one "gate/constraint/score").
- Problem asks for an **optimal ordering** to minimize/maximize something, but the obvious greedy keys (sort by `a`, sort by `m`) feel wrong or break on test cases.
- The objective is a **running max/min** over a quantity that accumulates as you process items (e.g., "minimum starting energy", "maximum performance over any prefix").
- Brute force is "try all n! orderings" — exchange argument collapses it to one sort.

### The mechanical trick
1. Assume an optimal ordering exists.
2. Look at any two adjacent items `X, Y` in that ordering.
3. Write down the cost/constraint for `X then Y` vs `Y then X`.
4. Simplify the inequality `cost(X,Y) ≤ cost(Y,X)` until it becomes a comparison between functions of `X` alone and `Y` alone — that function **is your sort key**.
5. Sort by it, sweep once.

### Canonical swap inequalities
| Problem family | "X before Y" iff |
|---|---|
| Gate-check with cost (LC 1665) | `m_X - a_X ≥ m_Y - a_Y` |
| Lexicographic concat (LC 179) | `X+Y ≥ Y+X` (string compare) |
| Two-city cost split (LC 1029) | `cost_A_X - cost_B_X ≤ cost_A_Y - cost_B_Y` |
| Efficiency-weighted team (LC 1383) | sort by efficiency desc, heap of speeds |

### Sibling pattern: "sort one field, sweep/heap the other"
- Sort by field X desc → iterate → maintain a heap on field Y (k-smallest, k-largest, etc.).
- LC 1383, LC 2542, LC 502 all share this skeleton with LC 1665.

### Smell test
> "If I swap two adjacent items in the answer, what inequality says my original order was better?"
- If the inequality cleanly separates into `f(X) vs f(Y)` → exchange argument, sort by `f`.
- If swapping requires global context → not this pattern; reach for DP or graph methods.

### Common mistakes
- Sorting by the **wrong field** when two fields are present (e.g., sorting LC 1665 by `m` alone instead of `m - a`). The swap-argument inequality is the only safe way to derive the key.
- Forgetting that **the total of `a` is invariant** — order only shifts *when* you pay, not *how much*. The objective is always about timing of the gate check, never about total cost.
- Using binary search on the answer with a wrong `possible()` ordering — BS doesn't save you if the check function uses a bad greedy.

---

## Practice Queues

### Multi-source BFS on grids (Rotten Oranges family)
Suggested solve order: 542 → 286 → 1162 → 1091 → 994 → 1293 → 864

**Direct multi-source BFS variants:**
- [x] LC 994 — Rotting Oranges (the anchor problem)
- [x] LC 542 — 01 Matrix (distance to nearest 0; seed BFS from all 0s)
- [ ] LC 286 — Walls and Gates (fill rooms with distance to nearest gate)
- [x] LC 1162 — As Far from Land as Possible (maximize distance from any land)
- [x] LC 1091 — Shortest Path in Binary Matrix (8-direction BFS, single source)
- [ ] LC 934 — Shortest Bridge (DFS to find one island, then BFS from all its cells)

**Level-by-level BFS ("minutes" / "steps" pattern):**
- [ ] LC 317 — Shortest Distance from All Buildings (BFS from each building, accumulate)
- [ ] LC 773 — Sliding Puzzle (each board state is a node; level = moves)

**State-augmented BFS:**
- [x] LC 1293 — Shortest Path in a Grid with Obstacles Elimination (state: `(r, c, remaining)`)
- [x] LC 864 — Shortest Path to Get All Keys (state: `(r, c, keys_bitmask)`)

### Cycle detection (undirected)
Suggested solve order: 261 → 684 → 1559 → 685

- [x] LC 1559 — Detect Cycles in 2D Grid (DFS with parent skip; grid bipartite ⇒ length ≥ 4 free)
- [ ] LC 261 — Graph Valid Tree (cycle check + single connected component) *(premium, skipped)*
- [x] LC 684 — Redundant Connection (Union-Find shines; return the edge that closes a cycle)
- [x] LC 685 — Redundant Connection II (directed variant — switches to 3-color DFS / different pattern)

### Shortest-Path Triage (BFS on implicit graphs)
Suggested solve order: 1345 → 127 → 433 → 752 → 815

- [ ] LC 1345 — Jump Game IV (anchor; value→indices map + BFS, clear list after expansion)
- [ ] LC 127 — Word Ladder (state = word; transitions = one-letter changes)
- [ ] LC 433 — Minimum Genetic Mutation (Word Ladder twin, 4-letter alphabet)
- [ ] LC 752 — Open the Lock (4-digit state space; BFS over implicit graph)
- [ ] LC 815 — Bus Routes (mirrors Jump Game IV's "clear after use" optimization, for routes)

### Prefix-Max / Suffix-Min Partitioning
Suggested solve order: 769 → 768 → 915 → 581 → 1574

- [x] LC 769 — Max Chunks To Make Sorted (permutation; count cuts where `prefMax[i] == i`)
- [x] LC 768 — Max Chunks To Make Sorted II (general array; `prefMax[i] ≤ sufMin[i+1]` cut rule)
- [x] LC 915 — Partition Array into Disjoint Intervals (return earliest valid cut)
- [x] LC 581 — Shortest Unsorted Continuous Subarray (boundary-finding variant)
- [ ] LC 1574 — Shortest Subarray to be Removed to Make Array Sorted (two-sweep generalization)

### Exchange-Argument Sorting
Suggested solve order: 1665 → 1383 → 179 → 1029 → 502 → 2542 → 1834 → 630

**Anchor & closest siblings (same "sort one field, sweep the other"):**
- [ ] LC 1665 — Minimum Initial Energy to Finish Tasks (sort by `m - a` desc; the anchor)
- [ ] LC 1383 — Maximum Performance of a Team (sort by efficiency desc + min-heap on speeds)
- [ ] LC 2542 — Maximum Subsequence Score (same skeleton as 1383)

**Classic exchange-argument canon:**
- [ ] LC 179 — Largest Number (sort strings by `a+b vs b+a`)
- [ ] LC 1029 — Two City Scheduling (sort by `cost_A - cost_B`)
- [ ] LC 881 — Boats to Save People (sort + two-pointer)

**Scheduling / deadline variants:**
- [ ] LC 502 — IPO (heap variant; capital gate-check + profit)
- [ ] LC 630 — Course Schedule III (duration + deadline; max-heap greedy)
- [ ] LC 1834 — Single-Threaded CPU (sort by enqueue time, tie-break by processing)
- [ ] LC 1167 — Minimum Cost to Connect Sticks (Huffman; combine smallest first)

### Weighted Interval Scheduling (DP on intervals)
Suggested solve order: 1235 → 2008 → 1751 → 2054 → 2830 → 435 → 452 → 646 → 1024 → 1326 → 300

**Anchor & direct twins (weighted DP):**
- [x] LC 1235 — Maximum Profit in Job Scheduling (anchor; start-sort + forward recursion OR end-sort + prefix DP)
- [ ] LC 2008 — Maximum Earnings From Taxi (1235 in disguise: start/end/profit per ride)
- [ ] LC 1751 — Maximum Number of Events That Can Be Attended II (1235 + k-event cap → 2D DP)
- [ ] LC 2054 — Two Best Non-Overlapping Events (fixed k=2 variant)
- [ ] LC 2830 — Maximize the Profit as the Salesman

**Unweighted greedy cousins (recognize the contrast):**
- [ ] LC 435 — Non-overlapping Intervals (sort by end, greedy keep earliest finisher)
- [ ] LC 452 — Minimum Number of Arrows to Burst Balloons (same greedy)
- [ ] LC 646 — Maximum Length of Pair Chain

**Interval coverage variants:**
- [ ] LC 1024 — Video Stitching
- [ ] LC 1326 — Minimum Number of Taps to Open to Water a Garden

**Structural cousin (same "take + jump to next valid" recurrence skeleton):**
- [ ] LC 300 — Longest Increasing Subsequence

---
