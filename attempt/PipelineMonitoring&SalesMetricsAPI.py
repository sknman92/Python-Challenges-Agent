#  Here is your next challenge — a real-world analytics engineering FastAPI project! 🚀

# ---

# ## **FastAPI Challenge: Pipeline Monitoring & Sales Metrics API**

# You're an analytics engineer at a data company. Your team runs dbt pipeline jobs daily and tracks sales performance across regions. You've been asked to build a small internal API that lets stakeholders query pipeline run history and sales metrics — the kind of thing you'd normally expose via a BI tool, but your team wants programmatic access.

# ---

# ### **Your Dataset**

# Use the following hardcoded data in your app:

# ```python
pipeline_runs = [
    {"run_id": 1, "pipeline_name": "customers_mart", "status": "success", "duration_seconds": 142, "run_date": "2024-06-01", "rows_processed": 18400},
    {"run_id": 2, "pipeline_name": "orders_mart", "status": "failed", "duration_seconds": 87, "run_date": "2024-06-01", "rows_processed": 0},
    {"run_id": 3, "pipeline_name": "customers_mart", "status": "success", "duration_seconds": 155, "run_date": "2024-06-02", "rows_processed": 18750},
    {"run_id": 4, "pipeline_name": "revenue_mart", "status": "success", "duration_seconds": 210, "run_date": "2024-06-02", "rows_processed": 52300},
    {"run_id": 5, "pipeline_name": "orders_mart", "status": "success", "duration_seconds": 98, "run_date": "2024-06-03", "rows_processed": 31200},
    {"run_id": 6, "pipeline_name": "revenue_mart", "status": "failed", "duration_seconds": 45, "run_date": "2024-06-03", "rows_processed": 0},
    {"run_id": 7, "pipeline_name": "customers_mart", "status": "success", "duration_seconds": 160, "run_date": "2024-06-04", "rows_processed": 19100},
    {"run_id": 8, "pipeline_name": "orders_mart", "status": "success", "duration_seconds": 102, "run_date": "2024-06-04", "rows_processed": 33800},
]

sales_records = [
    {"sale_id": 1, "region": "north", "rep_name": "Alice", "product": "Analytics Pro", "amount": 12400.0, "sale_date": "2024-06-01"},
    {"sale_id": 2, "region": "south", "rep_name": "Bob", "product": "Data Starter", "amount": 3200.0, "sale_date": "2024-06-01"},
    {"sale_id": 3, "region": "north", "rep_name": "Alice", "product": "Data Starter", "amount": 3100.0, "sale_date": "2024-06-02"},
    {"sale_id": 4, "region": "west", "rep_name": "Carlos", "product": "Analytics Pro", "amount": 15800.0, "sale_date": "2024-06-02"},
    {"sale_id": 5, "region": "south", "rep_name": "Diana", "product": "Analytics Pro", "amount": 13500.0, "sale_date": "2024-06-03"},
    {"sale_id": 6, "region": "west", "rep_name": "Carlos", "product": "Data Starter", "amount": 2900.0, "sale_date": "2024-06-03"},
    {"sale_id": 7, "region": "north", "rep_name": "Bob", "product": "Analytics Pro", "amount": 11200.0, "sale_date": "2024-06-04"},
    {"sale_id": 8, "region": "east", "rep_name": "Diana", "product": "Data Starter", "amount": 4100.0, "sale_date": "2024-06-04"},
]
# ```

# ---

# ### **What You Need to Build**

# **1. GET `/pipelines`**
# Return all pipeline runs. Support an optional query parameter `status` (values: `"success"` or `"failed"`) to filter results. If `status` is not provided, return all runs.

# **2. GET `/pipelines/{pipeline_name}/summary`**
# Return a summary for a specific pipeline (matched by `pipeline_name` as a path parameter). The summary should include:
# - `pipeline_name`
# - `total_runs`
# - `successful_runs`
# - `failed_runs`
# - `avg_duration_seconds` (rounded to 1 decimal place)
# - `total_rows_processed`

# If the pipeline name doesn't exist in the data, return a **404** with a meaningful error message.

# **3. GET `/sales`**
# Return all sales records. Support **two optional query parameters**:
# - `region` — filter by region (e.g. `"north"`, `"west"`)
# - `product` — filter by product name (e.g. `"Analytics Pro"`)

# Both filters should be combinable (i.e. you can filter by region AND product at the same time).

# **4. GET `/sales/summary`**
# Return an aggregated summary across all sales records (no filters needed). The response should include:
# - `total_sales` (count of records)
# - `total_revenue` (sum of all amounts)
# - `avg_sale_amount` (rounded to 2 decimal places)
# - `top_region` (the region with the highest total revenue)
# - `top_rep` (the rep with the highest total revenue)

# **5. POST `/sales`**
# Accept a new sale submission. Validate the incoming payload using a **Pydantic model**. Required fields: `region`, `rep_name`, `product`, `amount`, `sale_date`. The `sale_id` should be auto-assigned (e.g. max existing ID + 1). Append the new record to `sales_records` and return the full created record.

# ---

# ### **Requirements & Constraints**

# - Define **Pydantic response models** for at least the pipeline summary endpoint and the sales summary endpoint (the ones returning computed/aggregated data). You can use response models for the others too if you want the practice.
# - Use proper HTTP status codes (200, 201 for created, 404 for not found).
# - Your POST `/sales` endpoint should return a `201` status code on success.
# - No database required — work entirely with the in-memory lists above.
# - Structure your code cleanly. If it starts getting long, consider separating your models into a `models.py` file (optional but good practice).

