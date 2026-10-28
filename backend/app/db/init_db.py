import os
import yaml
from sqlalchemy.orm import Session
from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.db.models import User, RiskRule
from app.core.security import get_password_hash
from app.core.config import settings
from app.core.logging import logger


def init_db(db: Session) -> None:
    # 1. Create tables
    Base.metadata.create_all(bind=engine)

    # 2. Seed Admin User
    admin = db.query(User).filter(User.email == settings.SEED_ADMIN_EMAIL.lower()).first()
    if not admin:
        admin = User(
            email=settings.SEED_ADMIN_EMAIL.lower(),
            hashed_password=get_password_hash(settings.SEED_ADMIN_PASSWORD),
            full_name="ClauseGuard Administrator",
            role="admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        logger.info(f"Seeded admin user: {settings.SEED_ADMIN_EMAIL}")

    # 3. Seed Risk Rules from YAML
    yaml_path = os.path.join(os.path.dirname(__file__), "..", "config", "rules.yaml")
    if os.path.exists(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            rules = data.get("rules", [])
            for r in rules:
                existing_rule = db.query(RiskRule).filter(RiskRule.rule_code == r["rule_code"]).first()
                if not existing_rule:
                    rule_entry = RiskRule(
                        rule_code=r["rule_code"],
                        category=r["category"],
                        severity=r["severity"],
                        points=r["points"],
                        pattern_type=r["pattern_type"],
                        pattern_value=r["pattern_value"],
                        reason=r["reason"],
                        suggestion=r.get("suggestion", ""),
                        is_enabled=r.get("is_enabled", True)
                    )
                    db.add(rule_entry)
            db.commit()
            logger.info(f"Loaded {len(rules)} risk rules into database.")


if __name__ == "__main__":
    db = SessionLocal()
    init_db(db)
    db.close()
