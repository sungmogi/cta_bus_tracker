import os
from configparser import ConfigParser
import json
import requests
from datetime import datetime, timezone, timedelta

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: get_pred**")

        body = json.loads(event['body'])
        rt = body['rt']
        stop = body['stop']

        # Setup AWS based on config file
        config_file = 'bustracker-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # Configure for RDS access
        api_key = configur.get('cta', 'api_key')

        response = requests.get(
            "http://www.ctabustracker.com/bustime/api/v2/getpredictions",
            params={'key': api_key, 'rt': rt, 'stpid': stop, 'format': 'json'}
        )

        res = response.json()['bustime-response']
        
        if 'prd' not in res:
            return {
                'statusCode': 400,
                'body': json.dumps({"error": res['error'][0]['msg']})
            }
            
        
        preds = res['prd']
        
        timestamps = [{'time': pred['tmstmp'], 'vid': pred['vid']} for pred in preds]
        
        cst_offset = timedelta(hours=-5)
        cst_timezone = timezone(cst_offset)
        current_time = datetime.now(cst_timezone)
        
        formatted_timestamps = []
        
        for timestamp in timestamps:
            time = timestamp['time']
            formatted_time = datetime.strptime(time, "%Y%m%d %H:%M").replace(tzinfo=cst_timezone)
            time_diff = formatted_time - current_time
            time_diff_minutes = int(time_diff.total_seconds() / 60)
            formatted_timestamps.append({'time_diff': time_diff_minutes, 'vid': timestamp['vid']})
            
        return {
            'statusCode': 200,
            'body': json.dumps(formatted_timestamps)
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(err)})
        }
