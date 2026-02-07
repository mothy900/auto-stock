import shutil
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database():
    """Backs up the antigravity.db file."""
    # Define paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(project_root, "data", "antigravity.db")
    
    if not os.path.exists(db_path):
        logger.warning(f"Database not found at {db_path}. Skipping backup.")
        return

    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"antigravity_backup_{timestamp}.db"
    backup_path = os.path.join(project_root, "data", backup_filename)

    try:
        shutil.copy2(db_path, backup_path)
        logger.info(f"✅ Database backed up successfully to: {backup_path}")
    except Exception as e:
        logger.error(f"❌ Failed to backup database: {e}")
        raise

if __name__ == "__main__":
    backup_database()
