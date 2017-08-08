# -*- coding: utf-8 -*-
import request
from app import app
from flask import render_template, request, redirect, url_for, flash, abort, g, jsonify, make_response
from .forms import RegistrationForm
from .models import User, PrivateDetails
from app import db
from flask_login import login_required, current_user, login_user,  logout_user
from .security import generate_confirmation_token, confirm_token
from .email import send_email
from sqlalchemy.exc import IntegrityError


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html'), 500


# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         return jsonify({
#             'msg': 'User already logged in',
#             'url': '/'
#             })
#     else:
#         return jsonify({
#             'msg': 'User not logged in',
#             'url': '/login'
#         })

@app.route('/')
@login_required
def index():
    return jsonify({'code': 200,'status': True})


@app.route('/gen_tk')
# @csrf.exempt
def gen_tk():  
    form=RegistrationForm()
    print form.csrf_token
    return form.csrf_token


@app.route('/signup', methods=['POST'])
def signup():
        user = User(full_name=request.form['name'], email=request.form['email'], username=request.form['usr'], password=request.form['pwd'],phone_number=request.form['phn'])
        try:
            db.session.add(user)
            db.session.commit()

        except IntegrityError:
            db.session.rollback()
            return "false"

        token = generate_confirmation_token(user.email)

        confirm_url = url_for('confirm_email', token=token, _external=True)

        html = render_template('activate.html', confirm_url=confirm_url)

        subject = 'Please confirm your Email'

        send_email(user.email, subject, html)

        return "true"


@app.route('/confirm/<token>')
def confirm_email(token):
    """
     the try ... except bit at the beginning to check that the token is valid.
      The token contains a timestamp, so we can tell ts.loads() to raise an exception if it is older than max_age.
      In this case, we’re setting max_age to 86400 seconds, i.e. 24 hours.
    :param token:
    :return:
    """
    try:
        email = confirm_token(token)
    except Exception as e:
        return jsonify({
            'msg': 'The confirmation link is invalid or has expired, danger',
            'status': False,
            'code': 404
        })
        # flash('The confirmation link is invalid or has expired.', 'danger')
        #  abort(404)

    user = User.query.filter_by(email=email).first()
    if user.email_confirmed:
        return jsonify(message='Email has already benn confirmed please login')
    # flash('Email has already been confirmed Please login')
    else:
        user.email_confirmed = True
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'status': True,
            'msg': 'Your email has been confirmed',
            'url': '/login'
        })
    return redirect(url_for('login'))



@app.route('/login', methods=['POST'])
def login():

        user = User.query.filter_by(username=request.form['usr']).first()
        if user is not None and user.verify_password(request.form['pwd']):
            if user.email_confirmed:
                login_user(user, True)
                return "true"
            else:
                return "unconfirmed"

        else:
            return "false"
            # return redirect(request.args.get('next') or url_for('index'))
        

    # return render_template('login.html', form=form)


@app.route('/reset/password', methods=['POST'])
def reset():
    form = EmailForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user.email_confirmed:
            subject = 'Password reset requested'
            token = generate_confirmation_token(user.email)
            recover_url = url_for('reset_with_token', token=token, _external=True)
            html = render_template('recover.html', recover_url=recover_url)
            send_email(user.email, subject, html)
            flash('A confirmation link to reset your password has been sent to you')
            return redirect(url_for('login'))
        else:
            flash('This Email hasnt been confirmed yet')
            return 'Email not confirmed'

    return render_template('reset.html', form=form)


@app.route('/reset/<token>')
def reset_with_token(token):
    try:
        email = confirm_token(token, expiration=3600)

    except Exception as e:
        flash('The confirmation link is invalid or has expired.', 'danger')
        abort(400)
    form = PasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        user = form.password.data

        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({
        'msg': 'You have been logged out',
        'url': '/login'
    })
