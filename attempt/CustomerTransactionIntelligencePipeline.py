import pandas as pd
import numpy as np

np.random.seed(42)

n = 500
customer_ids = [f"C{str(i).zfill(3)}" for i in np.random.randint(1, 26, n)]
raw_dates = pd.date_range(start="2023-01-01", end="2024-06-30", periods=n)
raw_dates = raw_dates + pd.to_timedelta(np.random.randint(0, 5, n), unit="h")

df = pd.DataFrame({
    "customer_id": customer_ids,
    "raw_transaction_date": raw_dates.strftime("%Y-%m-%d %H:%M:%S"),  # stored as strings
    "amount": np.round(np.random.exponential(scale=80, size=n), 2),
    "category": np.random.choice(["Electronics", "Apparel", "Grocery", "Beauty", "Sports"], n),
    "is_returned": np.random.choice([True, False], n, p=[0.15, 0.85]),
})

# **Your Tasks:**

# **Part 1 — Datetime Parsing & Feature Engineering**

# 1. Parse `raw_transaction_date` into a proper datetime column called `transaction_date`. Then extract and add the following columns to `df`:
#    - `year`, `month`, `quarter`, `day_of_week` (0=Monday), `week_of_year`
#    - `is_weekend`: a boolean flag — `True` if the transaction occurred on Saturday or Sunday
#    - `hour_of_day`: the hour extracted from the timestamp

# **Part 2 — Time-Based Filtering**

# 2. Create a filtered DataFrame called `df_2023` containing only transactions from the year 2023.

# 3. From `df_2023`, create a further filtered DataFrame called `df_q4_2023` containing only Q4 transactions (October, November, December 2023).

# **Part 3 — Monthly Aggregation & MoM Delta**

# 4. Using `df_2023`, group by `customer_id` and `month` to compute total monthly spend per customer (sum of `amount`, excluding returned transactions where `is_returned == True`). Call this result `monthly_spend`.

# 5. Within each `customer_id`, sort by `month` and compute a **month-over-month spend delta** (i.e. the difference from the prior month). Add this as a column called `mom_delta`. Also add a boolean column `mom_growth` that is `True` when `mom_delta > 0`.

# **Part 4 — Rolling Average**

# 6. Still within `monthly_spend`, compute a **3-month rolling average** of spend per customer (ordered by month). Add this as `rolling_3m_avg`. Ensure the rolling window respects customer boundaries (i.e. does not bleed across customers).

# **Part 5 — Performance Tiering**

# 7. Using the total spend per customer across all of 2023 (sum across all months in `monthly_spend`), assign each customer a performance tier using `pd.qcut` with 4 bins. Label the tiers `["Low", "Mid", "High", "Elite"]`. Add this as a column called `spend_tier` on the `monthly_spend` DataFrame by merging or mapping it back in.

# **Part 6 — Day-of-Week Spend Pattern**

# 8. Using the full `df` (all dates), compute the **average transaction amount by day of week** (0=Monday through 6=Sunday) and by `category`. Pivot this into a DataFrame where rows are `day_of_week` and columns are `category`. Call it `dow_category_pivot`. Round all values to 2 decimal places.

# **Part 7 — Resampling**

# 9. Set `transaction_date` as the index on a copy of `df`. Then resample to a **weekly frequency** (`"W"`) and compute:
#    - Total `amount` transacted per week
#    - Count of transactions per week
#    - Return rate per week (mean of `is_returned` cast to int)

#    Store this as `weekly_summary`. Reset the index afterward.

# **Part 8 — Cohort Flag**

# 10. A customer is considered an **"early adopter"** if their **very first transaction** (across the entire dataset, all dates) occurred before `2023-04-01`. Add a boolean column `is_early_adopter` to `monthly_spend` by computing each customer's first transaction date from `df` and mapping it back in. Use only vectorized operations.

# ---

# **Deliverables:**

# At the end, print the following:
# - `monthly_spend.head(20)`
# - `dow_category_pivot`
# - `weekly_summary.head(10)`
# - The count of customers flagged as `is_early_adopter == True` in `monthly_spend`

# ---

# **Constraints:**
# - No `iterrows`, `itertuples`, `apply` with row-wise lambdas, or any Python-level loops over rows
# - All datetime features must be derived using the `dt` accessor or vectorized datetime methods
# - `pd.qcut` must be used for tiering — do not manually define bin edges

# Good luck! When you're ready, save your attempt to a file and share the path for grading. 🚀


#-----------------------------------------------------------
# SOLUTION

# Part 1
df['transaction_date'] = df['raw_transaction_date'].apply(pd.to_datetime)

df['year'] = df['transaction_date'].dt.year
df['month'] = df['transaction_date'].dt.month
df['quarter'] = df['transaction_date'].dt.quarter
df['day_of_week'] = df['transaction_date'].dt.day_of_week
df['hour_of_day'] = df['transaction_date'].dt.hour
df['week_of_year'] = df['transaction_date'].dt.isocalendar().week.astype(int)

df['is_weekend'] = df['day_of_week'].isin([5,6])

# Part 2
df_2023 = df.loc[df['year'] == 2023]
df_q4_2023 = df_2023.loc[df_2023['quarter'] == 4]

# Part 3
monthly_spend = df_2023.groupby(['customer_id', 'month']).apply(
    lambda x: x.loc[
        x['is_returned'] != True
    , 'amount'].sum()
).reset_index(name = 'monthly_spend')

monthly_spend['mom_delta'] = monthly_spend.sort_values(by=['month']).groupby(['customer_id'])\
    ['monthly_spend'].transform(
    lambda x: x - x.shift(1)
).reset_index(drop=True)

monthly_spend['mom_growth'] = monthly_spend['mom_delta'] > 0

# Part 4
monthly_spend['rolling_3m_avg'] = monthly_spend.groupby(['customer_id'])\
    ['monthly_spend'].transform(lambda x: x.rolling(window=3, min_periods=1).mean())

# Part 5
customer_spend = monthly_spend.groupby(['customer_id']).agg(
        total_spend = ('monthly_spend', 'sum')
    )

customer_tier = pd.qcut(customer_spend['total_spend'], q=4, labels=
        ['Low', 'Mid', 'High', 'Elite']) 

monthly_spend['spend_tier'] = monthly_spend['customer_id'].map(customer_tier)

# Part 6
dow_category_pivot = df.groupby(['day_of_week', 'category']).agg(
    avg_spend = ('amount', lambda x: x.mean().round(2))
).unstack()

# Part 7
df_date_index = df.copy().set_index('transaction_date')

df_resampled = df_date_index.resample('W').agg(
    total_amount = ('amount', 'sum'),
    trans_count = ('amount', 'count'),
    avg_returned = ('is_returned', lambda x: x.mean())
)

weekly_summary = df_resampled.reset_index()

# Part 8
# find index of first transaction
first_trans = df.groupby(['customer_id']).agg(
    first_trans_date = ('transaction_date', 'min')
)

min_date = pd.to_datetime('2023-04-01')

first_trans.loc[first_trans['first_trans_date'] < min_date, 'is_early_adopter'] = True

first_trans = first_trans.drop(columns = ['first_trans_date'])

monthly_spend['is_early_adopter'] = monthly_spend['customer_id'].map(first_trans['is_early_adopter'])


# Deliverables
monthly_spend.head(20)
dow_category_pivot
weekly_summary.head(10)
monthly_spend.loc[monthly_spend['is_early_adopter'], 'customer_id'].nunique()


















