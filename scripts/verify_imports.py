import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    print("Verifying imports...")
    from app.api import routes_relationships
    from app.api import routes_evidence
    from app.api import routes_ingest
    from app.api import routes_exports
    print("All API routes imported successfully.")
except ImportError as e:
    print(f"Import failed: {e}")
    sys.exit(1)
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(1)
