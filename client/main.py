import requests

import pathlib
import logging
import sys

from configparser import ConfigParser


############################################################
#
# classes
#
class User:

  def __init__(self, row):
    self.userid = row[0]
    self.username = row[1]
    self.pwdhash = row[2]


############################################################
#
# prompt
#
def prompt():
  """
  Prompts the user and returns the command number

  Parameters
  ----------
  None

  Returns
  -------
  Command number entered by user (0, 1, 2, ...)
  """
  print()
  print(">> Enter a command:")
  print("   0 => end")
  print("   1 => register")
  print("   2 => login")
  print("   3 => view routes")
  print("   4 => view stops")
  print("   5 => add favorite route")
  print("   6 => view ETA")

  cmd = input()

  if cmd == "":
    cmd = -1
  elif not cmd.isnumeric():
    cmd = -1
  else:
    cmd = int(cmd)

  return cmd


############################################################
#
# register
#
def register(baseurl):
  """
  call create_user
  
  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/user'
    url = baseurl + api

    print("Enter username>")
    username = input()

    print("Enter password>")
    password = input()

    data = {"username": username, "password": password}

    res = requests.post(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        body = res.json()
        print("Error message:", body)
      return

    #
    # deserialize and extract users:
    #
    body = res.json()

    print(body['message'])
    return

  except Exception as e:
    logging.error("register() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# login
#
def login(baseurl):
  """
  Login

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  token
  """

  try:
    #
    # call the web service:
    #
    api = '/login'
    url = baseurl + api

    print("Enter username>")
    username = input()

    print("Enter password>")
    password = input()

    data = {"username": username, "password": password}

    res = requests.post(url, json=data)

    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    body = res.json()

    token = body['token']

    print(f"Welcome, {username}")
    return token

  except Exception as e:
    logging.error("jobs() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# routes
#
def routes(baseurl):
  """
  View all CTA bus routes

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/routes'
    url = baseurl + api

    res = requests.get(url)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      #
      return

    #
    # deserialize and print message
    #
    body = res.json()

    for route, name in body.items():
        print(f"Route {route}: {name}")
    return

  except Exception as e:
    logging.error("routes() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
#
# stops
#
def stops(baseurl):
  """
  View CTA bus stops given route and direction

  Parameters
  ----------
  baseurl: baseurl for web service

  Returns
  -------
  nothing
  """

  try:
    #
    # call the web service:
    #
    api = '/stops'
    url = baseurl + api

    print("Enter bus route>")
    route = input()

    print("Enter number corresponding to desired direction>")
    print("   1 => Eastbound")
    print("   2 => Westbound")
    print("   3 => Southbound")
    print("   4 => Northbound")

    index = int(input())
    
    if index == 1:
        direction = 'Eastbound'
    elif index == 2:
        direction = 'Westbound'
    elif index == 3:
        direction = 'Southbound'
    elif index == 4:
        direction = 'Northbound'
    else:
        print("Invalid direction...")
        return

    data = {"rt": route, "dir": direction}

    res = requests.get(url, json=data)

    #
    # let's look at what we got back:
    #
    if res.status_code != 200:
      # failed:
      print("Failed with status code:", res.status_code)
      print("url: " + url)
      if res.status_code == 400:
        # we'll have an error message
        body = res.json()
        print("Error message:", body)
      return

    #
    # deserialize and print message
    #
    body = res.json()

    for stop in body:
        for key, value in stop.items():
            print(f"Stop {key}: {value}")
    return

  except Exception as e:
    logging.error("stops() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def add_fav_route(baseurl, token):
  """
  Parameters
  ----------
  baseurl: baseurl for web service
  userid

  Returns
  -------
  nothing
  """
  try:
    if token is None:
      print("Please login")
      return
    
    #
    # call the web service:
    #
    api = '/fav-routes'
    url = baseurl + api

    #
    # make request:
    #
    
    req_header = {"Authentication": token}

    print("Enter bus route>")
    route = input()

    print("Enter bus stop>")
    stop = input()

    data = {"rt": route, "stop": stop}

    res = requests.post(url, headers=req_header, json=data)

    if res.status_code != 200:
        if res.status_code == 401:
           print("Authentication failure. Please log in.")
           return
        print("Failed with status code:", res.status_code)
        return

    body = res.json()

    print(body['message'])
    return
    

  except Exception as e:
    logging.error("add_fav_route() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


def get_pred(baseurl, token):
  """
  Parameters
  ----------
  baseurl: baseurl for web service
  userid

  Returns
  -------
  nothing
  """
  try:
    if token is None:
      print("Please login")
      return
    
    #
    # call the web service:
    #
    api = '/fav-routes'
    url = baseurl + api

    #
    # make request:
    #
    
    req_header = {"Authentication": token}

    res = requests.get(url, headers=req_header)

    if res.status_code != 200:
        if res.status_code == 401:
           print("Authentication failure. Please log in.")
           return
        print("Failed with status code:", res.status_code)
        return

    body = res.json()
    print("Enter number corresponding to desired route and stop>")
    for i, fav_route in enumerate(body):
        print(f"   {i+1} => Route {fav_route['rt']}, Stop {fav_route['stop']}")

    index = int(input())
    rt_stop = body[index-1]

    print(f"Fetching ETA for Route {rt_stop['rt']}, Stop {rt_stop['stop']}")

    # Second API call

    api = '/preds'
    url = baseurl + api

    data = {"rt": rt_stop['rt'], "stop": rt_stop['stop']}

    res = requests.get(url, json=data)

    body = res.json()

    if 'error' in body:
        print(body['error'])
        return
    
    for eta in body:
        if int(eta['time_diff']) <= 0:
            print(f"Vehicle {eta['vid']} will arrive soon")
        else:
            print(f"Vehicle {eta['vid']} will arrive in {eta['time_diff']} minutes")

    return

  except Exception as e:
    logging.error("add_fav_route() failed:")
    logging.error("url: " + url)
    logging.error(e)
    return


############################################################
# main
#
try:
  print('** Welcome to Bus Tracker **')
  print()

  # eliminate traceback so we just get error message:
  sys.tracebacklimit = 0

  config_file = 'bustracker-client-config.ini'

  print("Config file to use for this session?")
  print("Press ENTER to use default, or")
  print("enter config file name>")
  s = input()

  if s == "":  # use default
    pass  # already set
  else:
    config_file = s

  #
  # does config file exist?
  #
  if not pathlib.Path(config_file).is_file():
    print("**ERROR: config file '", config_file, "' does not exist, exiting")
    sys.exit(0)

  #
  # setup base URL to web service:
  #
  configur = ConfigParser()
  configur.read(config_file)
  baseurl = configur.get('client', 'webservice')

  #
  # make sure baseurl does not end with /, if so remove:
  #
  if len(baseurl) < 16:
    print("**ERROR: baseurl '", baseurl, "' is not nearly long enough...")
    sys.exit(0)

  if baseurl == "https://YOUR_GATEWAY_API.amazonaws.com":
    print("**ERROR: update config file with your gateway endpoint")
    sys.exit(0)

  if baseurl.startswith("http:"):
    print("**ERROR: your URL starts with 'http', it should start with 'https'")
    sys.exit(0)

  lastchar = baseurl[len(baseurl) - 1]
  if lastchar == "/":
    baseurl = baseurl[:-1]

  #
  # main processing loop:
  #
  cmd = prompt()

  while cmd != 0:
    #
    if cmd == 1:
      register(baseurl)
    elif cmd == 2:
      token = login(baseurl)
    elif cmd == 3:
      routes(baseurl)
    elif cmd == 4:
      stops(baseurl)
    elif cmd == 5:
      add_fav_route(baseurl, token)
    elif cmd == 6:
      get_pred(baseurl, token)
    else:
      print("** Unknown command, try again...")
    #
    cmd = prompt()

  #
  # done
  #
  print()
  print('** done **')
  sys.exit(0)

except Exception as e:
  logging.error("**ERROR: main() failed:")
  logging.error(e)
  sys.exit(0)
