from app import db

class LogType(db.Model):
  __tablename__ = "log_type"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

  def __repr__(self):
    return f"<LogType {self.name}>"
