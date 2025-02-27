from app import db
from datetime import datetime

class ServiceView(db.Model):
    __tablename__ = 'service_views'
    
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50))
    service_id = db.Column(db.String(50))
    view_count = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def increment_view(cls, category, service_id):
        view = cls.query.filter_by(category=category, service_id=service_id).first()
        if view:
            view.view_count += 1
            view.last_updated = datetime.utcnow()
        else:
            view = cls(category=category, service_id=service_id, view_count=1)
            db.session.add(view)
        db.session.commit() 