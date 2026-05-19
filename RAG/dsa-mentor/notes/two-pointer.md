# Two-Pointer

## When to reach for it
- Input is sorted (or can be sorted cheaply).
- You want O(n) or O(n log n) instead of O(n^2) by removing a nested loop.
- You're searching for a pair, triplet, or partition that satisfies a constraint.

## Variants
- **Opposite ends:** `l = 0, r = n - 1`. Move the pointer whose value makes the constraint
  worse. Examples: two-sum on sorted, container with most water, valid palindrome.
- **Fast/slow on same end:** both start at 0, fast advances unconditionally. Useful for
  in-place dedup, partitioning, and "remove element" style problems.
- **Fast/slow on linked list:** detect cycle, find middle, find kth-from-end.

## The invariant that makes it work
At every step, you can *eliminate* one pointer's current position from consideration —
because any other partner for that position has already been checked or is provably worse.
If you can't articulate that elimination argument, two-pointer probably isn't the right tool.

## Common traps
- Forgetting to skip duplicates when the problem wants unique pairs/triplets.
- Off-by-one on `while l < r` vs `while l <= r` — they correspond to different invariants.
- Trying two-pointer on an unsorted array where the invariant doesn't hold.
