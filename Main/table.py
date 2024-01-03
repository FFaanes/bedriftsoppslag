
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    company_number = db.Column(db.Integer, nullable=False, unique=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_email = db.Column(db.String(50), nullable=False)
    register_date = db.Column(db.String(30), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    permission = db.Column(db.Integer)