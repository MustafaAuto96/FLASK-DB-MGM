from flask import (
    Blueprint, render_template, redirect, url_for, request, flash, send_file, current_app
)
from flask_login import login_required, current_user, login_user, logout_user
from io import BytesIO
import pandas as pd
from datetime import datetime
from decorators import roles_required
from extensions import db
from models import Site, ProblemReport, User
from forms import SiteForm, ProblemReportForm, UserForm
from sqlalchemy import or_
from flask import current_app as app

main_bp = Blueprint ('main', __name__)


@main_bp.route ('/')
def index():
    return redirect (url_for ('main.site_data'))


# ===== SITE DATA VIEW =====
@main_bp.route ('/site_data')
@login_required
def site_data():
    search = request.args.get ('search', '', type=str)
    query = Site.query

    if search:
        # Use ilike for case-insensitive partial match on multiple columns
        like_term = f'%{search}%'

        query = query.filter (
            or_ (
                Site.site_location.ilike (like_term),
                Site.device_name.ilike (like_term),
                Site.sdwan_site_id.ilike (like_term),
                Site.lan_ip.ilike (like_term),
                Site.atm_port.ilike (like_term),
                Site.el_isp_info_details.ilike (like_term),
                Site.el_isp_capacity.ilike (like_term),
                Site.el_isp_l2_ip.ilike (like_term),
                Site.ilevant_isp_info_details.ilike (like_term),
                Site.ilevant_isp_capacity.ilike (like_term),
                Site.horizon_isp_info_details.ilike (like_term),
                Site.horizon_isp_capacity.ilike (like_term),
                Site.horizon_isp_l2_ip.ilike (like_term),
            )
        )
    sites = query.all ()
    return render_template ('site_data.html', sites=sites, search=search)


@main_bp.route ('/export_sites')
@login_required
def export_sites():
    sites = Site.query.all ()
    df = pd.DataFrame ([{
        "Site Name": s.site_location,
        "Device Name": s.device_name,
        "SDWAN Site ID": s.sdwan_site_id,
        "LAN IP": s.lan_ip,
        "ATM Port": s.atm_port,
        "EL ISP Info": s.el_isp_info_details,
        "EL Capacity": s.el_isp_capacity,
        "EL L2 IP": s.el_isp_l2_ip,
        "Ilevant ISP Info": s.ilevant_isp_info_details,
        "ILevant Capacity": s.ilevant_isp_capacity,
        "Horizon ISP Info": s.horizon_isp_info_details,
        "Horizon Capacity": s.horizon_isp_capacity,
        "Horizon L2 IP": s.horizon_isp_l2_ip
    } for s in sites])

    output = BytesIO ()
    with pd.ExcelWriter (output, engine='openpyxl') as writer:
        df.to_excel (writer, index=False, sheet_name='Sites')
    output.seek (0)

    return send_file(output, download_name='site_data.xlsx', as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')



@main_bp.route ('/site_data/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required ('Admin', 'Network Team')
def edit_site(id):
    site = Site.query.get_or_404 (id)
    form = SiteForm (obj=site)

    # Manually populate ISP fields from the site model into the form, on GET
    if request.method == 'GET':
        form.el_isp_details.data = site.el_isp_info_details
        form.el_capacity.data = site.el_isp_capacity
        form.el_l2_ip.data = site.el_isp_l2_ip
        form.atm_port.data = site.atm_port
        form.ilevant_isp_details.data = site.ilevant_isp_info_details
        form.ilevant_capacity.data = site.ilevant_isp_capacity
        form.horizon_isp_details.data = site.horizon_isp_info_details
        form.horizon_capacity.data = site.horizon_isp_capacity
        form.horizon_l2_ip.data = site.horizon_isp_l2_ip

    if form.validate_on_submit ():
        # Populate model from form fields
        site.site_location = form.site_location.data
        site.device_name = form.device_name.data
        site.sdwan_site_id = form.sdwan_site_id.data
        site.lan_ip = form.lan_ip.data
        site.atm_port = form.atm_port.data

        site.el_isp_info_details = form.el_isp_details.data
        site.el_isp_capacity = form.el_capacity.data
        site.el_isp_l2_ip = form.el_l2_ip.data

        site.ilevant_isp_info_details = form.ilevant_isp_details.data
        site.ilevant_isp_capacity = form.ilevant_capacity.data

        site.horizon_isp_info_details = form.horizon_isp_details.data
        site.horizon_isp_capacity = form.horizon_capacity.data
        site.horizon_isp_l2_ip = form.horizon_l2_ip.data

        db.session.commit ()
        flash ('Site updated successfully', 'success')
        return redirect (url_for ('main.site_data'))

    return render_template ('submit_site.html', form=form, edit=True)


@main_bp.route ('/site_data/delete/<int:id>', methods=['POST'])
@login_required
@roles_required('Admin', 'Network Team')
def delete_site(id):
    site = Site.query.get_or_404 (id)
    db.session.delete (site)
    db.session.commit ()
    flash ('Site deleted', 'info')
    return redirect (url_for ('main.site_data'))

@main_bp.route('/site_data/clone/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Network Team')
def clone_site(id):
    site = Site.query.get_or_404(id)
    form = SiteForm()

    if request.method == 'GET':
        # Pre-fill form with existing site data for cloning
        form.site_location.data = site.site_location
        form.device_name.data = site.device_name
        form.sdwan_site_id.data = site.sdwan_site_id
        form.lan_ip.data = site.lan_ip
        form.atm_port.data = site.atm_port
        form.el_isp_details.data = site.el_isp_info_details
        form.el_capacity.data = site.el_isp_capacity
        form.el_l2_ip.data = site.el_isp_l2_ip
        form.ilevant_isp_details.data = site.ilevant_isp_info_details
        form.ilevant_capacity.data = site.ilevant_isp_capacity
        form.horizon_isp_details.data = site.horizon_isp_info_details
        form.horizon_capacity.data = site.horizon_isp_capacity
        form.horizon_l2_ip.data = site.horizon_isp_l2_ip

    if form.validate_on_submit():
        # Create new site with form data (clone behavior)
        new_site = Site(
            site_location=form.site_location.data,
            device_name=form.device_name.data,
            sdwan_site_id=form.sdwan_site_id.data,
            lan_ip=form.lan_ip.data,
            atm_port=form.atm_port.data,
            el_isp_info_details=form.el_isp_details.data,
            el_isp_capacity=form.el_capacity.data,
            el_isp_l2_ip=form.el_l2_ip.data,
            ilevant_isp_info_details=form.ilevant_isp_details.data,
            ilevant_isp_capacity=form.ilevant_capacity.data,
            horizon_isp_info_details=form.horizon_isp_details.data,
            horizon_isp_capacity=form.horizon_capacity.data,
            horizon_isp_l2_ip=form.horizon_l2_ip.data,
        )
        db.session.add(new_site)
        db.session.commit()
        flash('Site cloned successfully as new site.', 'success')
        return redirect(url_for('main.site_data'))

    # Pass 'add' mode flag to template for button text and heading
    return render_template('submit_site.html', form=form, edit=False)

@main_bp.route('/site_data/add_to_daily_report/<int:site_id>', methods=['GET'])
@login_required
@roles_required('Admin', 'Network Team', 'NOC Team')
def add_to_daily_report(site_id):
    site = Site.query.get_or_404(site_id)
    # Redirect to daily_problem_report with ?site_id=XX query param to preselect
    return redirect(url_for('main.daily_problem_report', site_id=site.id))


# ===== SUBMIT NEW SITE =====
@main_bp.route ('/submit_site', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Network Team')
def submit_site():
    form = SiteForm ()
    if form.validate_on_submit ():
        new_site = Site (
            site_location=form.site_location.data,
            device_name=form.device_name.data,
            sdwan_site_id=form.sdwan_site_id.data,
            lan_ip=form.lan_ip.data,
            el_isp_info_details=form.el_isp_details.data,
            el_isp_capacity=form.el_capacity.data,
            el_isp_l2_ip=form.el_l2_ip.data,
            ilevant_isp_info_details=form.ilevant_isp_details.data,
            ilevant_isp_capacity=form.ilevant_capacity.data,
            horizon_isp_info_details=form.horizon_isp_details.data,
            horizon_isp_capacity=form.horizon_capacity.data,
            horizon_isp_l2_ip=form.horizon_l2_ip.data,
        )
        db.session.add (new_site)
        db.session.commit ()
        flash ('New site added', 'success')
        return redirect (url_for ('main.site_data'))
    return render_template ('submit_site.html', form=form)


# ===== DAILY PROBLEM REPORT =====
@main_bp.route('/daily_problem_report', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'Network Team', 'NOC Team')
def daily_problem_report():
    form = ProblemReportForm()
    sites = Site.query.order_by('site_location').all()
    form.site_location.choices = [(site.id, site.site_location) for site in sites]

    # Preselect site_location if query param present
    site_id = request.args.get('site_id', type=int)
    if site_id and site_id in [site.id for site in sites]:
        form.site_location.data = site_id

    if form.validate_on_submit():
        report = ProblemReport(
            site_id=form.site_location.data,
            ticket_id=form.ticket_id.data,
            status=form.status.data,
            reason=form.reason.data,
            last_update=form.last_update.data,
            issue_date=form.issue_date.data,
            last_follow_up=form.last_follow_up.data
        )
        db.session.add(report)
        db.session.commit()
        flash('Problem report added', 'success')
        return redirect(url_for('main.daily_problem_report'))

    reports = ProblemReport.query.order_by(ProblemReport.issue_date.desc()).all()
    return render_template('daily_report.html', form=form, reports=reports)


@main_bp.route ('/export_reports')
@login_required
def export_reports():
    # Query all daily problem reports
    reports = ProblemReport.query.all ()

    # Prepare list of dicts for DataFrame
    data = []
    for r in reports:
        data.append ({
            'Site Location': r.site.site_location if r.site else '',
            'Ticket ID': r.ticket_id,
            'Status': r.status,
            'Reason': r.reason or '',
            'Last Update': r.last_update or '',
            'Issue Date': r.issue_date.strftime ('%Y-%m-%d') if r.issue_date else '',
            'Last Follow Up': r.last_follow_up.strftime ('%Y-%m-%d') if r.last_follow_up else ''
        })

    df = pd.DataFrame (data)

    # Create Excel in memory
    output = BytesIO ()
    with pd.ExcelWriter (output, engine='openpyxl') as writer:
        df.to_excel (writer, index=False, sheet_name='Daily Reports')
    output.seek (0)

    # Send file as attachment with proper parameter for Flask>=2.0
    return send_file (
        output,
        download_name='daily_problem_reports.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@main_bp.route ('/daily_problem_report/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'NOC Team')
def edit_report(id):
    report = ProblemReport.query.get_or_404 (id)
    form = ProblemReportForm (obj=report)
    form.site_location.choices = [(site.id, site.site_location) for site in
                                  Site.query.order_by ('site_location').all ()]
    form.site_location.data = report.site_id
    if form.validate_on_submit ():
        report.site_id = form.site_location.data
        report.ticket_id = form.ticket_id.data
        report.status = form.status.data
        report.reason = form.reason.data
        report.last_update = form.last_update.data
        report.issue_date = form.issue_date.data
        report.last_follow_up = form.last_follow_up.data
        db.session.commit ()
        flash ('Problem report updated', 'success')
        return redirect (url_for ('main.daily_problem_report'))
    return render_template ('daily_report.html', form=form, edit=True)


@main_bp.route ('/daily_problem_report/delete/<int:id>', methods=['POST'])
@login_required
@roles_required('Admin', 'NOC Team')
def delete_report(id):
    report = ProblemReport.query.get_or_404 (id)
    db.session.delete (report)
    db.session.commit ()
    flash ('Report deleted', 'info')
    return redirect (url_for ('main.daily_problem_report'))

@main_bp.route('/daily_problem_report/clone/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin', 'NOC Team')
def clone_report(id):
    report = ProblemReport.query.get_or_404(id)
    form = ProblemReportForm()
    form.site_location.choices = [(site.id, site.site_location) for site in Site.query.order_by('site_location').all()]

    if request.method == 'GET':
        form.site_location.data = report.site_id
        form.ticket_id.data = report.ticket_id
        form.status.data = report.status
        form.reason.data = report.reason
        form.last_update.data = report.last_update
        form.issue_date.data = report.issue_date
        form.last_follow_up.data = report.last_follow_up

    if form.validate_on_submit():
        new_report = ProblemReport(
            site_id=form.site_location.data,
            ticket_id=form.ticket_id.data,
            status=form.status.data,
            reason=form.reason.data,
            last_update=form.last_update.data,
            issue_date=form.issue_date.data,
            last_follow_up=form.last_follow_up.data
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Problem report cloned successfully as new report.', 'success')
        return redirect(url_for('main.daily_problem_report'))

    return render_template('daily_report.html', form=form, edit=False)

# ===== ADMIN USER MANAGEMENT =====
@main_bp.route ('/admin', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def admin():
    form = UserForm ()
    users = User.query.all ()
    if form.validate_on_submit ():
        user = User (username=form.username.data, group=form.group.data)
        user.set_password (form.password.data)
        db.session.add (user)
        db.session.commit ()
        flash ('User created successfully', 'success')
        return redirect (url_for ('main.admin'))
    return render_template ('admin.html', form=form, users=users)


@main_bp.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@roles_required('Admin')
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.password.data = ''  # Clear password on GET to avoid pre-fill & browser validation issues

    if form.validate_on_submit():
        app.logger.debug(f"Form data - username: {form.username.data}, password entered: {'YES' if form.password.data else 'NO'}, password length: {len(form.password.data) if form.password.data else 0}, group: {form.group.data}")
        app.logger.debug(f"Raw password field from form: '{request.form.get('password')}'")

        user.username = form.username.data
        user.group = form.group.data

        if form.password.data:
            app.logger.info(f"Updating password for user: {user.username}")
            try:
                user.set_password(form.password.data)
            except Exception as e:
                app.logger.error(f"Error setting password: {e}")
                flash('An error occurred while updating the password.', 'danger')
                return render_template('admin.html', form=form, edit=True, edit_user=user)
        else:
            app.logger.info(f"No password change for user: {user.username}")

        db.session.commit()
        app.logger.info(f"User '{user.username}' updated successfully.")
        flash('User updated successfully', 'success')
        return redirect(url_for('main.admin'))

    if form.errors:
        app.logger.warning(f"Form validation errors: {form.errors}")

    return render_template('admin.html', form=form, edit=True, edit_user=user)


@main_bp.route ('/admin/delete/<int:id>', methods=['POST'])
@login_required
def delete_user(id):
    user = User.query.get_or_404 (id)
    db.session.delete (user)
    db.session.commit ()
    flash ('User deleted', 'info')
    return redirect (url_for ('main.admin'))


# ===== AUTH ROUTES =====
@main_bp.route ('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect (url_for ('main.site_data'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by (username=username).first ()
        if user and user.check_password (password):
            login_user (user)
            flash (f'Welcome back, {user.username}!', 'success')
            return redirect (url_for ('main.site_data'))
        else:
            flash ('Invalid username or password', 'danger')
    return render_template ('login.html')


@main_bp.route ('/logout')
@login_required
def logout():
    logout_user ()
    flash ('You have been logged out', 'info')
    return redirect (url_for ('main.login'))