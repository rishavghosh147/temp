from app import app
from functools import wraps
from flask import request, jsonify,json
import jwt
from datetime import datetime
from key.keys import admin_secret_key,participants_secret_key,authorization_token_key

def token_validation_participents(f):
    @wraps(f)
    def validation(*args,**kwargs):
        check=authorization(participants_secret_key)
        if check:
            return check
        return f(*args,**kwargs)
    return validation

def token_validation_admin(f):
    @wraps(f)
    def validation(*args,**kwargs):
        check=authorization(admin_secret_key)
        if check:
            return check
        return f(*args,**kwargs)
    return validation

def token_validation_common(f): #error
    @wraps(f)
    def validation(*args,**kwargs):
        if authorization(admin_secret_key) is None:
            type="admin"
        elif authorization(participants_secret_key) is None:
            type="participant"
        else:
            return jsonify({"error":"you are not verified"})
        return f(*args,type=type,**kwargs)
    return validation


def expire():
    time=datetime.now()
    return int(time.timestamp())

def authorization(secret_key):
    token=request.headers.get(authorization_token_key)
    if not token:
        return False
    # token=json.loads(header)
    try:
        data=jwt.decode(token,secret_key,algorithms=['HS256'])
        if data['expire']< expire():
            return jsonify({"error":"login expire !!!"})
    except:
        return jsonify({"error":"the token is not valid !!!"})
    
def user_email(secret_key):
    head=request.headers.get(authorization_token_key)
    data=jwt.decode(head,secret_key,algorithms=['HS256'])
    return data['email']