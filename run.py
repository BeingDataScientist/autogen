"""
Convenience script to run the orchestrator from project root
"""

# Apply typing patch for Python 3.9.0 compatibility (not needed for Python 3.12.3+)
try:
    import airline_orchestrator.typing_patch
except ImportError:
    pass

from airline_orchestrator.main import main

if __name__ == "__main__":
    main()

