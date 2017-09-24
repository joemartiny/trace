# -*- coding: utf-8 -*-
import os
# import request
from paymiummApp_server import app,csrf,login_manager,twilio_client
from flask import render_template, request, redirect, url_for, flash, abort, g, jsonify, make_response, session
from forms import RegistrationForm, LoginForm, EmailForm, PasswordForm, CompleteForm
from models import User, PrivateDetails
from paymiummApp_server import db
from flask_login import login_required, current_user, login_user,  logout_user
from security import generate_confirmation_token, confirm_token,generate_recovery_token,confirm_recovery_token,\
    resend_confirmation_token, confirm_resend_confirmation_token
from email import send_email
from sqlalchemy.exc import IntegrityError
from functools import wraps
# from functionality import sendOneTimeMail
from werkzeug.security import generate_password_hash, check_password_hash
import random
import socket
import re
import datetime
import threading

 
states=['ABIA',
    'ADAMAWA',
    'AKWA IBOM',
    'ANAMBRA',
    'BAUCHI',
    'BAYELSA',
    'BENUE',
    'BORNO',
    'CROSS RIVER',
    'DELTA',
    'EBONYI',
    'EDO',
    'EKITI',
    'ENUGU',
    'GOMBE',
    'IMO',
    'JIGAWA',
    'KADUNA',
    'KANO',
    'KATSINA',
    'KEBBI',
    'KOGI',
    'KWARA',
    'LAGOS',
    'NASSARAWA',
    'NIGER',
    'OGUN',
    'ONDO',
    'OSUN',
    'OYO',
    'PLATEAU',
    'RIVERS',
    'SOKOTO',
    'TARABA',
    'YOBE',
    'ZAMFARA',
    'State']

  
@login_manager.user_loader
def user_loader(user_id):
    """ This sets the callback for reloading a user from the session. The
        function you set should take a user ID (a ``unicode``) and return a
        user object, or ``None`` if the user does not exist."""
    return User.query.get(int(user_id))
  
def  activateMail(email):
        try:
            token = generate_confirmation_token(email)
            html = render_template('activate.html', confirm_url='http://127.0.0.1:8000/account/confirMail/'+token,email='http://127.0.0.1:8000/account/resendConfirmation?email='+email)

            subject = 'Paymiumm: Confirm Your Account'

            send_email(email, subject, html)
            return True        
        except Exception,e:
            print e
            return False

        except socket.gaierror,e:
            print e
            return False


def  resend_activateMail(email=""):

        try:
            token = resend_confirmation_token(email)
            html = render_template('activate.html', confirm_url='http://127.0.0.1:8000/account/confirMail/'+token,email='http://127.0.0.1:8000/account/resendConfirmation?email='+email)

            subject = 'Paymiumm: Confirm Your Account'

            send_email(email, subject, html)
        except Exception,e:
            print e
            return False

        except socket.gaierror,e:
            print e
            return False
  


def validate_(type,value):
    if type=="username":

        if re.match("(\S+)([A-z]+)([0-9]*)([-_]*)",value):
            print re.match("(\S+)([A-z]+)([0-9]*)([-_]*)",value)
            return True
        else:
            print "username regex error"
            return False

    elif type=="password":
        if re.match("(\S+)",value):
            return True
        else:
            print "password regex error"
            return False

    elif type=="fullname":
        if re.match("([A-z]+) ([A-z]+)",value):
            return True
        else:
            print "name regex error"
            return False

    elif type=="number":
        if re.match("([+]+)([0-9]+)",value):
            return True
        else:
            print "number regex error"
            return False

    elif type=="address":
        if re.match("^([0-9]+)(\s*)(\S*)([a-zA-Z ]+)(\s*)(\S*)",value):
            return True
        else:
            print "address regex error"
            return False

    elif type=="city":
        if re.match("[A-z]{2,}",value):
            return True
        else:
            print "city regex error"
            return False

    elif type=="date":
        if re.match("(\d+) (\d+) \d{4}",value):
            return True
        else:
            print "date regex error"
            return False

    elif type=="postal":
        if re.match("\d{6}",value):
            return True
        else:
            print "postal regex error"
            return False


    elif type=="state":
        for x in states:
            if x==value and value!="State":
                return True

        print "opps states is not valid"
        return False

    elif type=="email":
        if re.match("([a-zA-Z0-9_\.\-])+\@(([a-zA-Z0-9\-])+\.)+([a-zA-Z0-9]{2,4})+",value):
            return True
        else:
            print "email regex error"
            return False


