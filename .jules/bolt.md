## 2024-05-18 - DocumentFragment for Large DOM Lists
**Learning:** The frontend architecture renders up to 1000 items concurrently on page load and filter changes. Modifying the DOM by individually appending elements to `postsContainer` inside a large loop causes severe layout thrashing/repaints.
**Action:** Always use `DocumentFragment` when rendering large lists in vanilla JS for this project to batch DOM mutations. Also, memoize or lift operations out of the loop like `new Date()` allocation to save memory/GC pauses.

## 2026-05-07 - Mitigating Serverless Cron Bottlenecks with ThreadPoolExecutor
**Learning:** The application uses a serverless architecture (GitHub Actions cron job). The previous sequential processing of multiple target sites (`requests.get`) caused cumulative blocking on network I/O, extending execution times and potentially risking timeout failures. Python's `ThreadPoolExecutor` handles this pattern well because it mitigates the GIL limitations for I/O bound tasks like network requests.
**Action:** When performing multiple independent HTTP requests in this project, use `concurrent.futures.ThreadPoolExecutor` to run network I/O concurrently. Ensure `executor.map` is used if preserving order is necessary.
