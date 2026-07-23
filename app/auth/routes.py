"""
SupportSight Authentication Routes

Login, logout, registration, and password management.
"""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.auth import auth_bp
from app.models.user import User
from app import db
from app.utils.validators import validate_email, validate_username, validate_password


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember', False)

        if not username or not password:
            flash('Please enter both username and password.', 'warning')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()

        if user is None:
            user = User.query.filter_by(email=username).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Contact support.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            user.update_last_login()

            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard.home'))

        flash('Invalid username or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()

        # Validation
        is_valid, error = validate_username(username)
        if not is_valid:
            flash(error, 'warning')
            return render_template('auth/register.html')

        is_valid, error = validate_email(email)
        if not is_valid:
            flash(error, 'warning')
            return render_template('auth/register.html')

        is_valid, error = validate_password(password)
        if not is_valid:
            flash(error, 'warning')
            return render_template('auth/register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'warning')
            return render_template('auth/register.html')

        # Check for existing user
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'warning')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('auth/register.html')

        # Create user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not current_user.check_password(current_password):
            flash('Current password is incorrect.', 'danger')
            return render_template('auth/change_password.html')

        is_valid, error = validate_password(new_password)
        if not is_valid:
            flash(error, 'warning')
            return render_template('auth/change_password.html')

        if new_password != confirm_password:
            flash('New passwords do not match.', 'warning')
            return render_template('auth/change_password.html')

        if current_password == new_password:
            flash('New password must be different from current password.', 'warning')
            return render_template('auth/change_password.html')

        current_user.set_password(new_password)
        db.session.commit()

        flash('Password changed successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/change_password.html')


@auth_bp.route('/forgot-password')
def forgot_password():
    """Forgot password page (placeholder)."""
    flash('Password reset functionality coming soon.', 'info')
    return redirect(url_for('auth.login'))