def generateOneTimePassword():
    
    return generate_password_hash(str(random.random()))[20:26]
 
def removeOTP(user):
    user_ = User.query.filter_by(email=user).first()
    user_.password_hash=""
    db.session.commit()
    print user


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


def sendOneTimeText(number):
        try:
            gP=generateOneTimePassword()
            message = twilio_client.messages.create(to=number, from_="+2348114291038", body="Your Paymiumm OTP is "+gP)
            return True

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


@app.route('/get')
# @login_required
# @complete_registration
def get():
    t=threading.Timer(3,removeOTP,args=["ogochukwujoseph@gmail.com"])
    t.start()
    return jsonify({
        'code': 200,
        'status': 'okay',
    })


def exec_(email):
    t=threading.Timer(3,removeOTP,args=[email])
    t.start()
    return jsonify({
        'code': 200,
        'status': 'okay',
    })






@app.route("/generatePasswordToken", methods=['POST'])
@csrf.exempt
def generatePasswordToken():

    #get all json keys from request
    req_json=request.get_json()

    #check if value passed was a username or email

    if validate_("username",req_json['usr']) or validate_("email",req_json['usr']):
        type_=req_json['t_y_pE']
        user = User.query.filter_by(username=req_json['usr']).first()
        user_mail = User.query.filter_by(email=req_json['usr']).first()
        # session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']


        if user is not None:
            #if passed data is a validated username then get the email
            # user.email
            # if user.password_hash=="":
                if user.email_confirmed:
                    # return make_response(jsonify({'res':(user.password_hash!="")}))
                    # if (user.password_hash=="")==True:
                        try:
                            if type_=="email":
                                res=sendOneTimeMail(user.email)
                                if res!=False:
                                    # session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
                                    # users=User.query.filter_by(username=req_json['usr'])

                                    user.password_hash=res
                                    db.session.commit()
                                    exec_(str(user.email))
                                    print "username password change is done"
                                    return make_response(jsonify({'res':'success'}))

                                else:
                                    print "error in connection"
                                    print make_response(jsonify({'res':'error'}))
                                    return make_response(jsonify({'res':'error'}))
                            # else:
                                
                            #         res=sendOneTimeText(user.phone_number)
                            #         session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
                            #         # users=User.query.filter_by(username=req_json['usr'])
                            #         user.password_hash=res
                            #         db.session.commit()
                            #         exec_(str(user.email))
                            #         print "username password change is done"
                            #         return make_response(jsonify({'res':'success'}))



                        except:
                                print "error in occured"
                                return make_response(jsonify({'res':'error'}))

                    # else:
                    #     return make_response(jsonify({'res':'pswdErr'}))
                else:
                    return make_response(jsonify({'res':'unconfirmed'}))    

            # else:
            #     # # session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
            #     # return make_response(jsonify({'res':'alreadyPsskeyed'}))



        elif user_mail is not None:

            # if user_mail.password_hash=="":

                if user_mail.email_confirmed:
                    # if (user_mail.password_hash=="")==True:
                        

                        try:
                            if type_=="email":
                                res=sendOneTimeMail(user_mail.email)
                                if res!=False:
                                    # session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
                                    # users=User.query.filter_by(username=req_json['usr'])

                                        
                                    
                                    user_mail.password_hash=res
                                    db.session.commit()
                                    exec_(str(user_mail.email))
                                    print "username password change is done"
                                    return make_response(jsonify({'res':'success'}))

                                else:
                                    print "error in connection"
                                    print make_response(jsonify({'res':'error'}))
                                    return make_response(jsonify({'res':'error'}))
                            # else:
                            #         res=sendOneTimeText(user_mail.phone_number)
                            #         session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
                            #         user_mail.password_hash=res
                            #         db.session.commit()
                            #         print "email password change is done"
                            #         exec(str(user_mail.email))
                            #         return make_response(jsonify({'res':'success'}))

                        except:
                                print "error in occured"
                                return make_response(jsonify({'res':'error'}))

                    # else:
                    #     return make_response(jsonify({'res':'pswdErr'}))

                else:
                    return make_response(jsonify({'res':'unconfirmed'}))

            # else:
            #     # session['t_B_TSD_adEAS_']=req_json['t__Ukn__r_z_A_R']
            #     return make_response(jsonify({'res':'alreadyPsskeyed'}))    
                
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
                        
                        
                        
                        if user.dev_identity=="":
                            user.dev_identity=req_json['t__Ukn__r_z_A_R']
                            db.session.commit()
                            user.password_hash=""
                            
                        else:
                            if user.dev_identity==req_json['t__Ukn__r_z_A_R']:
                                user.password_hash=""
                                print "hello"
                            else:
                                return make_response(jsonify({'res':'used'}))
                        
                        db.session.commit()
                        session['user']=user.username
                        now = datetime.datetime.now()
                        login_user(user,remember=True)

                        return make_response(jsonify({'res':'true','da_t_e':str(now.year),'userId':str(session['user']),'user':str(user.username),'t_k_n_t_R': req_json['t__Ukn__r_z_A_R'],'user_email':str(user.email),'user_img':str(user.img_path)}))

                        #  return redirect(request.args.get('next') or url_for('index'))
                    elif  user.email_confirmed and not user.account_confirmed:

                        print "aunconfirmed"
                        if user.dev_identity=="":
                            user.dev_identity=req_json['t__Ukn__r_z_A_R']
                            db.session.commit()
                            user.password_hash=""
                            
                        else:
                            if user.dev_identity==req_json['t__Ukn__r_z_A_R']:
                                user.password_hash=""
                                print "hello"
                            else:
                                return make_response(jsonify({'res':'used'}))
                        
                        db.session.commit()
                        session['user']=user.username
                        now = datetime.datetime.now()
                        login_user(user,remember=True)
                        
                        return make_response(jsonify({'res':'accountUnconfirmed','da_t_e':str(now.year),'userId':str(session['user']),'user':str(user.username),'t_k_n_t_R':req_json['t__Ukn__r_z_A_R'],'user_email':str(user.email),'user_img':str(user.img_path)}))

                    print "unconfirmed"
                    return make_response(jsonify({'res':"unconfirmed"}))
                    #  flash('Mail not configured')

        elif user_mail is not None and user_mail.password_hash==req_json['pwd']:
                    print req_json['usr']

                    if user_mail.email_confirmed and user_mail.account_confirmed:

                        # print "\n\n"+request.form['remember']+"\n\n"
                        print "true"                        

                        #device token handler 
                        #check if user device identity has been set, if true then match with the token passed in the request, else return false, stating that the device token doesn't match....if it's not, set device identity 


                        if user_mail.dev_identity=="":
                            #set device identity
                            user_mail.dev_identity=req_json['t__Ukn__r_z_A_R']
                            db.session.commit()
                            #and clear the OTP from the db column
                            user_mail.password_hash=""
                        else:
                            #device identity already set....do this
                            if user_mail.dev_identity==req_json['t__Ukn__r_z_A_R']:
                                #and clear the OTP from the db column
                                user_mail.password_hash=""
                                print "hello"
                            else:
                                #return an error message......
                                return make_response(jsonify({'res':'used'}))
                        db.session.commit()
                        session['user']=user_mail.username
                        now = datetime.datetime.now()

                        login_user(user_mail,remember=True)

                        return make_response(jsonify({'res':'true','da_t_e':str(now.year),'userId':session['user'],'user':user_mail.username,'t_k_n_t_R':req_json['t__Ukn__r_z_A_R'],'user_email':str(user_mail),'user_img':str(user_mail.img_path)}))
                        #  return redirect(request.args.get('next') or url_for('index'))
                    elif  user_mail.email_confirmed and not user_mail.account_confirmed:

                        print "aunconfirmed"

                        #device token handler 
                        #check if user device identity has been set, if true then match with the token passed in the request, else return false, stating that the device token doesn't match....if it's not, set device identity 


                        if user_mail.dev_identity=="":
                            #set device identity
                            user_mail.dev_identity=req_json['t__Ukn__r_z_A_R']
                            db.session.commit()
                            #and clear the OTP from the db column
                            user_mail.password_hash=""
                        else:
                            #device identity already set....do this
                            if user_mail.dev_identity==req_json['t__Ukn__r_z_A_R']:
                                #and clear the OTP from the db column
                                user_mail.password_hash=""
                                print "hello"
                            else:
                                #return an error message......
                                return make_response(jsonify({'res':'used'}))
                        db.session.commit()

                        session['user']=user_mail.username
                        now = datetime.datetime.now()

                        login_user(user_mail,remember=True)

                        return make_response(jsonify({'res':"accountUnconfirmed",'da_t_e':str(now.year),'userId':session['user'],'user':user_mail.username,'t_k_n_t_R':req_json['t__Ukn__r_z_A_R'],'user_email':str(user_mail),'user_img':str(user_mail.img_path)}))

                    print "unconfirmed"
                    return make_response(jsonify({'res':"unconfirmed"}))
                    #  flash('Mail not configured')

        else:
            print "false"
            return make_response(jsonify({'res':"false"}))

    else:
        print "false"
        return make_response(jsonify({'res':"false"}))





