# Slow customer order lookup (simulated)

This exercise isolates SQL performance in a temporary in-memory database. It does not inject API latency or change your normal database.

1. Run `python -m scripts.benchmark`.
2. Read `benchmark-results.json`. Compare the median of 30 runs before and after indexing.
3. Explain why the first plan scans rows and may sort, while the second can search an index.
4. Record your own machine, date and results. The query, data and warmup are identical between phases.
5. Repeat if desired to observe variation. Do not claim these timings represent production performance.

Root cause: filtering and ordering lack a supporting index in the initial benchmark table.
Resolution: add `(customer_id, created_at DESC)` index. The normal API schema already includes this index.
Verification: compare plans and measured medians. There is no fixed speedup requirement.
Customer response example: We added an index supporting customer order lookups and confirmed the query uses it. Timing results are recorded for the test environment.
