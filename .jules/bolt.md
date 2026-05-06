## 2024-05-18 - DocumentFragment for Large DOM Lists
**Learning:** The frontend architecture renders up to 1000 items concurrently on page load and filter changes. Modifying the DOM by individually appending elements to `postsContainer` inside a large loop causes severe layout thrashing/repaints.
**Action:** Always use `DocumentFragment` when rendering large lists in vanilla JS for this project to batch DOM mutations. Also, memoize or lift operations out of the loop like `new Date()` allocation to save memory/GC pauses.

## 2026-05-06 - Concurrent Web Scraping
**Learning:** The previous implementation executed web scraping tasks sequentially, meaning that network I/O block time was strictly linear with respect to the number of target sites. For a web scraper, I/O wait times dominate processing time.
**Action:** Use `concurrent.futures.ThreadPoolExecutor` to execute `scrape_site` across multiple target sites simultaneously. This drastically reduces the total execution time, scaling favorably up to the `max_workers` limit.
