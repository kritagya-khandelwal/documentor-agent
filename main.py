#!/usr/bin/env python3
"""
Documentor Agent - An AI agent that analyzes codebases and generates comprehensive documentation.

This module provides a simple interface to use the documentor agent for generating
tutorial documentation from any codebase.
"""

import os
from dotenv import load_dotenv

from file_extractor import file_extractor
from educator_agent import educator_agent


def main():
    """Main function to demonstrate the documentor agent."""
    print("Documentor Agent - Codebase Documentation Generator")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv(override=True)
    
    # Check if API key is available
    if not os.getenv("GOOGLE_API_KEY"):
        print("Warning: GOOGLE_API_KEY not found in environment variables.")
        print("Please set your Google API key in a .env file or environment variable.")
        return
    
    # Example usage
    print("Example: Analyzing a sample project...")
    
    # You can replace this with any directory path
    project_directory = "/path/to/your/project"
    
    if not os.path.exists(project_directory):
        print(f"Project directory not found: {project_directory}")
        print("Please update the project_directory variable in main.py")
        return
    
    try:
        # Extract files from the project
        print("Extracting files from project...")
        files = file_extractor(directory=project_directory)
        print(f"Extracted {len(files)} files")
        
        # Run the educator agent
        print("Running educator agent...")
        output_state = educator_agent.invoke({
            "files": files, 
            "project_name": "Sample Project", 
            "max_components": 5
        })
        
        print("Documentation generated successfully!")
        print(f"Output directory: {output_state.get('output_path', 'docs/')}")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
