# **Challenge: Build Your First FastAPI App — A Simple Book Info API**

# You're going to build a tiny REST API that serves information about books. This will cover the core basics of FastAPI.

# **Setup (install if needed):**
# ```
# pip install fastapi uvicorn
# ```

# **Your Tasks:**

# 1. Create a FastAPI app instance.

# 2. Define a **GET** endpoint at `/` that returns a welcome message like:
#    `{"message": "Welcome to the Book API!"}`

# 3. Define a **GET** endpoint at `/book` that returns a hardcoded dictionary with info about a single book:

# The book data your endpoint should return
book = {
    "title": "The Hitchhiker's Guide to the Galaxy",
    "author": "Douglas Adams",
    "year": 1979,
    "genre": "Science Fiction"
}

# 4. Define a **GET** endpoint at `/book/summary` that returns only the `title` and `author` fields from the book above (not the full dictionary).

# 5. Run your app using `uvicorn` and test all three endpoints in your browser at `http://127.0.0.1:8000`.

# **Bonus:** Visit `http://127.0.0.1:8000/docs` — what do you see? This is one of FastAPI's best built-in features. No extra work needed, just explore it!

# **How to run your app (once your file is ready):**
# ```
# uvicorn your_filename:app --reload
# ```

# **What you'll learn:**
# - How to create a FastAPI app instance
# - How to define a route using a decorator (`@app.get(...)`)
# - How Python functions become API endpoints
# - How FastAPI automatically converts dictionaries to JSON responses
# - How FastAPI auto-generates interactive API documentation

# Keep your entire solution in a single `.py` file. Good luck!

# ---

# Take your time building it — when you're ready, give me the **file path** to your solution and I'll grade it for you! 🚀


# Task 1
from fastapi import FastAPI
app = FastAPI()

# Task 2
@app.get("/")
def read_root():
    return {"message":"Welcome to the Book API"}

# task 3
@app.get("/book")
def get_book():
    return book

# task 4
@app.get("/book/summary")
def author_title():
    return [{"title" : book.get('title', '')}, {"author" : book.get('author', '')}]

# Task 5
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("BuildYourFirstFASTAPIApp:app", host="127.0.0.1", port=8000, reload=True)






