## 🏪 Retail Sales Analysis: Store Performance Dashboard

# You work as an analytics engineer at a retail company. You've received a raw sales dataset that needs to be cleaned and transformed before it can be used in a reporting dashboard.

### The Dataset

import pandas as pd

data = {
    "sale_id":    [1, 2, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "store_id":   ["S1", "S1", "S1", "S2", "S2", "S3", "S3", "S1", "S2", "S3", "S1", "S2", "S3", "S1", "S2", "S3"],
    "region":     ["North", "North", "North", "South", "South", "East", "East", "North", "South", "East", "North", "South", "East", "North", "South", "East"],
    "category":   ["Electronics", "Clothing", "Clothing", "Electronics", "Furniture", "Clothing", "Electronics", "Furniture", "Clothing", "Furniture", "Electronics", "Electronics", "Clothing", "Furniture", "Furniture", "Electronics"],
    "revenue":    [500, 200, 200, 450, 300, 150, 600, 350, 220, 410, 480, 390, 175, 320, 275, 530],
    "units_sold": [5, 4, 4, 3, 6, 2, 7, 4, 5, 8, 6, 5, 3, 4, 5, 9],
    "quarter":    ["Q1", "Q1", "Q1", "Q1", "Q1", "Q1", "Q2", "Q2", "Q2", "Q2", "Q2", "Q3", "Q3", "Q3", "Q3", "Q3"],
    "rating":     [4, 3, 3, 5, 2, 4, 5, 3, 4, 2, 4, 5, 3, 2, 4, 5]
}

df = pd.DataFrame(data)

### Your Tasks

# **Task 1 — Deduplication**
# The raw data contains duplicate records (a data pipeline bug caused some sales to be logged twice). Remove duplicates based on `sale_id`, keeping the first occurrence. Confirm the shape of the cleaned DataFrame before moving on.

# **Task 2 — Value Mapping**
# The `rating` column contains numeric scores (1–5). Add a new column called `rating_label` that maps these scores to human-readable labels using the following scheme:
# - 1–2 → `"Poor"`
# - 3 → `"Average"`
# - 4 → `"Good"`
# - 5 → `"Excellent"`

# **Task 3 — GroupBy Agg**
# Group the cleaned data by `store_id` and `category`, then compute a summary table with:
# - Total `revenue` (sum)
# - Average `units_sold` (mean, rounded to 1 decimal place)
# - Most common `rating_label` (mode — take the first mode value if there's a tie)

# **Task 4 — GroupBy Transform**
# Add a new column to the cleaned DataFrame called `store_revenue_total` that contains each store's **total revenue across all records**, broadcast back to every row belonging to that store. Then add another column `revenue_pct_of_store` that shows what percentage of the store's total revenue each individual sale represents (rounded to 1 decimal place).

# **Task 5 — Unstack to Pivot**
# Using the cleaned DataFrame, create a pivot table that shows **total revenue** broken down by `quarter` (rows) and `category` (columns). Use `groupby` + `unstack` to produce this — not `pd.pivot_table`. Fill any missing combinations with `0`.

# **Task 6 — Stack to Unpivot**
# Take the pivot table you created in Task 5 and use `.stack()` to melt it back into a long format with columns: `quarter`, `category`, and `revenue`. Reset the index so it's a clean flat DataFrame. Filter out any rows where `revenue == 0`.

# ---

# ### Bonus Challenge
# From your Task 3 summary table, identify which `category` has the highest **average revenue per store** (i.e. average of the per-store total revenues for that category). Print the category name and the value.



#-------------------------------------------
# SOLUTION

# TASK 1
# checking for dupes
dupe_max = df.duplicated(subset=['sale_id'])
dupe_dropped = df.loc[~dupe_max].reset_index(drop=True)
# alternatively, could have just done
# df.drop_duplicates(subset=['sale_id'])

# confirming shape before moving on
print(f'Shape before: {df.shape} | after dedupe: {dupe_dropped.shape}')

# TASK 2
rating_mapping = {
    1:'Poor',
    2:'Poor', 
    3:'Average',
    4:'Good',
    5:'Excellent',
}

dupe_dropped['rating_label'] = dupe_dropped['rating'].map(rating_mapping)

# TASK 3
df_agg = dupe_dropped.groupby(['store_id', 'category']).agg(
    total_revenue=('revenue','sum'),
    avg_units_sold=('units_sold', lambda x: x.mean().round(1)),
    most_common_rating=('rating_label', lambda x: x.mode()[0]),
).reset_index()

# TASK 4
dupe_dropped['store_revenue_total'] = dupe_dropped.groupby(['store_id'])['revenue'].transform('sum')

dupe_dropped['revenue_pct_of_store'] = (
    dupe_dropped['revenue'] / dupe_dropped['store_revenue_total'] * 100
).round(1)

# TASK 5
df_pivot = dupe_dropped.groupby(['quarter','category'])['revenue'].sum().unstack(fill_value=0)

# TASK 6
df_melted = df_pivot.stack().reset_index(name='revenue')
df_melted = df_melted.loc[df_melted['revenue'] != 0].reset_index(drop=True)

# BONUS
highest_avg_revenue = df_agg.groupby(['category']).agg(
    avg_revenue = ('total_revenue','mean')
).reset_index().nlargest(1, 'avg_revenue')

print('--------Highest Avg Revenue per Category--------')
print(f'{highest_avg_revenue.iloc[0, 0]} - {highest_avg_revenue.iloc[0, 1]:.1f}')

