#!/usr/bin/env python3
"""
Job Tracker LLM - Main Launcher

This is the single entry point for the job tracker application.
"""

import sys
import os
from pathlib import Path

def main():
    """Main entry point that runs the application."""
    # Add src to Python path
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))
    
    # Import and run the main function
    try:
        from job_tracker_llm.unified_cli import main as app_main
        return app_main()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running from the project root directory.")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 