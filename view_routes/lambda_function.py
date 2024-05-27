import os
from configparser import ConfigParser
import json
import requests

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: view_routes**")

        # Setup AWS based on config file
        config_file = 'bustracker-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # Configure for RDS access
        api_key = configur.get('cta', 'api_key')

        response = requests.get(
            "http://www.ctabustracker.com/bustime/api/v2/getroutes",
            params={'key': api_key, 'format': 'json'}
        )

        routes = response.json()['bustime-response']['routes']
        rts = [{route['rt']: route['rtnm']} for route in routes]
        print(rts)

        res = {
            'statusCode': 200,
            'body': json.dumps({rts})
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(err)})
        }
