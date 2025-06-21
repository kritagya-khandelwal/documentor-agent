#!/usr/bin/env python3
"""
Command Line Interface for the Documentor Agent.
"""

import argparse
import os
import sys
from dotenv import load_dotenv

from file_extractor import file_extractor
from educator_agent import educator_agent


def main():
    """CLI main function."""
    parser = argparse.ArgumentParser(
        description="Documentor Agent - Generate comprehensive documentation for any codebase"
    )
    parser.add_argument(
        "directory",
        help="Path to the project directory to analyze"
    )
    parser.add_argument(
        "--project-name",
        default=None,
        help="Name of the project (defaults to directory name)"
    )
    parser.add_argument(
        "--max-components",
        type=int,
        default=5,
        help="Maximum number of components to identify (default: 5)"
    )
    parser.add_argument(
        "--include-patterns",
        nargs="*",
        default=[],
        help="File patterns to include (e.g., '*.py' '*.js')"
    )
    parser.add_argument(
        "--exclude-patterns",
        nargs="*",
        default=[],
        help="File patterns to exclude (e.g., '*.pyc' 'node_modules/*')"
    )
    parser.add_argument(
        "--max-file-size",
        type=int,
        default=None,
        help="Maximum file size in bytes to process"
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching of LLM responses"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your Google API key in a .env file or environment variable.")
        sys.exit(1)
    
    # Validate directory
    if not os.path.exists(args.directory):
        print(f"Error: Directory does not exist: {args.directory}")
        sys.exit(1)
    
    if not os.path.isdir(args.directory):
        print(f"Error: Path is not a directory: {args.directory}")
        sys.exit(1)
    
    # Set project name if not provided
    project_name = args.project_name or os.path.basename(os.path.abspath(args.directory))
    
    try:
        print(f"Documentor Agent - Analyzing: {project_name}")
        print("=" * 60)
        
        # Extract files from the project
        print("Extracting files from project...")
        files = file_extractor(
            directory=args.directory,
            include_patterns=args.include_patterns,
            exclude_patterns=args.exclude_patterns,
            max_file_size=args.max_file_size
        )
        print(f"✓ Extracted {len(files)} files")
        
        if len(files) == 0:
            print("Warning: No files were extracted. Check your include/exclude patterns.")
            sys.exit(1)
        
        # Run the educator agent
        print("Running educator agent...")
        output_state = educator_agent.invoke({
            "files": files, 
            "project_name": project_name, 
            "max_components": args.max_components,
            "use_cache": not args.no_cache
        })
        
        print("✓ Documentation generated successfully!")
        print(f"📁 Output directory: {output_state.get('output_path', 'docs/')}")
        print(f"📊 Components identified: {len(output_state.get('components', []))}")
        print(f"📝 Chapters generated: {len(output_state.get('pages', []))}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 