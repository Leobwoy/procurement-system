from app import db
class Procurement(db.Model):
    __tablename__ = 'procurement'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    supplier = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    receiver = db.Column(db.String(100), nullable=False)
    package_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Procurement {self.item_name} from {self.supplier}>"


    
