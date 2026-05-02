## 2024-05-24 - DocumentFragment and Date Loop Caching
**Learning:** In a vanilla JS app rendering up to 1000 items, appending directly to the DOM in a loop causes significant performance drops due to excessive reflows and repaints. Similarly, instantiating `new Date()` within a large loop is computationally expensive.
**Action:** Use `document.createDocumentFragment()` to batch DOM insertions into a single reflow. Cache variables like `new Date()` outside the loop if they remain constant for the entire loop iteration.
