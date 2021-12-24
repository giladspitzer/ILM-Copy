import json
import requests
from hashlib import md5
from datetime import datetime

def lambda_handler(event, context):
    d = md5(str(datetime.strftime(datetime.utcnow(), '%m%d%Y')).encode('utf-8')).hexdigest()
    p = md5(str('FB6Ejd+U^KK=Wxnc').encode('utf-8')).hexdigest()
    print(requests.get('https://ilmjtcv.com/bg/send_appointment_follow_up/' + str(d) + '/' + str(p)))
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }

lambda_handler(0, 0)