@app.route('/signup', methods=['POST'])
@csrf.exempt
def signup():

        req_json=request.get_json()
        #validate form value
        user=req_json['usr']
        email=req_json['email']
        name=req_json['name']
        num=req_json['phn']

        if validate_("username",user) and validate_("email",email) and validate_("fullname",name) and validate_("number",num):
            
            try:
                user_ = User.query.filter_by(username=user).first()
                email_ = User.query.filter_by(email=email).first()
                phn_ = User.query.filter_by(phone_number=num).first()

                if user_ is not None:

                    print "username already exist"
                    return make_response(jsonify({'res':'user'}))

                elif email_ is not None:

                    return make_response(jsonify({'res':'email'}))

                elif phn_ is not None:

                    return make_response(jsonify({'res':'number'}))

                else:
                    user = User(full_name=name, email=email, username=user, phone_number=num, img_path="img_badge/fm0894tf9re.jpg")
                    db.session.add(user)
                    db.session.commit()
                    res=activateMail(email)
                    if res!=False:
                        return make_response(jsonify({'res':'true'}))
                    else:
                        db.session.rollback()
                        return make_response(jsonify({'res':'mailErr'}))

            except IntegrityError:
                db.session.rollback()
                return make_response(jsonify({'res':'false'}))
            except Exception,e:
                db.session.delete(user)
                db.session.commit()
                print "Error Occured: \n"+str(e)
                return make_response(jsonify({'res':'false'}))
        
        else:
            return make_response(jsonify({'res':'error'}))


