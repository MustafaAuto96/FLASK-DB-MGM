from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_location = db.Column(db.String(120), nullable=False)
    device_name = db.Column(db.String(120), nullable=False)
    sdwan_site_id = db.Column(db.String(120), nullable=False)
    lan_ip = db.Column(db.String(45), nullable=False)

    # ISP fields stored as JSON or you can split into multiple columns
    el_isp_info_details = db.Column(db.String(255))
    el_isp_capacity = db.Column(db.String(50))
    el_isp_l2_ip = db.Column(db.String(45))

    ilevant_isp_info_details = db.Column(db.String(255))
    ilevant_isp_capacity = db.Column(db.String(50))

    atm_port = db.Column (db.String (100))

    horizon_isp_info_details = db.Column(db.String(255))
    horizon_isp_capacity = db.Column(db.String(50))
    horizon_isp_l2_ip = db.Column(db.String(45))

    @property
    def el_isp_capacity_mbps(self):
        if self.el_isp_capacity and not self.el_isp_capacity.strip ().lower ().endswith ('mbps'):
            return f"{self.el_isp_capacity.strip ()} Mbps"
        return self.el_isp_capacity or ''

    @property
    def ilevant_isp_capacity_mbps(self):
        if self.ilevant_isp_capacity and not self.ilevant_isp_capacity.strip ().lower ().endswith ('mbps'):
            return f"{self.ilevant_isp_capacity.strip ()} Mbps"
        return self.ilevant_isp_capacity or ''

    @property
    def horizon_isp_capacity_mbps(self):
        if self.horizon_isp_capacity and not self.horizon_isp_capacity.strip ().lower ().endswith ('mbps'):
            return f"{self.horizon_isp_capacity.strip ()} Mbps"
        return self.horizon_isp_capacity or ''

class ProblemReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=False)
    ticket_id = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(10), nullable=False)  # UP or DOWN
    reason = db.Column(db.Text, nullable=True)
    last_update = db.Column(db.Text, nullable=True)
    issue_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    last_follow_up = db.Column(db.Date, nullable=False, default=datetime.utcnow)

    site = db.relationship('Site', backref=db.backref('problem_reports', lazy=True))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    group = db.Column(db.String(50), nullable=False)  # Admin, Network Team, NOC Team etc

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)