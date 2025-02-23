from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db():
    from models.user import User
    from models.procurement import Procurement
    from models.audit_log import AuditLog

    db.create_all()