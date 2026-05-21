## 2024-05-18 - DocumentFragment for Large DOM Lists
**Learning:** The frontend architecture renders up to 1000 items concurrently on page load and filter changes. Modifying the DOM by individually appending elements to `postsContainer` inside a large loop causes severe layout thrashing/repaints.
**Action:** Always use `DocumentFragment` when rendering large lists in vanilla JS for this project to batch DOM mutations. Also, memoize or lift operations out of the loop like `new Date()` allocation to save memory/GC pauses.

## 2026-05-07 - Mitigating Serverless Cron Bottlenecks with ThreadPoolExecutor
**Learning:** The application uses a serverless architecture (GitHub Actions cron job). The previous sequential processing of multiple target sites (`requests.get`) caused cumulative blocking on network I/O, extending execution times and potentially risking timeout failures. Python's `ThreadPoolExecutor` handles this pattern well because it mitigates the GIL limitations for I/O bound tasks like network requests.
**Action:** When performing multiple independent HTTP requests in this project, use `concurrent.futures.ThreadPoolExecutor` to run network I/O concurrently. Ensure `executor.map` is used if preserving order is necessary.

## 2024-11-09 - Intl.DateTimeFormat caching inside loops
**Learning:** Using `toLocaleDateString()` inside a loop that iterates over a large dataset (up to 1000 items in this project) is significantly slower than caching an `Intl.DateTimeFormat` instance outside the loop and using its `.format()` method. Furthermore, calling `new Date()` multiple times per item for both date parsing and formatting is redundant.
**Action:** When formatting dates inside a loop, always cache `Intl.DateTimeFormat` outside the loop. Also, minimize redundant `new Date()` calls by parsing once and reusing the object or its parsed time value.

## 2024-03-08 - Requests.Session() for consecutive API requests
**Learning:** Sending multiple consecutive messages using `requests.post()` directly causes the application to establish a new TCP connection and perform a TLS handshake for every single request. This adds significant overhead (often hundreds of milliseconds per request) and network delay when sending notifications to many targets or users.
**Action:** When making multiple consecutive API requests to the same host (such as sending Telegram notifications), always create a `requests.Session()` and pass it to the functions or use it directly. This reuses the underlying connection, avoiding repeated handshakes and significantly improving performance.
