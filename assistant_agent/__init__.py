from .agent import assistant_root
from .database import init_db

# Initialize database on module load
init_db()

__all__ = ["assistant_root"]
