from flask_sqlalchemy import SQLAlchemy

# Initialize db
db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
