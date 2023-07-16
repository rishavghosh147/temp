from app import app
from flask_restful import Resource
from flask import json,request,jsonify,make_response
from database.database import Temp_user, User,db,Temp_otp,Participants
import jwt
from datetime import datetime, timedelta
from key.keys import otp_virify_secret_key,admin_secret_key,participants_secret_key,authorization_token_key

class otp_verify(Resource): #done
    def post(self):
        if 'verification' in request.headers:
            header=request.headers.get('verification')
            # header=json.loads(token)
        data=json.loads(request.data)
        if not data['otp']:
            return jsonify({"error":"please enter a valid otp !!!"})
        try:
            verify_type=jwt.decode(header,otp_virify_secret_key,algorithms=['HS256'])
        except:
            return jsonify({"error":"you are not permited"})
        if 'signup' in verify_type:
            user=Temp_user.query.filter_by(email=verify_type['email']).first()
            if user and user.otp==int(data['otp']):
                users=User(fname=user.fname,lname=user.lname,email=user.email,mobile=user.mobile,roll=user.roll,password=user.password,role_id=user.role_id,year=user.year,stream=user.stream)
                db.session.add(users)
                db.session.delete(user)
                db.session.commit()
                return jsonify({"successful":"user registered successfully "})
        elif 'login' in verify_type:
            otp=Temp_otp.query.filter_by(login_email=verify_type['email']).first()
            if otp and otp.otp==int(data['otp']):
                if verify_type['role']=="0":
                    secret_key=admin_secret_key
                else:
                    secret_key=participants_secret_key

                token=self.token_gen(verify_type['email'].lower(),secret_key)
                db.session.delete(otp)
                db.session.commit()
                return jsonify({"successful":"you are loged in successfully","authorization":token})
        elif 'forget' in verify_type:
            otp=Temp_otp.query.filter_by(login_email=verify_type['email'].lower()).first()
            if  otp and otp.otp==int(data['otp']):
                user=User.query.filter_by(email=verify_type['email'].lower()).first()
                user.password=otp.password
                db.session.delete(otp)
                db.session.commit()
                return jsonify({"successful":"the password has been changed successfully"})
        return jsonify({"error":"you entered a wrong otp !!!"})
    
    def token_gen(self,email,secret_key):
        time=datetime.now()+timedelta(minutes=60)
        exp_time=int(time.timestamp())
        payload={"email":email,"expire":exp_time}
        token=jwt.encode(payload,secret_key,algorithm='HS256')
        return token.decode('utf-8')