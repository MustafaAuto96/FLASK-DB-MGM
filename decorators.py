from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def roles_required(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('main.login'))
            if current_user.group not in allowed_roles:
                flash('Access Denied: You do not have permission.', 'danger')
                # Optionally redirect to safe page (home or dashboard)
                return redirect(url_for('main.site_data'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator