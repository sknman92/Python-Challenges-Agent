# **Challenge: Student Grade Processing Pipeline**

# You work at an edtech company and need to process raw student assessment data using a variety of Python looping and data structure techniques. You are explicitly required to use specific constructs for each task — using the wrong construct (e.g. a for loop where a comprehension is required) counts as an incorrect solution.

# ---

# **Setup — Run this first:**

# ```python
import pandas as pd

raw_records = [
    {"student_id": "S001", "name": "Alice",   "subject": "Math",    "score": 88, "week": 1},
    {"student_id": "S001", "name": "Alice",   "subject": "Science", "score": 72, "week": 1},
    {"student_id": "S001", "name": "Alice",   "subject": "Math",    "score": 95, "week": 2},
    {"student_id": "S002", "name": "Bob",     "subject": "Math",    "score": 60, "week": 1},
    {"student_id": "S002", "name": "Bob",     "subject": "Science", "score": 55, "week": 1},
    {"student_id": "S002", "name": "Bob",     "subject": "Science", "score": 80, "week": 2},
    {"student_id": "S003", "name": "Carol",   "subject": "Math",    "score": 45, "week": 1},
    {"student_id": "S003", "name": "Carol",   "subject": "Science", "score": 90, "week": 2},
    {"student_id": "S003", "name": "Carol",   "subject": "Math",    "score": 70, "week": 2},
    {"student_id": "S004", "name": "David",   "subject": "Science", "score": 33, "week": 1},
    {"student_id": "S004", "name": "David",   "subject": "Math",    "score": 58, "week": 2},
    {"student_id": "S004", "name": "David",   "subject": "Science", "score": 61, "week": 2},
    {"student_id": "S005", "name": "Eva",     "subject": "Math",    "score": 99, "week": 1},
    {"student_id": "S005", "name": "Eva",     "subject": "Science", "score": 87, "week": 2},
    {"student_id": "S005", "name": "Eva",     "subject": "Math",    "score": 95, "week": 2},
]

df = pd.DataFrame(raw_records)

thresholds = {"Math": 65, "Science": 60}
# ```

# ---

# **Task 1 — For Loop + Dictionary Building**

# Using a plain `for` loop (no comprehensions), iterate over `raw_records` and build a nested dictionary called `student_scores` with the following structure:

# ```python
# {
#   "S001": {"name": "Alice", "scores": [88, 72, 95]},
#   "S002": {"name": "Bob",   "scores": [60, 55, 80]},
#   ...
# }
# ```

# Each student's scores list should contain all their scores in the order they appear in `raw_records`. Do not use `defaultdict`.

# ---

# **Task 2 — While Loop: Iterative Score Normalisation**

# Write a `while` loop that repeatedly scales down any student's average score that exceeds 90, by multiplying it by 0.95, until no average exceeds 90. Work from the `student_scores` dict you built in Task 1.

# Store the final normalised averages in a dict called `normalised_averages`:

# ```python
# {"S001": 87.4, "S002": 65.0, ...}  # rounded to 1 decimal place
# ```

# Print how many scaling iterations were required for each student.

# ---

# **Task 3 — List Comprehension: Flagging At-Risk Students**

# Using a **single list comprehension** (no for loops, no filtering after the fact), produce a list called `at_risk` containing the `student_id` of any student whose normalised average (from Task 2) is strictly below 65. The list should be sorted ascending.

# ---

# **Task 4 — Dict Comprehension: Subject Pass Rates**

# Using `iterrows()` on `df` and a plain `for` loop, build an intermediate structure that tracks, per subject, how many scores meet or exceed the subject's threshold (from the `thresholds` dict) vs. total scores recorded.

# Then, using a **dict comprehension**, produce a final dict called `pass_rates`:

# ```python
# {"Math": 71.4, "Science": 66.7}  # percentage, rounded to 1 decimal place
# ```

# ---

# **Task 5 — Nested Loops + Set Comprehension: Weekly Improvement**

# Using **nested for loops**, compare each student's average score in week 2 vs. week 1 (using `raw_records`, not df). A student "improved" if their week 2 average is strictly higher than their week 1 average.

# Then, using a **set comprehension**, produce a set called `improved_students` containing the names (not IDs) of students who improved. Students who have no scores in one of the weeks should be skipped.

# ---

# **Task 6 — Bringing It Together**

# Using any looping construct you consider most appropriate (justify your choice in a comment), produce a final printed report in this format for every student, sorted by `student_id`:

