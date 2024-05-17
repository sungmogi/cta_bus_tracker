import requests
import json

def lambda_handler(event, context):
    # API endpoint
    api_url = 'http://www.ctabustracker.com/bustime/api/v2/getroutes'
    
    # API key
    api_key = 'n4KcAdJxZSryePdBghR6mSiqG'
    
    # Parameters for the GET request
    params = {
        'key': api_key,
        'format': 'json'
    }
    
    # Sending the GET request
    response = requests.get(api_url, params=params)
    
    # Checking if the request was successful
    if response.status_code == 200:
        # Parsing the JSON response
        data = response.json()
        rt_rtnm_list = [(route['rt'], route['rtnm']) for route in data['bustime-response']['routes']]
        return {
            'statusCode': 200,
            'body': json.dumps(rt_rtnm_list)
        }
    else:
        # Handling errors
        return {
            'statusCode': response.status_code,
            'body': 'Failed to retrieve available routes from API'
        }

