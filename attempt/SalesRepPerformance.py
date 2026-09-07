import pandas as pd

data = {
    "deal_id": range(1, 21),
    "rep": [
        "Alice", "Bob", "Alice", "Carol", "Bob",
        "Alice", "Carol", "Bob", "Carol", "Alice",
        "Bob", "Alice", "Carol", "Bob", "Alice",
        "Carol", "Bob", "Alice", "Carol", "Bob"
    ],
    "month": [
        "2024-01", "2024-01", "2024-01", "2024-01", "2024-02",
        "2024-02", "2024-02", "2024-02", "2024-03", "2024-03",
        "2024-03", "2024-03", "2024-04", "2024-04", "2024-04",
        "2024-04", "2024-05", "2024-05", "2024-05", "2024-05"
    ],
    "deal_value": [
        12000, 8500, 15000, 4000, 9000,
        11000, 7500, 3000, 14000, 6000,
        9500, 18000, 5000, 11000, 7000,
        13000, 16000, 4500, 8000, 12500
    ],
    "days_to_close": [
        30, 45, 20, 60, 35,
        25, 50, 70, 15, 40,
        30, 10, 55, 28, 42,
        18, 22, 65, 33, 27
    ],
    "product": [
        "Pro", "Basic", "Enterprise", "Basic", "Pro",
        "Pro", "Enterprise", "Basic", "Enterprise", "Basic",
        "Pro", "Enterprise", "Pro", "Enterprise", "Basic",
        "Enterprise", "Enterprise", "Basic", "Pro", "Pro"
    ]
}

df = pd.DataFrame(data)

# **Your tasks:**

# **Step 1 — Monthly rep summary**

# Group by `rep` and `month` and compute:
# - `total_revenue`: sum of `deal_value`
# - `deal_count`: number of deals
# - `avg_days_to_close`: mean of `days_to_close`
# - `enterprise_share`: proportion of deals where `product == "Enterprise"` (a value between 0 and 1)

# Store this as a DataFrame called `monthly_summary`. Make sure `month` is sorted chronologically within each rep.

# ---

# **Step 2 — 3-month rolling average revenue**

# For each rep, compute a 3-month rolling average of `total_revenue` (using a minimum of 1 period so early months are not dropped). Add this as a column called `rolling_3m_revenue` on `monthly_summary`.

# This must respect the per-rep grouping — the rolling window should not bleed across reps.

# ---

# **Step 3 — Month-over-month revenue change**

# For each rep, compute the absolute change in `total_revenue` from the previous month. Call this column `mom_revenue_delta`. The first month for each rep should be `NaN`.

# Again, this must not bleed across reps.

# ---

# **Step 4 — Tier assignment**

# Using the `total_revenue` column, assign a performance tier for each rep-month row using the following logic:

# - `"Elite"` — `total_revenue` is in the top 25% across **all** rep-month rows
# - `"Strong"` — between 50th and 75th percentile
# - `"Developing"` — between 25th and 50th percentile
# - `"Underperforming"` — bottom 25%

# Use `pd.qcut` with appropriate labels. Add this as a column called `tier`. Do not hardcode any revenue thresholds.

# ---

# **Step 5 — Flag reps improving**

# Add a boolean column called `is_improving` that is `True` if `rolling_3m_revenue` is strictly greater than the rep's own **median** `rolling_3m_revenue` across all their months. Use `transform` cleanly — no loops, no manual merges.

# ---

# **Final output**

# Print `monthly_summary` with all columns:
# `rep`, `month`, `total_revenue`, `deal_count`, `avg_days_to_close`, `enterprise_share`, `rolling_3m_revenue`, `mom_revenue_delta`, `tier`, `is_improving`

# ---

# **Constraints and quality bar:**
# - No Python `for` loops over rows or groups
# - No hardcoded revenue thresholds in Step 4
# - `transform` must be used correctly in Step 5 — a single clean expression, not a branching lambda
# - Use `.empty` if you ever need to check whether a DataFrame has no rows
# - All rolling and diff operations must be scoped per rep — test this by checking that Alice's row in `2024-01` does not influence Bob's rolling average


# Step 1:

# first cleaning month to dt
df['month'] = pd.to_datetime(df['month'], format='%Y-%m')

monthly_summary = df.groupby(['rep', 'month']).agg(
    total_revenue = ('deal_value', 'sum'),
    deal_count = ('product', 'count'),
    avg_days_to_close = ('days_to_close', 'mean'),
    enterprise_share = ('product', lambda x: sum([1 if y == 'Enterprise' else 0 for y in x]) / x.count())
).reset_index()

# Step 2

monthly_summary['rolling_3m_revenue'] = monthly_summary.groupby(['rep'])['total_revenue'].transform(lambda x: x.rolling(window=3, min_periods=1).sum())

# Step 3

monthly_summary['mom_revenue_delta'] = monthly_summary.groupby(['rep'])['total_revenue'].transform(lambda x: x - x.shift(1))

# Step 4

monthly_summary['tier'] = pd.qcut(monthly_summary['total_revenue'], q=4, labels=['Underperforming', 'Developing', 'Strong', 'Elite'])

# Step 5

monthly_summary['is_improving'] = monthly_summary.groupby(['rep'])['rolling_3m_revenue'].transform(
    lambda x: [True if y > x.median() else False for y in x]
)

# Final Output

print(monthly_summary)



