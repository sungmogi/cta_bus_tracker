import os
from configparser import ConfigParser
import datatier
import json
import requests

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: view_fav_routes**")

        if "headers" not in event:
            msg = "no headers in request"
            print("**ERROR:", msg)

            return {
                'statusCode': 400,
                'body': json.dumps(msg)
            }
      
        headers = event['headers']  
    
        if "Authentication" not in headers:
            msg = "no security credentials"
            print("**ERROR:", msg)
        
            return {
                'statusCode': 401,
                'body': json.dumps(msg)
            }
      
        token = headers["Authentication"]

        # Setup AWS based on config file
        config_file = 'bustracker-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        auth_url = configur.get('auth', 'webservice')
        data = {"token": token}
        api = '/auth'
        url = auth_url + api
        response = requests.post(url, json=data)
        
        if response.status_code != 200:
            return {
                'statusCode': 401,
                'body': json.dumps({"error": "token expired"})
            }

        data = response.json()
        userid = data['userid']

        # Configure for RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        # SQL query to insert new user
        sql = '''
            SELECT route_number, stop_id FROM fav_routes WHERE user_id=%s;
        '''

        rows = datatier.retrieve_all_rows(dbConn, sql, [userid])

        fav_routes = [{'rt': row[0], 'stop': row[1] } for row in rows]
        print(fav_routes)

        return {
            'statusCode': 200,
            'body': json.dumps(fav_routes)
        }

    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
            'statusCode': 400,
            'body': json.dumps({"error": str(err)})
        }
