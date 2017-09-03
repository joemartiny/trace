# -*- coding: utf-8 -*-
import request
from app import app,csrf,login_manager
from flask import render_template, request, redirect, url_for, flash, abort, g, jsonify, make_response, session
from .forms import RegistrationForm, LoginForm, EmailForm, PasswordForm, CompleteForm
from .models import User, PrivateDetails
from app import db
from flask_login import login_required, current_user, login_user,  logout_user
from .security import generate_confirmation_token, confirm_token,generate_recovery_token,confirm_recovery_token,\
    resend_confirmation_token, confirm_resend_confirmation_token
from .email import send_email
from sqlalchemy.exc import IntegrityError
from functools import wraps
# from functionality import sendOneTimeMail
from werkzeug.security import generate_password_hash, check_password_hash
import random
import socket
import re
        
  
@login_manager.user_loader
def user_loader(user_id):
    """ This sets the callback for reloading a user from the session. The
        function you set should take a user ID (a ``unicode``) and return a
        user object, or ``None`` if the user does not exist."""
    return User.query.get(int(user_id))
  
def validate_(type,value):
    if type=="username":

        if re.match("(\S+)([A-z]+)([0-9]*)([-_]*)",value):
            print re.match("(\S+)([A-z]+)([0-9]*)([-_]*)",value)
            return True
        else:
            print re.match("/^(\S+)([A-z]+)([0-9]*)([-_]*)$/g",value)
            return False

    elif type=="password":
        if re.match("(\S+)",value):
            return True
        else:
            print re.match("(\S+)",value)
            return False

    elif type=="email":
        if re.match("([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+",value):
            return True
        else:
            print re.match("([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+",value)
            return False


def generateOneTimePassword():
    
    return generate_password_hash(str(random.random()))[20:26]
 
def sendOneTimeMail(user):

        gP=generateOneTimePassword()
        print user

        html = render_template('one_password_mail.html', one_time_password=gP)

        subject = 'Paymiumm: Your one-time password'

        try:

            send_email(user, subject, html)

            return str(gP)

        except Exception,e:
            print e
            return False

        except socket.gaierror,e:
            print e
            return False




@app.route('/')
# @login_required
# @complete_registration
def index():
    return jsonify({
        'code': 200,
        'status': 'okay',
        'random': generateOneTimePassword()
    })





@app.route("/generatePasswordToken", methods=['POST'])
@csrf.exempt
def generatePasswordToken():

    #get all json keys from request
    req_json=request.get_json()

    #check if value passed was a username or email
    if validate_("username",req_json['usr']) or validate_("email",req_json['usr']):
        user = User.query.filter_by(username=req_json['usr']).first()
        user_mail = User.query.filter_by(email=req_json['usr']).first()


        if user is not None:
            #if passed data is a validated username then get the email
            # user.email
            if user.email_confirmed:
                try:
                    res=sendOneTimeMail(user.email)
                    if res!=False:

                        # users=User.query.filter_by(username=req_json['usr'])
                        user.password_hash=res
                        db.session.commit()
                        print "username password change is done"
                        return make_response(jsonify({'res':'success'}))

                    else:
                        print "error in connection"
                        print make_response(jsonify({'res':'error'}))
                        return make_response(jsonify({'res':'error'}))
                except:
                        print "error in occured"
                        return make_response(jsonify({'res':'error'}))

            else:
                return make_response(jsonify({'res':'unconfirmed'}))



        elif user_mail is not None:

            if user_mail.email_confirmed:
                res=sendOneTimeMail(user_mail)

                try:
                    if res is not False:

                        user_mail.password_hash=res
                        db.session.commit()
                        print "email password change is done"
                        return make_response(jsonify({'res':'success'}))

                    else:

                        return make_response(jsonify({'res':"error"}))
                except:
                        print "error in occured"
                        return make_response(jsonify({'res':'error'}))

            else:
                return make_response(jsonify({'res':'unconfirmed'}))
                
        else:
            return make_response(jsonify({'res':"invalid"}))
    
    else:
        print "opps"
        return make_response(jsonify({'res':"invalid"}))


@app.route("/login", methods=['POST'])
@csrf.exempt
def login():

    #get all json keys from request
    req_json=request.get_json()

    #check if value passed was a username or email
    if validate_("username",req_json['usr']) or validate_("email",req_json['usr']) and validate_("password",req_json['pwd']):
        user = User.query.filter_by(username=req_json['usr']).first()
        user_mail = User.query.filter_by(email=req_json['usr']).first()
        # print req_json['usr']


        if user is not None and user.password_hash==req_json['pwd']:
            #if passed data is a validated username then get the email
            # user.email
                    if user.email_confirmed and user.account_confirmed:

                        # print "\n\n"+request.form['remember']+"\n\n"
                        print "true"
                        login_user(user,remember=True)
                        
                        user.password_hash=""
                        db.session.commit()
                        return make_response(jsonify({'res':'true'}))

                        #  return redirect(request.args.get('next') or url_for('index'))
                    elif  user.email_confirmed and not user.account_confirmed:

                        print "aunconfirmed"
                        login_user(user,remember=True)
                        
                        return make_response(jsonify({'res':'accountUnconfirmed'}))

                    print "unconfirmed"
                    return make_response(jsonify({'res':"unconfirmed"}))
                    #  flash('Mail not configured')

        elif user_mail is not None and user_mail.password_hash==req_json['pwd']:
                    print req_json['usr']

                    if user_mail.email_confirmed and user_mail.account_confirmed:

                        # print "\n\n"+request.form['remember']+"\n\n"
                        print "true"
                        login_user(user_mail,remember=True)
                        

                        user_mail.password_hash=""
                        db.session.commit()
                        return make_response(jsonify({'res':'true'}))
                        #  return redirect(request.args.get('next') or url_for('index'))
                    elif  user_mail.email_confirmed and not user_mail.account_confirmed:

                        print "aunconfirmed"
                        login_user(user_mail,remember=True)
                        return make_response(jsonify({'res':"accountUnconfirmed"}))

                    print "unconfirmed"
                    return make_response(jsonify({'res':"unconfirmed"}))
                    #  flash('Mail not configured')

        else:
            print "false"
            return make_response(jsonify({'res':"false"}))

    else:
        print "false"
        return make_response(jsonify({'res':"false"}))



