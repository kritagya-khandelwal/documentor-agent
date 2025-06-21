# Chapter 3: File Extractor

Welcome back! In the last chapter, we explored the **[Agent Nodes Logic](02_agent_nodes_logic.md)**, the individual functions that power our documentation agent. Now, we're going to focus on a crucial first step: getting the code files into our agent's hands. This is where the **File Extractor** comes in!

## What is the File Extractor? 🤔

Imagine you have a project with many files. Some are important code files, others might be temporary files, configuration files, or large binary files that we don't need for documentation. The File Extractor is like a smart librarian for your code. Its job is to go into a specified folder (your project directory) and carefully select *only* the files that are relevant for documentation.

It's designed to be flexible, allowing you to:

*   **Specify a Directory:** Tell it exactly where to look for files.
*   **Include/Exclude Patterns:** Define rules for which files to grab (e.g., only Python files) and which to ignore (e.g., `.log` files, `venv` directories).
*   **Respect `.gitignore`:** It's smart enough to understand your project's `.gitignore` file, automatically skipping files that you've already told Git to ignore. This is super handy for keeping your documentation focused on your actual code.
*   **Size Limits:** You can even set a maximum file size, so it won't try to read massive files that aren't suitable for documentation.

## Why Do We Need It? 📂

Our documentation agent needs to read your code to understand it. But it can't just blindly read every single file in your project. That would be inefficient and could lead to errors or irrelevant information. The File Extractor acts as a filter, ensuring that only the necessary code files are passed on to the next stages of our workflow.

Think of it as preparing your ingredients before cooking. You wouldn't throw the whole vegetable garden into the pot, right? You select the best, freshest ingredients. The File Extractor does the same for your code files.

## How Does It Work? ⚙️

Let's look at the code that makes the File Extractor work:

```python
# file_extractor.py

import fnmatch
import os
import pathspec

def file_extractor(directory: str, include_patterns: list[str] = [], exclude_patterns: list[str] = [], max_file_size: int = None) -> list:
    """
    Extracts files from a directory based on specified patterns and size constraints.
    ... (rest of the function)
    """
    extracted_files = []
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")
  
    # ... (code to handle .gitignore) ...

    all_files = []
    for root, dirs, files in os.walk(directory):
        # ... (code to handle directory exclusions) ...
        for filename in files:
            filepath = os.path.join(root, filename)
            all_files.append(filepath)

    # ... (loop through all_files to check patterns and size) ...
    for filepath in all_files:
        relpath = os.path.relpath(filepath, directory)

        # --- Exclusion check ---
        excluded = False
        # ... (check against .gitignore and exclude_patterns) ...

        included = False
        # ... (check against include_patterns) ...

        if not included or excluded:
            continue # Skip to next file if not included or excluded

        if max_file_size and os.path.getsize(filepath) > max_file_size:
            continue # Skip large files

        # --- File is being processed ---        
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                content = f.read()
            extracted_files.append({"path": relpath, "content": content})
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")

    return extracted_files
```

**Let's break down the key parts:**

1.  **Importing Libraries:**
    *   `fnmatch`: This is used for matching filenames against patterns (like `*.py`).
    *   `os`: This module provides functions for interacting with the operating system, like walking through directories (`os.walk`) and getting file sizes (`os.path.getsize`).
    *   `pathspec`: This powerful library helps us work with `.gitignore` files and other pattern matching.

2.  **The `file_extractor` Function:**
    *   It takes the `directory`, `include_patterns`, `exclude_patterns`, and `max_file_size` as input.
    *   It first checks if the provided `directory` actually exists.
    *   **`.gitignore` Handling:** It looks for a `.gitignore` file in the specified directory. If found, it reads the patterns from it using `pathspec` to create a filter.
    *   **Walking the Directory:** `os.walk(directory)` is used to go through every file and folder within the `directory`. It's like a recursive search.
    *   **Filtering Files:** For each file found, it performs several checks:
        *   **Exclusion:** It checks if the file's path matches any of the `exclude_patterns` or if it's ignored by the `.gitignore` rules.
        *   **Inclusion:** It checks if the file's path matches any of the `include_patterns`. If no `include_patterns` are given, all files are considered for inclusion by default.
        *   **Size Limit:** If `max_file_size` is set, it checks if the file's size exceeds this limit.
    *   **Reading Content:** If a file passes all the checks (i.e., it's included and not excluded, and within the size limit), its content is read using `f.read()`.
    *   **Storing Results:** The file's relative path and its content are stored in a list called `extracted_files`.

## A Simple Example 🌳

Let's say you have a project structure like this:

```
my_project/
├── src/
│   ├── main.py
│   └── utils.py
├── tests/
│   ├── test_main.py
│   └── test_utils.py
├── data/
│   └── sample.csv
├── .gitignore
└── README.md
```

And your `.gitignore` file contains:

```
*.csv
*.log
venv/
```

If you call `file_extractor('my_project', include_patterns=['*.py'], exclude_patterns=['tests/'])`, here's what would happen:

*   It would look inside `my_project`.
*   It would see `*.py` in `include_patterns`, so it wants Python files.
*   It sees `tests/` in `exclude_patterns`, so it will skip the `tests` directory.
*   It reads `.gitignore` and knows to skip `*.csv` and `*.log` files.

The files that would be extracted are:

*   `src/main.py`
*   `src/utils.py`

The files that would be skipped are:

*   `tests/test_main.py` (because of `exclude_patterns`)
*   `tests/test_utils.py` (because of `exclude_patterns`)
*   `data/sample.csv` (because of `.gitignore`)
*   `README.md` (because it's not a `.py` file and no `include_patterns` were set to catch it)

## What's Next? ➡️

The File Extractor is our gatekeeper, ensuring our agent works with the right data. Now that we know how files are selected, in the next chapter, we'll dive into the **[Pydantic Models](04_pydantic_models.md)**. These are like blueprints that help us structure the data our agent works with, making everything organized and predictable! ✨

---

Generated by Kritagya Khandelwal