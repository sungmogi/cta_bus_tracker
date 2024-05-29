import os
from configparser import ConfigParser
import datatier
import bcrypt
import json
import jwt
import datetime

def lambda_handler(event, context):
    try:
        print("**STARTING**")
        print("**lambda: login**")

        # username and password parsed from event
        body = json.loads(event['body'])
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

        sql = '''
            SELECT userid, username, pwdhash FROM users WHERE username=%s;
        '''

        row = datatier.retrieve_one_row(dbConn, sql, [username])

        if row == ():  # no such user
            print("**No such user, returning...**")
            return { 'statusCode': 400, 'body': json.dumps("Invalid username or password") }
        
        userid, db_username, stored_hash = row
    
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
            secret_key = configur.get('jwt', 'secret_key')
            exp_time = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=2)
            payload = {"userid": userid, "username": db_username, "exp": exp_time}
            token = jwt.encode(payload, secret_key, algorithm='HS256')

            return { 'statusCode': 200, 'body': json.dumps({"token": token})}
            
        else:
            return { 'statusCode': 400, 'body': json.dumps("Invalid username or password") }


    except Exception as err:
        print("**ERROR**")
        print(str(err))
        
        return {
        'statusCode': 400,
        'body': json.dumps(str(err))
        }