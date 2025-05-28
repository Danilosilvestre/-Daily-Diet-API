from database import db
import uuid
from datetime import datetime, timezone

now = datetime.now(timezone.utc)

class Meal(db.Model):
    # Id (Int), Name(Str), Description(Str), Data and time(DateTime), is_on_diet(Bool) 
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    date_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    is_on_diet = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)