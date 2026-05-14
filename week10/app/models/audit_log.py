from datetime import datetime, timezone
import json

from ..extensions import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, index=True)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(255))
    details = db.Column(db.Text)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user = db.relationship('User', backref='audit_logs')

    def set_details(self, details):
        self.details = json.dumps(details or {}, ensure_ascii=False)

    def get_details(self):
        if not self.details:
            return {}

        try:
            return json.loads(self.details)
        except json.JSONDecodeError:
            return {}

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "status": self.status,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "details": self.get_details(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
