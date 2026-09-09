# **Challenge: Sales Report File Handler**

# You work as an analytics engineer at a retail company. Every week, you need to process raw sales data and produce several output files for different teams. Your task is to implement a series of file I/O operations using proper context managers throughout — no bare file opens, no skipping `with` statements.

# ---

# **The Data**

import pandas as pd
import csv
import os

# Weekly sales transactions
sales_data = [
    {"order_id": "A001", "region": "North", "product": "Widget", "units": 10, "unit_price": 25.50, "date": "2024-01-08"},
    {"order_id": "A002", "region": "South", "product": "Gadget", "units": 4,  "unit_price": 89.99, "date": "2024-01-08"},
    {"order_id": "A003", "region": "North", "product": "Gadget", "units": 7,  "unit_price": 89.99, "date": "2024-01-09"},
    {"order_id": "A004", "region": "East",  "product": "Widget", "units": 15, "unit_price": 25.50, "date": "2024-01-09"},
    {"order_id": "A005", "region": "West",  "product": "Doohickey", "units": 3, "unit_price": 149.00, "date": "2024-01-10"},
    {"order_id": "A006", "region": "South", "product": "Widget", "units": 8,  "unit_price": 25.50, "date": "2024-01-10"},
    {"order_id": "A007", "region": "East",  "product": "Doohickey", "units": 2, "unit_price": 149.00, "date": "2024-01-11"},
    {"order_id": "A008", "region": "West",  "product": "Gadget", "units": 6,  "unit_price": 89.99, "date": "2024-01-11"},
    {"order_id": "A009", "region": "North", "product": "Widget", "units": 12, "unit_price": 25.50, "date": "2024-01-12"},
    {"order_id": "A010", "region": "East",  "product": "Gadget", "units": 5,  "unit_price": 89.99, "date": "2024-01-12"},
]

# A second batch that arrives later in the week (for the append task)
late_arrivals = [
    {"order_id": "A011", "region": "West",  "product": "Widget", "units": 9,  "unit_price": 25.50, "date": "2024-01-13"},
    {"order_id": "A012", "region": "North", "product": "Doohickey", "units": 1, "unit_price": 149.00, "date": "2024-01-13"},
]

# **Your Tasks**

# **Task 1 — Write a CSV using the `csv` module with a context manager**

# Using the `csv.DictWriter` and a `with` statement, write `sales_data` to a file called `sales_raw.csv`. Include a header row. Do not use pandas for this task.

# ---

# **Task 2 — Read it back and verify with a context manager**

# Using `csv.DictReader` inside a `with` statement, read `sales_raw.csv` back in. Print the total number of rows read and confirm it matches `len(sales_data)`. Also print the `order_id` and computed `revenue` (units × unit_price) for each row. Note: all values read from a CSV via the `csv` module come back as strings — handle the type casting correctly.

# ---

# **Task 3 — Append late arrivals to the existing CSV**

# Open `sales_raw.csv` in append mode using a context manager and write the `late_arrivals` rows using `csv.DictWriter`. Important: do NOT write the header again. After appending, read the file back and confirm the total row count is now 12.

# ---

# **Task 4 — Write a summary log as a plain text file**

# Using `open()` as a context manager, write a plain text file called `weekly_summary.txt`. The file should contain:
# - A title line: `Weekly Sales Summary — Week of 2024-01-08`
# - A blank line
# - One line per region showing total revenue for that region, formatted like:
#   `North: $1,234.56`
# - A final line showing overall total revenue

# Use all 12 rows (original + late arrivals) for the calculations. Do all aggregation in Python or pandas — your choice — but the file writing must use a `with` block.

# ---

# **Task 5 — Write a multi-sheet Excel file using `pd.ExcelWriter` as a context manager**

# Using `pd.ExcelWriter` inside a `with` statement (this is the correct, modern way to use it — do not call `.save()` or `.close()` manually), write an Excel file called `sales_report.xlsx` with the following three sheets:

# - **`Raw Data`**: all 12 rows as a DataFrame
# - **`By Region`**: total units and total revenue grouped by region, sorted by total revenue descending
# - **`By Product`**: total units and total revenue grouped by product, sorted by total revenue descending

