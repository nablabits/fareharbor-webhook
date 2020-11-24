"""Define the models in the database."""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class sampleTable(db.Model):
    """Create a sample table in the app to play with."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), unique=False, nullable=True)
    city = db.Column(db.String(200), unique=False, nullable=True)

    def __init__(self, name, city):
        self.name = name
        self.city = city

    def __repr__(self):
        """Set the display options when querying."""
        return "{}-{}".format(self.id, self.name)
