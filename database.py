from app import app, db
from models import User, Procurement, AuditLog

# Create the database tables
def create_tables():
    with app.app_context():
     db.create_all()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
