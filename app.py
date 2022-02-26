import os, logging
import utilities
from pymongo import MongoClient
from bson import json_util
from flask import (Flask, render_template, request)

app = Flask(__name__)

DATABASE = "gocart"

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
log = logging.getLogger(__name__)

@app.route('/')
def cart():
  return render_template("cart.html")
  
@app.route('/checkout')
def checkout():
  return render_template("checkout.html")

@app.route('/payment-requests', methods = ["GET"])
def get_payment_requests():
  payment_requests = get_collection("payment_requests")

  results = payment_requests.find()
  result_string = ""
  for result in results:
    result_string = result_string.join(json_util.dumps(result))

  return result_string

@app.route('/payment-requests', methods = ["POST"])
def create_payment_request():
  # send a request to the GoCart API
  response = utilities.api_request("payment-requests", "POST", request.json)
  return response

def get_client():
  client = MongoClient(os.environ["MONGODB_CONNSTRING"])
  return client

def get_database():
  client = get_client()
  return client[DATABASE]

def get_collection(collection):
  client = get_database()
  return client[collection]

@app.route('/reset-db')
def db_reset():
  client = get_client()
  client.drop_database(DATABASE)

  return "db reset"

if __name__ == "__main__":
  app.run()
