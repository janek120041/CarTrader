from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.notifications import bp
from app.models import Notification

@bp.route('/notifications')
@login_required
def notifications():
    # Mark all notifications as read
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).all()
    for notification in unread:
        notification.mark_as_read()
    
    # Get all notifications for the user, ordered by creation date
    notifications = Notification.query.filter_by(user_id=current_user.id)\
        .order_by(Notification.created_at.desc()).all()
    
    return render_template('notifications/notifications.html', 
                         title='Notifications',
                         notifications=notifications)

@bp.route('/notifications/mark_read/<int:id>')
@login_required
def mark_read(id):
    notification = Notification.query.get_or_404(id)
    if notification.user_id != current_user.id:
        flash('You do not have permission to access this notification.', 'danger')
        return redirect(url_for('main.index'))
    
    notification.mark_as_read()
    return redirect(url_for('notifications.notifications'))

@bp.route('/notifications/mark_all_read')
@login_required
def mark_all_read():
    notifications = Notification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).all()
    
    for notification in notifications:
        notification.mark_as_read()
    
    flash('All notifications marked as read.', 'success')
    return redirect(url_for('notifications.notifications')) 