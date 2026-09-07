import pandas as pd
import numpy as np

data = {
    "content_id": [
        "C01", "C01", "C01", "C01", "C01",
        "C02", "C02", "C02", "C02", "C02",
        "C03", "C03", "C03", "C03", "C03",
        "C04", "C04", "C04", "C04", "C04",
    ],
    "genre": [
        "Drama", "Drama", "Drama", "Drama", "Drama",
        "Comedy", "Comedy", "Comedy", "Comedy", "Comedy",
        "Drama", "Drama", "Drama", "Drama", "Drama",
        "Comedy", "Comedy", "Comedy", "Comedy", "Comedy",
    ],
    "week": [1, 2, 3, 4, 5] * 4,
    "views": [
        12000, 15000, 13000, 17000, 16000,
        8000,  9500,  8800,  10200, 11000,
        20000, 18000, 22000, 21000, 25000,
        5000,  7000,  6500,  8000,  9000,
    ],
    "watch_hours": [
        4500, 5800, 4900, 6700, 6200,
        2100, 2600, 2300, 2900, 3200,
        8000, 7200, 9100, 8500, 10500,
        1200, 1900, 1700, 2200, 2600,
    ],
}

df = pd.DataFrame(data)


# **Your Tasks:**

# **Task 1 — Per-Genre Summary**
# Group by `genre` and compute the **mean** `views` and **mean** `watch_hours` across 
# all rows in that genre. Name the resulting columns `avg_views` and `avg_watch_hours`.

# ---

# **Task 2 — Per-Content Rolling Average Views**
# For each `content_id`, compute a **3-week rolling mean** of `views` (minimum 1 period).
# Add this as a new column called `rolling_avg_views` on the original DataFrame.
# The rolling window should respect the ordering by `week` within each content group.

# ---

# **Task 3 — Week-over-Week View Delta**
# For each `content_id`, compute the **week-over-week difference** in `views` 
# (i.e. current week minus previous week). Add this as a new column called `wow_views_delta`.
# The first week for each content should be `NaN`.

# ---

# **Task 4 — Percentile-Based Performance Tier**
# Using `pd.qcut`, assign each row a performance tier based on the `views` column 
# across the **entire dataset** (not per group). Use 4 quantile buckets and 
# label them `["low", "mid-low", "mid-high", "high"]`. Add this as a new column 
# called `performance_tier`.

# ---

# **Task 5 — Above-Genre-Average Flag**
# For each row, add a boolean column called `above_genre_avg` that is `True` if 
# that row's `views` is greater than the **mean views for its genre**. Use `.transform()`
# with a clean vectorized expression — no branching logic, no if/else, no list comprehensions inside the lambda.

# ---

# **Expected Output Checks:**
# - `df` should have 20 rows and 8 columns after all tasks: the original 5 plus `rolling_avg_views`, `wow_views_delta`, `performance_tier`, and `above_genre_avg`.
# - For `content_id = "C01"`, the `rolling_avg_views` at week 3 should be the mean of weeks 1, 2, and 3 views: `mean([12000, 15000, 13000])`.
# - For `content_id = "C03"`, `wow_views_delta` at week 2 should be `18000 - 20000 = -2000`.
# - `above_genre_avg` should be a column of `True`/`False` values, not strings or integers.



# Task 1

genre_summary = df.groupby(['genre']).agg(
    avg_views = ('views', 'mean'),
    avg_watch_hours = ('watch_hours', 'mean')
).reset_index()

# Task 2

df['rolling_avg_views'] = df.groupby(['content_id'])['views'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# Task 3

df['wow_views_delta'] = df.groupby(['content_id'])['views'].transform(lambda x: x - x.shift(1))

# Task 4

df['performance_tier'] = pd.qcut(df['views'], 4, labels=['low', 'mid_low', 'mid-high', 'high'])

# Task 5

df['above_genre_avg'] = df.groupby(['genre'])['views'].transform(
    lambda x: x > x.mean()
)

# Final Ouput check
df.shape






