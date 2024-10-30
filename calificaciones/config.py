import os 

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    FIREBASE_CONFIG = 'C:\evaluacion\planevaluacion-803ca-firebase-adminsdk-l70kg-80b3dc84ec.json'

