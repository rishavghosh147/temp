from app import app
from flask_restful import Resource
from flask import json,request,jsonify,send_file
from authentication.token_validation import token_validation_admin
from database.database import Event,Team_participate,Participants,User
import pandas as pd,jwt
from authentication.send_otp import send_mail
from key.keys import admin_secret_key,authorization_token_key

class Download_by_admin(Resource): #done
    @token_validation_admin
    def post(self):
        data=json.loads(request.data)
        token=request.headers.get(authorization_token_key)
        event=Event.query.filter_by(event_name=data['event_name']).first()
        xl=[]
        i=0
        if event.team==0:
            roll=Participants.query.filter_by(event_name=data['event_name']).all()
            for x in roll:
                user=User.query.filter_by(roll=roll[i].roll).first()
                i=i+1
                xl.append({
                'name': user.fname+" "+user.lname,
                'roll': user.roll,
                'email': user.email,
                'mobile': user.mobile,
                'year': user.year,
                'stream': user.stream
            })
        else:
            roll=Team_participate.query.filter_by(event_name=data['event_name']).order_by(Team_participate.team_name).all()
            for x in roll:
                user=User.query.filter_by(roll=roll[i].roll).first()
                xl.append({
                'name': user.fname+" "+user.lname,
                'roll': user.roll,
                'email': user.email,
                'mobile': user.mobile,
                'year': user.year,
                'stream': user.stream, 
                'team_name': x.team_name
            })
                
        filename='event_details/'+data['event_name']+'.xlsx'
        df=pd.DataFrame(xl)
        df.to_excel(filename,index=False)
        msg=f"Participants of {data['event_name']}"
        data=jwt.decode(token,admin_secret_key,algorithms=['HS256'])
        send_mail('Participants details',data['email'],msg)
        return jsonify({"successful":"please check your mail"})