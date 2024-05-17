import os
from configparser import ConfigParser
import datatier
import bcrypt
import json

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: create_user**")

        # username and password parsed from event
        body = event['body']
        username = body['username']
        password = body['password']

        # setup AWS based on config file:
        config_file = 'bustracker-config.ini'
        os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

        configur = ConfigParser()
        configur.read(config_file)

        # configure for RDS access
        rds_endpoint = configur.get('rds', 'endpoint')
        rds_portnum = int(configur.get('rds', 'port_number'))
        rds_username = configur.get('rds', 'user_name')
        rds_pwd = configur.get('rds', 'user_pwd')
        rds_dbname = configur.get('rds', 'db_name')

        dbConn = datatier.get_dbConn(rds_endpoint, rds_portnum, rds_username, rds_pwd, rds_dbname)

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        sql = '''
            INSERT INTO users (username, pwdhash) VALUES (%s, %s);
        '''

        datatier.perform_action(dbConn, sql, [username, hashed_password])

        return { 'statusCode': 200, 'body': json.dumps({"message": "User registered successfully"}) }


    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
        'statusCode': 400,
        'body': json.dumps(str(err))
        }