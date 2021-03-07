from flask import Flask, request
from flask_cors import CORS
import requests
import sys
import json

app = Flask(__name__)
app.debug = True
CORS(app)

_chargers_api = "https://s3-ap-southeast-1.amazonaws.com/he-public-data/chargers1e8f81f.json"

def get_restaurant_recommendation():
  restr_response = requests.get("https://s3-ap-southeast-1.amazonaws.com/he-public-data/restaurants6010ade.json")
  restaurants_list = restr_response.json()["restaurants"]
  top_10_restaurants = sorted(restaurants_list, key = lambda i: i['rating'])[:10]
  return {"restaurants" : top_10_restaurants}

def get_chargers():
  chargers_api_response = requests.get(_chargers_api)
  if chargers_api_response.status_code == 200:
    return chargers_api_response.json()
  return {"error" : "Couldn't fetch any response from the _chargers_api address"}


def get_charge_status(curr_fuel_dis, charger_arr):
  """
    Since the only condition mentioned was that the car should reach the destination and there were no pointers
    mentioned whether a threshold of charge should be present before reaching the destination, I'll consider 'equal to'
    condition when comparing the values.
  """
  max_dis = len(charger_arr['array']) # max distance we can go after charging from the charging station
  max_charge_from_station = max(charger_arr['array'])
  recommended_restaurants = None

  if curr_fuel_dis >= max_dis:
    if recommended_restaurants is None:
      """
      Since we are using the same api to get list of restaurants, storing this value in a variable to use it in future testcase.
      Depending on the endpoint called to get the restaurant list we can also change this value to get dynamic results everytime.
      """
      recommended_restaurants = get_restaurant_recommendation()
    return recommended_restaurants

  if curr_fuel_dis + max_charge_from_station >= max_dis:
    return 200

  return 400 # return code 400 if reaching destination is unsuccessful

@app.route("/")
def home_page():
  return "Welcome to Home page"

@app.route('/getRes', methods=['GET', 'POST'])
def getRes():
  try:
    """
    We should use the POST method here to accept requests only from known accounts,
    but keeping it generic for now.
    """
    respone = request.json   # getting the form data sent with api request
    vehicle_curr_fuel = float(respone.get('vehicle_curr_fuel'))
  except:
    return "Couldn't get the current fuel level of the vehicle. Please pass a value in <vehicle_curr_fuel> in the form."
  # elif request.method == 'GET':
  #   return "Request not authorized."
  res_json = []
  all_chargers = get_chargers()
  if "error" in all_chargers:
    return all_chargers["error"]

  chargers_list = all_chargers["chargers"]
  for charger_arr in chargers_list:
    res_json.append(get_charge_status(vehicle_curr_fuel, charger_arr))
  return json.dumps(res_json)



