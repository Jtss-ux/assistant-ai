import sys
import os

# Add relevant paths to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), "assistant_agent"))

try:
    from assistant_agent.deterministic_agent import run_deterministic_query
    print("✅ SUCCESS: run_deterministic_query imported successfully.")
except ImportError as e:
    print(f"❌ FAIL: {e}")
except Exception as e:
    print(f"⚠️  OTHER ERROR: {e}")
