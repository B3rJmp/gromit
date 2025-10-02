from app import db

class LogType(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String, nullable=False)

  logs = db.relationship('Log', backref='log_type', lazy=True)

  def __repr__(self):
    return f"<LogType {self.name}>"