@app.route('/resendConfirmation',methods=['POST'])
@csrf.exempt
def resend():

        # return make_response(jsonify({'res':'sent'}))
        req_json=request.get_json()
        #validate form value
        email=req_json['email']


        if validate_("email",email):
            
            try:
                email_ = User.query.filter_by(email=email).first()

                if email_ is not None and not email_.account_confirmed:

                    res=resend_activateMail(email)
                    if res!=False:
                        return make_response(jsonify({'res':'sent'}))
                    else:
                        return make_response(jsonify({'res':'mailErr'}))

                else:
                    return make_response(jsonify({'res':'invalid'}))
                    


            except IntegrityError,e:
                return make_response(jsonify({'res':'false'}))
            except Exception,e:
                # print "Error Occured: \n"+str(e)
                return make_response(jsonify({'res':'false'}))
        
        else:
            return make_response(jsonify({'res':'false'}))


@app.route('/personal',methods=['POST'])
@csrf.exempt
def personal():

        # return make_response(jsonify({'res':str(session['user'])}))
        req_json=request.get_json()
        # validate form value
        add=req_json['ad_d_r_eSS']
        state=req_json['statE']
        city=req_json['city']
        postal=req_json['postalC']
        dob=req_json['dob']



        if validate_("address",add) and validate_("state",state) and validate_("city",city) and validate_("postal",postal) and validate_("date",dob):
            
            try:
                # User.query.filter_by(username=user).first()
                user_ = User.query.filter_by(username=session['user']).first()
                # return make_response(jsonify({'res':str(session['user'])}))



                if user_ is not None:
                    try:
                        pDtails = PrivateDetails(address=add, city=city, state=state, postal_code=postal, date_of_birth=dob,user_id=str(session['user']))
                        db.session.add(pDtails)
                        db.session.commit()
                        user_.account_confirmed=True
                        db.session.commit()
                        return make_response(jsonify({'res':'true'})) 
                    except Exception,e:
                        db.session.delete(pDtails)
                        db.session.commit()
                        # print "Error Occured: \n"+str(e)
                        return make_response(jsonify({'res':'false'}))


                else:                    
                    print "user does not exist already exist"

                    return make_response(jsonify({'res':'error'}))

            except IntegrityError:
                db.session.rollback()
                return make_response(jsonify({'res':'false'}))
            except Exception,e:
                # db.session.delete(pDtails)
                db.session.commit()
                # print "Error Occured: \n"+str(e)
                return make_response(jsonify({'res':str(e)}))
        
        else:
            return make_response(jsonify({'res':'error'}))