# ---

# ### **Stretch Goals (optional, but try at least one)**

# - Add a query parameter to `GET /pipelines` to filter by `run_date`
# - Add input validation to the POST endpoint so that `amount` must be greater than 0 and `region` must be one of a fixed set of allowed values
# - Add a `GET /sales/{sale_id}` endpoint that returns a single sale by ID or 404 if not found

# ---

#-------------------------------------------
# SOLUTION

from fastapi import FastAPI, HTTPException, status
app = FastAPI()

import pandas as pd
from enum import Enum
from pydantic import BaseModel, Field, field_validator

# Base models for query parameter validation
class Status(str, Enum):
    success = 'success'
    failed = 'failed'
 
class Region(str, Enum):
    north = 'north'
    south = 'south'
    east = 'east'
    west = 'west'

# Task 1
@app.get("/pipelines")
def get_pipeline_runs(status: Status | None = None):

    return [p for p in pipeline_runs if status is None or p.get('status', None) == status]

# basemodel to validate output for pipeline summary api
class pipelineSummary(BaseModel):
    pipeline_name : str = Field(
        description="name of pipeline user requested"
    )

    total_runs: float = Field(
        description="count of runs"
    )

    successful_runs: float = Field(
        description="count of successful runs"
    )

    failed_runs: float = Field(
        description="count of failed runs"
    )

    avg_duration_seconds: float = Field(
        description="avg seconds it took for a pipeline to run"
    )

    total_rows_processed: float = Field(
        description="sum of rows processsed"
    )

# Task 2
@app.get("/pipelines/{pipeline_name}/summary", response_model=pipelineSummary)
def get_pipeline_summary(pipeline_name: str):
    
    """
    Per grading, FastAPI won't even route to the funciton if pipeline name is missing from URL.
    This is a no-op.
    """
    # assert pipeline_name, 'Must supply a pipeline name'

    pipeline = [p for p in pipeline_runs if p.get('pipeline_name', None) == pipeline_name]

    if pipeline:

        df_pipeline = pd.DataFrame(pipeline)

        return {
                'pipeline_name' : pipeline_name,
                'total_runs' : df_pipeline.shape[0],
                'successful_runs' : df_pipeline.loc[df_pipeline['status'] == 'success'].shape[0],
                'failed_runs' : df_pipeline.loc[df_pipeline['status'] == 'failed'].shape[0],
                'avg_duration_seconds' : float(round(df_pipeline['duration_seconds'].mean(), 1)),
                'total_rows_processed' : int(df_pipeline['rows_processed'].sum())
            }

    else:
        raise HTTPException(status_code=404, detail='Pipeline name does not exist in data')

# Task 3
@app.get("/sales")
def get_sales(region: Region | None = None, product: str | None = None):
    return [s for s in sales_records if (region is None or s.get('region', None) == region) and (product is None or s.get('product', None) == product)]

# defining basemodel to validate output
class salesSummary(BaseModel): 
    total_sales: float = Field(
        description="count of total sales")

    total_revenue: float = Field(
        description="sum of amount"
    )

    avg_sale_amount: float = Field(
        description="avg sale amount"
    )

    top_region: str = Field(
        description="top region my sales"
    )

    top_rep: str = Field(
        description="top rep by sales"
    )

# Task 4
@app.get("/sales/summary", response_model=salesSummary)
def get_sales_summary():
    df_sales = pd.DataFrame(sales_records)
    
    return {
            'total_sales' : df_sales.shape[0],
            'total_revenue' : float(df_sales['amount'].sum()),
            'avg_sale_amount' : float(round(df_sales['amount'].mean(), 2)),
            'top_region' : df_sales.groupby(['region'])['amount'].sum().nlargest(1).index[0],
            'top_rep' : df_sales.groupby(['rep_name'])['amount'].sum().nlargest(1).index[0],
        }

# Task 5
# defining basemodel to validate incoming submission
class SalesSubmission(BaseModel):
    region: Region

    rep_name: str = Field(
        description="name of the rep"
    )

    product: str = Field(
        description="product name"
    )

    amount: float = Field(
        gt=0,
        description="sales amount"
    )

    sale_date: str = Field(
        description="stringified date (YYYY-MM-DD)"
    )

    @field_validator('sale_date')
    def validate_date_format(cls, v):
        import re
        if not re.match(r'\d{4}-\d{2}-\d{2}', v):
               raise ValueError("sale_date must be in YYYY-MM-DD format")
        return v

@app.post("/sales", status_code=201)
def post_sales(sales_input: SalesSubmission):

    max_id = 0
    for s in sales_records:
        sale_id = s.get('sale_id', 0)
        if sale_id > max_id:
            max_id = sale_id

    # materialize input
    s = sales_input.model_dump(mode='json')

    """
    Per grading, don't want to assert in a FastAPI endpoint.
    Won't be caught gratefully and will return a generic 500 error
    """
    # test date field
    # import re
    # re_date = re.compile(r'\d{4}-\d{2}-\d{2}')
    # assert re_date.match(s['sale_date']), "Date field in json load must match YYYY-MM-DD"

    # test amount
    # assert s['amount'] > 0, "Amount must be greater than 0"

    max_id += 1

    new_s = {"sale_id": max_id, **s}

    sales_records.append(new_s)

    return new_s


# Task 5
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("PipelineMonitoring&SalesMetricsAPI:app", host="127.0.0.1", port=8000, reload=True)



