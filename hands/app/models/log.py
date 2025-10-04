from app import db

class Log(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
  log_type_id = db.Column(db.Integer, db.ForeignKey('log_type.id'), nullable=False)
  description = db.Column(db.String(100), nullable=False)
  timestamp = db.Column(db.DateTime, server_default=db.func.now())

  log_type = db.relationship("LogType", backref="log")

  def __repr__(self):
    return f"<Log {self.description}>"
