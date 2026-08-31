import pandas as pd

data = {
    "rep": ["Alice", "Alice", "Alice", "Bob", "Bob", "Bob", "Carol", "Carol", "Carol"],
    "region": ["North", "North", "South", "North", "South", "South", "North", "North", "South"],
    "deal_size": ["small", "large", "large", "small", "small", "large", "large", "small", "large"],
    "revenue": [1200, 8500, 7200, 950, 1100, 6800, 9100, 800, 5500]
}

df = pd.DataFrame(data)

#-----------------------------------------------------------
# **Your tasks:**

# 1. For each sales rep, calculate their **total revenue** and **number of deals**.

# 2. Add a column called `avg_large_deal` that shows each rep's **average revenue 
# from large deals only**. If a rep has no large deals, show `0`.

# 3. Filter the final result to only include reps whose **total revenue is above 15,000**.

# Your final output should be a DataFrame indexed (or grouped) by `rep`, with the columns:
#  `total_revenue`, `num_deals`, and `avg_large_deal`.
#-----------------------------------------------------------

# Task 1
df[['total_revenue', 'num_deals']] = df.groupby('rep')[['revenue', 'deal_size']].\
    transform(lambda x: x.sum() if x.name == 'revenue' else x.count()
              ) 
                                                                     
# Task 2
def _avg_large_deal(rep_group):
    """"
    Helper function taking each rep group
    and calculating avg_large_deal.
    If rep has no large deal, showing 0
    """

    # filter to large groups
    group_filtered = rep_group.loc[rep_group['deal_size'] == 'large']

    # calculating avg_large_deal
    # if group_filtered is not None:
    if not group_filtered.empty:
        # if there are surviving roles, calculate average
        avg_large_deal = group_filtered['revenue'].sum() / group_filtered['deal_size'].count()

    else:
        # otherwise, just return 0
        avg_large_deal = 0

    rep_group['avg_large_deal'] = avg_large_deal

    return rep_group

df_2 = df.groupby('rep').apply(_avg_large_deal)

# Task 3
df_3 = df_2.loc[df_2['total_revenue'] > 15000]

# additions after grading
df_final = df_3.groupby('rep')\
    [['total_revenue', 'num_deals', 'avg_large_deal']].max()




