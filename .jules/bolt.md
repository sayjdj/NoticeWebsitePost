## 2024-05-18 - DocumentFragment for Large DOM Lists
**Learning:** The frontend architecture renders up to 1000 items concurrently on page load and filter changes. Modifying the DOM by individually appending elements to `postsContainer` inside a large loop causes severe layout thrashing/repaints.
**Action:** Always use `DocumentFragment` when rendering large lists in vanilla JS for this project to batch DOM mutations. Also, memoize or lift operations out of the loop like `new Date()` allocation to save memory/GC pauses.

## 2026-05-07 - Mitigating Serverless Cron Bottlenecks with ThreadPoolExecutor
**Learning:** The application uses a serverless architecture (GitHub Actions cron job). The previous sequential processing of multiple target sites (`requests.get`) caused cumulative blocking on network I/O, extending execution times and potentially risking timeout failures. Python's `ThreadPoolExecutor` handles this pattern well because it mitigates the GIL limitations for I/O bound tasks like network requests.
**Action:** When performing multiple independent HTTP requests in this project, use `concurrent.futures.ThreadPoolExecutor` to run network I/O concurrently. Ensure `executor.map` is used if preserving order is necessary.

## 2024-11-09 - Intl.DateTimeFormat caching inside loops
**Learning:** Using `toLocaleDateString()` inside a loop that iterates over a large dataset (up to 1000 items in this project) is significantly slower than caching an `Intl.DateTimeFormat` instance outside the loop and using its `.format()` method. Furthermore, calling `new Date()` multiple times per item for both date parsing and formatting is redundant.
**Action:** When formatting dates inside a loop, always cache `Intl.DateTimeFormat` outside the loop. Also, minimize redundant `new Date()` calls by parsing once and reusing the object or its parsed time value.
## 2024-05-25 - Avoid new Date() and Formatting in Render Loops
**Learning:** Calling `new Date(string)` inside a high-frequency loop (like `renderPosts` during filtering) causes measurable overhead. Even with `Intl.DateTimeFormat` cached outside the loop, the sheer act of object allocation and formatting inside the render loop blocked the main thread.
**Action:** When a static list of data requires complex transformation (like parsing dates or formatting them), iterate over the dataset once upon fetch to pre-calculate these values (e.g., `_parsed_time` and `_formatted_date`) and store them on the object itself. Use the pre-calculated fields directly in the render loop. Also, use strict checks like `!== undefined` for numerical values to avoid epoch `0` logic bugs.
