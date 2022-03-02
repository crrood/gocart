import os, logging
import api, db
from bson import json_util
from flask import (Flask, make_response, render_template, request)
from flask_basicauth import BasicAuth

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'gocart'
app.config['BASIC_AUTH_PASSWORD'] = 'devex2022'
app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
log = logging.getLogger(__name__)

# static shopping cart
@app.route('/')
def cart():
  return render_template('cart.html')

# checkout page
@app.route('/checkout')
def checkout():
  return render_template('checkout.html')

# get a list of already created payments
# stored server-side
@app.route('/payment-requests', methods = ['GET'])
def get_payment_requests():
  payment_collection = db.get_collection('payment_requests')

  results = payment_collection.find()
  result_string = ''
  for result in results:
    result_string = result_string + json_util.dumps(result) + '<hr>'

  return result_string

# create a new payment via the GoCart API
@app.route('/payment-requests', methods = ['POST'])
def create_payment_request():
  response = api.request('payment-requests', 'POST', request.json)

  # add to DB
  if response.status_code == 200:
    try:
      json_data = json_util.loads(response.data)
      json_data['status'] = 'created'
      payment_collection = db.get_collection('payment_requests')
      payment_collection.insert_one(json_data)
    except:
      log.error('oh shit')
      log.info(response.data)

  return response

# get a list of orders
@app.route('/orders', methods = ['GET'])
def get_orders():
  order_collection = db.get_collection('orders')

  results = order_collection.find()
  result_string = ''
  for result in results:
    result_string = result_string + json_util.dumps(result) + '<hr>'

  return result_string

# store order in DB
@app.route('/orders', methods = ['POST'])
def create_order():
  order_collection = db.get_collection('orders')
  order_collection.insert_one(request.json)

  return make_response({}, 200)

# webhooks
@app.route('/webhooks', methods = ['POST'])
def receive_webhook():
  event_name = request.json['eventName']
  if event_name == 'ORDER_PAYMENT_SUCCEEDED':
    order_collection = db.get_collection('orders')
    order_id = request.json['payload']['orderId']
    order = order_collection.find({'orderId': order_id})
  else:
    payment_collection = db.get_collection('payment-requests')
    payment_request_id = request.json['payload']['paymentRequestId']
    payment = payment_collection.find({'paymentRequestId': request.json['payload']['paymentRequestId']})

  return make_response({}, 200)

# drop all data from DB
@app.route('/reset-db')
def db_reset():
  return db.reset()

if __name__ == '__main__':
  app.run()
