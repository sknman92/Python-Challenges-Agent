import pandas as pd

data = {
    "order_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "region": ["North", "South", "North", "East", "South", "East", "North", "West", "West", "South"],
    "category": ["Electronics", "Clothing", "Clothing", "Electronics", "Electronics", "Clothing", "Electronics", "Clothing", "Electronics", "Clothing"],
    "sales_amount": [250.00, 80.00, 120.00, 430.00, 310.00, 95.00, 175.00, 60.00, 540.00, 45.00],
    "units_sold": [2, 3, 5, 1, 4, 2, 3, 1, 6, 2]
}
df = pd.DataFrame(data)

#-------------------------------------------------------------
# **Your tasks:**

# 1. Calculate the **total sales amount** and **total units sold** for each combination of `region` and `category`.

# 2. Add a new column called `avg_order_value` that represents the average sales amount per unit sold 
# (i.e., `total_sales / total_units`) for each group.

# 3. Sort the results by `total_sales_amount` in **descending order**.

# 4. Filter the final result to only include rows where `total_sales_amount` is **greater than 200**.

# **Expected output columns:** `region`, `category`, `total_sales_amount`, `total_units_sold`, `avg_order_value`
#-------------------------------------------------------------

df.head()

# Task 1
df_agg = df.groupby(['region', 'category']).agg(
    total_sales_amount = ('sales_amount', 'sum'),
    total_units_sold = ('units_sold', 'sum')
).reset_index()

# Task 2
df_agg['avg_order_value'] = df_agg['total_sales_amount'] / df_agg['total_units_sold']

# Task 3
df_sorted = df_agg.sort_values(by = ['total_sales_amount'], ascending=False)

# Task 4
df_filtered = df_sorted.loc[df_sorted['total_sales_amount'] > 200]



