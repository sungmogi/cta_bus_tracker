import os
from configparser import ConfigParser
import json
import requests

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: view_stops**")

        body = json.loads(event['body'])
        rt = body['rt']
        dir = body['dir']

        # Setup AWS based on config file
        config_file = 'bustracker-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # Configure for RDS access
        api_key = configur.get('cta', 'api_key')

        response = requests.get(
            "http://www.ctabustracker.com/bustime/api/v2/getstops",
            params={'key': api_key, 'rt': rt, 'dir': dir, 'format': 'json'}
        )

        stops = response.json()['bustime-response']['stops']
        parsed_stops = [{stop['stpid']: stop['stpnm']} for stop in stops]
        
        return {
            'statusCode': 200,
            'body': json.dumps(parsed_stops)
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(err)})
        }