# ---

# **Task 6 — Error-safe file reading**

# Write a function called `safe_read_csv(filepath)` that:
# - Accepts a file path string
# - Uses a `with` statement and a `try/except` block to attempt to open and read the file
# - If the file does not exist, catches the appropriate exception, prints a user-friendly message like `"File not found: <filepath>"`, and returns `None`
# - If the file exists, reads it with `csv.DictReader` and returns a list of dicts
# - Test it by calling it once with `"sales_raw.csv"` (should succeed) and once with `"nonexistent_file.csv"` (should fail gracefully)

# ---

# **Constraints and Best Practices to Follow**

# - Every file open operation must use a `with` statement — no exceptions
# - Do not call `.close()` anywhere manually
# - For Task 5, use `pd.ExcelWriter` as a context manager (the `with pd.ExcelWriter(...) as writer:` pattern)
# - For Task 3, be careful about the append mode and header behaviour
# - For Task 6, the `try/except` must sit outside or wrap the `with` block — think carefully about where the `FileNotFoundError` is actually raised

# ---

#---------------------------------------------------------------------
# SOLUTION
import json

# Task 1
sales_data
file_name = 'sales_raw.csv'
directory = 'data'
file_path = os.path.join(directory, file_name)
with open(file_path, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=sales_data[0].keys())
    writer.writeheader()
    writer.writerows(sales_data)

# Task 2
with open(file_path, 'r') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    if not len(sales_data) == (len(rows)):
        raise RuntimeError("Number of rows don't match")
    df = pd.DataFrame(rows)
    df[['units', 'unit_price']] = df[['units', 'unit_price']].apply(lambda x: x.astype(float))
    print(df['order_id'])
    df['revenue'] = df['units'] * df['unit_price']

with open(file_path, 'w', newline='') as w:
    df.to_csv(w, index=False)


# Task 3
with open(file_path, 'a', newline='') as f:
    df = pd.DataFrame(late_arrivals)
    df['revenue'] = df['units'] * df['unit_price']
    df_dict = df.to_dict('records')
    writer = csv.DictWriter(f, fieldnames=df.columns)
    writer.writerows(df_dict)

# Task 4
log_name = 'sales_log.txt'
log_file_path = os.path.join(directory, log_name)
with open(log_file_path, 'w') as f:
    f.write('Weekly Sales Summary - Week of 2024-01-08')
    
with open(log_file_path, 'a') as f:
    region_revenue = df.groupby(['region'])['revenue'].sum().reset_index()
    region_revenue['summary'] = region_revenue['region'] + ": $" + region_revenue['revenue']\
        .map('{:,.2f}'.format) + "\n"

    f.write("\n")

    for x in region_revenue['summary']:
        f.write(x)

    total_revenue =  region_revenue['revenue'].sum()
    final_line = f"Total Revenue: {total_revenue}"
    f.write(final_line)

# Task 5
excel_name = "sales_report.xlsx"
excel_file_path = os.path.join(directory, excel_name)

with pd.ExcelWriter(excel_file_path, mode='w') as excel_writer:
    with open(file_path, 'r') as file_reader:
        reader = csv.DictReader(file_reader)
        rows = list(reader)
        df = pd.DataFrame(rows)
        raw_data = df
        by_region = df.groupby(['region']).agg(
            total_units = ('units', 'sum'),
            total_revenue = ('revenue', 'sum'),
        ).sort_values(by=['total_revenue'], ascending=False).reset_index()
        by_product = df.groupby(['product']).agg(
            total_units = ('units', 'sum'),
            total_revenue = ('revenue', 'sum')
        ).sort_values(by=['total_revenue'], ascending=False).reset_index()

        raw_data.to_excel(excel_writer, sheet_name = "Raw Data", index=False)
        by_region.to_excel(excel_writer, sheet_name = "By Region", index=False)
        by_product.to_excel(excel_writer, sheet_name = "by_product", index=False)
        
# Task 6

def safe_read_csv(filepath:str):
    assert filepath, "Must supply a filepath"

    try:
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            return rows
    except FileNotFoundError as e:
        print(f"File was not found: {e}")


# testing
safe_read_csv(r"sales_raw.csv")


