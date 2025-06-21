import fnmatch
import os
import pathspec


def file_extractor(directory: str, include_patterns: list[str] = [], exclude_patterns: list[str] = [], max_file_size: int = None) -> list:
    """
    Extracts files from a directory based on specified patterns and size constraints.

    Args:
        directory (str): The directory to extract files from.
        include_patterns (list[str]): List of patterns to include in the files extraction.
        exclude_patterns (list[str]): List of patterns to exclude from the files extraction.
        max_file_size (int): Maximum size of the files to extract.

    Returns:
        list: A list of files. [{"path": "file/relative/path", "content": "content/code written in the file"}]
    """

    extracted_files = []
    if not os.path.isdir(directory):
        raise ValueError(f"Directory does not exist: {directory}")
  
    gitignore_path = os.path.join(directory, ".gitignore")
    gitignore_spec = None
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, "r", encoding="utf-8-sig") as f:
                gitignore_patterns = f.readlines()
            gitignore_spec = pathspec.PathSpec.from_lines("gitwildmatch", gitignore_patterns)
            print(f"Loaded .gitignore patterns from {gitignore_path}")
        except Exception as e:
            print(f"Warning: Could not read or parse .gitignore file {gitignore_path}: {e}")
  
    all_files = []
    for root, dirs, files in os.walk(directory):
        excluded_dirs = set()
        for d in dirs:
            dirpath_rel = os.path.relpath(os.path.join(root, d), directory)

            if gitignore_spec and gitignore_spec.match_file(dirpath_rel):
                excluded_dirs.add(d)
                continue

            if exclude_patterns:
                for pattern in exclude_patterns:
                    if fnmatch.fnmatch(dirpath_rel, pattern) or fnmatch.fnmatch(d, pattern):
                        excluded_dirs.add(d)
                        break

        for d in dirs.copy():
            if d in excluded_dirs:
                dirs.remove(d)

        for filename in files:
            filepath = os.path.join(root, filename)
            all_files.append(filepath)

    total_files = len(all_files)
    processed_files = 0

    for filepath in all_files:
        relpath = os.path.relpath(filepath, directory)

        # --- Exclusion check ---
        excluded = False
        if gitignore_spec and gitignore_spec.match_file(relpath):
            excluded = True

        if not excluded and exclude_patterns:
            for pattern in exclude_patterns:
                if fnmatch.fnmatch(relpath, pattern):
                    excluded = True
                    break

        included = False
        if include_patterns:
            for pattern in include_patterns:
                if fnmatch.fnmatch(relpath, pattern):
                    included = True
                    break
        else:
            included = True

        processed_files += 1 # Increment processed count regardless of inclusion/exclusion

        status = "processed"
        if not included or excluded:
            status = "skipped (excluded)"
            # Print progress for skipped files due to exclusion
            if total_files > 0:
                percentage = (processed_files / total_files) * 100
                rounded_percentage = int(percentage)
                print(f"\033[92mProgress: {processed_files}/{total_files} ({rounded_percentage}%) {relpath} [{status}]\033[0m")
            continue # Skip to next file if not included or excluded

        if max_file_size and os.path.getsize(filepath) > max_file_size:
            status = "skipped (size limit)"
            # Print progress for skipped files due to size limit
            if total_files > 0:
                percentage = (processed_files / total_files) * 100
                rounded_percentage = int(percentage)
                print(f"\033[92mProgress: {processed_files}/{total_files} ({rounded_percentage}%) {relpath} [{status}]\033[0m")
            continue # Skip large files

        # --- File is being processed ---        
        try:
            with open(filepath, "r", encoding="utf-8-sig") as f:
                content = f.read()
            extracted_files.append({"path": relpath, "content": content})
        except Exception as e:
            print(f"Warning: Could not read file {filepath}: {e}")
            status = "skipped (read error)"

        # --- Print progress for processed or error files ---
        if total_files > 0:
            percentage = (processed_files / total_files) * 100
            rounded_percentage = int(percentage)
            print(f"\033[92mProgress: {processed_files}/{total_files} ({rounded_percentage}%) {relpath} [{status}]\033[0m")

    return extracted_files 