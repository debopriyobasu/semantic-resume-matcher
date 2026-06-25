from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from alembic import command
from alembic.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("bootstrap")


def run_migrations() -> None:
    logger.info("Running database migrations via Alembic...")
    alembic_cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    command.upgrade(alembic_cfg, "head")
    logger.info("Database migrations completed successfully.")


def main() -> None:
    try:
        # 1. Run migrations
        run_migrations()

        # 2. Import jobs
        logger.info("Importing job postings from CSV...")
        from scripts.import_jobs import main as import_jobs_main
        import_jobs_main()

        # 3. Embed jobs
        logger.info("Generating embeddings for job postings...")
        from scripts.embed_jobs import main as embed_jobs_main
        embed_jobs_main()

        logger.info("Bootstrap complete!")
    except Exception as e:
        logger.error("Bootstrap process failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
