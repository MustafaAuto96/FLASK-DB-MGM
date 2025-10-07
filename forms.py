from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, DateField
from wtforms.validators import DataRequired, Length, IPAddress, Optional


class SiteForm (FlaskForm):
    site_location = StringField ('Site Location Name', validators=[DataRequired ()])
    device_name = StringField ('Device Name', validators=[DataRequired ()])
    sdwan_site_id = StringField ('SDWAN Site ID', validators=[DataRequired ()])
    lan_ip = StringField ('LAN IP', validators=[DataRequired (), IPAddress ()])

    el_isp_details = StringField ('EL ISP Details', validators=[Optional ()])
    el_capacity = StringField ('Capacity', validators=[Optional ()])
    el_l2_ip = StringField ('L2 IP', validators=[Optional (), IPAddress ()])

    ilevant_isp_details = StringField ('ILevant ISP Details', validators=[Optional ()])
    ilevant_capacity = StringField ('Capacity', validators=[Optional ()])

    atm_port = StringField ('ATM Port', validators=[Optional ()])

    horizon_isp_details = StringField ('Horizon ISP Details', validators=[Optional ()])
    horizon_capacity = StringField ('Capacity', validators=[Optional ()])
    horizon_l2_ip = StringField ('L2 IP', validators=[Optional (), IPAddress ()])

    submit = SubmitField ('Add Site')


class ProblemReportForm (FlaskForm):
    site_location = SelectField ('Site Location', coerce=int, validators=[DataRequired ()])
    ticket_id = StringField ('Ticket ID', validators=[DataRequired ()])
    status = SelectField ('Status', choices=[('UP', 'UP'), ('DOWN', 'DOWN')], validators=[DataRequired ()])
    reason = TextAreaField ('Reason', validators=[Optional ()])
    last_update = TextAreaField ('Last Update', validators=[Optional ()])
    issue_date = DateField ('Issue Date', validators=[DataRequired ()])
    last_follow_up = DateField ('Last Follow Up', validators=[DataRequired ()])
    submit = SubmitField ('Add Report')


class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Optional(), Length(min=6)])
    group = SelectField('Group', choices=[('Admin', 'Admin'), ('Network Team', 'Network Team'), ('NOC Team', 'NOC Team')], validators=[DataRequired()])
    submit = SubmitField('Submit')

