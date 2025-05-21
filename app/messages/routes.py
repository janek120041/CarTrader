from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app import db
from app.messages import bp
from app.models import User, Message

@bp.route('/send/<int:recipient_id>', methods=['GET', 'POST'])
@login_required
def send(recipient_id):
    recipient = User.query.get_or_404(recipient_id)
    
    if recipient == current_user:
        flash('You cannot send a message to yourself.', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            message = Message(
                sender_id=current_user.id,
                recipient_id=recipient_id,
                content=content
            )
            db.session.add(message)
            db.session.commit()
            flash('Your message has been sent.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Message content cannot be empty.', 'error')
    
    return render_template('messages/send.html', recipient=recipient) 