"""
Database Optimization Migration
- Adds file_path column to email_attachments
- Makes encrypted_content nullable
- Removes html_body column from emails (optional)
"""

from qmail.app import create_app
from qmail.models.database import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate():
    """Run database optimization migration"""
    app = create_app()
    
    with app.app_context():
        logger.info("Starting database optimization migration...")
        
        # Step 1: Add file_path column to email_attachments
        try:
            with db.engine.connect() as conn:
                conn.execute(db.text('ALTER TABLE email_attachments ADD COLUMN file_path VARCHAR(500)'))
                conn.commit()
            logger.info("✓ Added file_path column to email_attachments")
        except Exception as e:
            logger.warning(f"file_path column may already exist: {e}")
        
        # Step 2: Make encrypted_content nullable (for large files stored on disk)
        try:
            with db.engine.connect() as conn:
                # SQLite doesn't support ALTER COLUMN, so we skip this for SQLite
                if 'sqlite' not in str(db.engine.url):
                    conn.execute(db.text('ALTER TABLE email_attachments ALTER COLUMN encrypted_content DROP NOT NULL'))
                    conn.commit()
                    logger.info("✓ Made encrypted_content nullable")
                else:
                    logger.info("⊘ SQLite doesn't need this change (TEXT is already nullable)")
        except Exception as e:
            logger.warning(f"encrypted_content may already be nullable: {e}")
        
        # Step 3: Remove html_body column from emails (optional - commented out for safety)
        # Uncomment if you want to remove this column completely
        # try:
        #     with db.engine.connect() as conn:
        #         conn.execute(db.text('ALTER TABLE emails DROP COLUMN html_body'))
        #         conn.commit()
        #     logger.info("✓ Removed html_body column from emails")
        # except Exception as e:
        #     logger.warning(f"html_body column may not exist: {e}")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Database optimization migration complete!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Create attachments directory: mkdir -p instance/attachments")
        logger.info("2. Restart your application")
        logger.info("3. Test sending emails with attachments")
        logger.info("\nSee DATABASE_OPTIMIZATION.md for more details.")

if __name__ == '__main__':
    migrate()