# ```
# === Student Report ===
# S001 | Alice  | Normalised Avg: 87.4 | At Risk: No  | Improved: Yes
# S002 | Bob    | Normalised Avg: 65.0 | At Risk: No  | Improved: Yes
# S003 | Carol  | Normalised Avg: 72.1 | At Risk: No  | Improved: Yes
# S004 | David  | Normalised Avg: 51.0 | At Risk: Yes | Improved: Yes
# S005 | Eva    | Normalised Avg: 87.4 | At Risk: No  | Improved: No
# ```

# ---

# **Constraints & Rules:**
# - Tasks 1 and 2 must use explicit `for` and `while` loops respectively — no comprehensions
# - Tasks 3 and 4 must use comprehensions — no explicit for loops in the final output construction
# - Task 5 nested loops must iterate over `raw_records` directly, not a pre-aggregated DataFrame
# - Do not use `groupby` anywhere in this challenge
# - Do not import any library beyond `pandas`


#----------------------------------------
# TASK 1

# finding unique student ids
student_ids = sorted(set((record.get('student_id', 'No Student ID'), record.get('name')) for record in raw_records))

# nested loop
student_scores = {}
for id, name in student_ids:
    temp_score_list = []
    for record in raw_records:
        if record.get('student_id', 'No Student ID') == id:
            temp_score_list.append(record.get('score'))
        temp_dict = {
            id : {
                'name' : name, 
                'scores' : temp_score_list 
            }
        }

        student_scores.update(temp_dict)
                
# TASK 2
import numpy as np
normalised_averages = {}
for id, record in student_scores.items():
    avg_score = float(np.array((record['scores'])).mean().round(1))
    loop_count = 0
    while avg_score > 90:
        avg_score *= 0.95
        loop_count += 1
    print(f"Student {id} required {loop_count} iterations to normalise their average")
    normalised_averages.update(
        {
            id : avg_score
        }
    )    

# TASK 3
at_risk = {id: score for id, score in normalised_averages.items() if score < 65}

# TASK 4
initial_dict = {
    'Math' : {'Pass' : 0, 'Total' : 0},
    'Science' : {'Pass' : 0, 'Total' : 0}
}
for index, row in df.iterrows():
    threshold_score = thresholds.get(row['subject'])
    subject = row['subject']
    pass_counter = 0
    total_counter = 0
    if row['score'] > threshold_score:
        pass_counter += 1
    total_counter += 1 

    initial_dict[subject]['Pass'] += pass_counter
    initial_dict[subject]['Total'] += total_counter

pass_rate = {}
for subject, counter in initial_dict.items():
    rate = round(((counter['Pass'] / counter['Total'])*100), 1)
    pass_rate.update(
        {
            subject : rate
        }
    )

# TASK 5
temp_list = []
for id, _ in student_ids:
    temp_records = []
    for record in raw_records:
        if record['student_id'] == id:
            temp_records.append(record)
    # does the student have scores in both week 1 and 2
    if len([r for r in temp_records if r['week'] == 1]) > 0 \
        and len([r for r in temp_records if r['week'] == 2]) > 0:
        week1_avg = np.array([r['score'] for r in temp_records if r['week'] == 1]).mean()
        week2_avg = np.array([r['score'] for r in temp_records if r['week'] == 2]).mean()
        improved = week2_avg > week1_avg
        if improved:
            student_name = next(r['name'] for r in temp_records if r['student_id'] == id)
            temp_list.append(student_name)

improved_students = {x for x in temp_list}

# TASK 6
student_profile = []
for id, name in student_ids:
    at_risk
    normalised_averages
    improved_students

    # grabbing normalised averages
    normalised_avg = normalised_averages.get(id)

    # at_risk?
    if at_risk.get(id, 'No') == 'No':
        at_risk_flag = 'No'
    else:
        at_risk_flag = 'Yes'

    # improved?
    if name in improved_students:
        improved_students_flag = 'Yes'
    else:
        improved_students_flag = 'No'

    student_profile.append(
        (id, name, normalised_avg, at_risk_flag, improved_students_flag)
    )

for id, name, normalised_avg, at_risk_flag, improved_students_flag in student_profile:
    print(
        f"{id} | {name} | Normalised Avg: {normalised_avg} | At Risk: {at_risk_flag} | Improved: {improved_students_flag}"
    )



        

        
