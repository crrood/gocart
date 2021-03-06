import os, logging
import api, db
from bson import json_util
from flask import (Flask, make_response, render_template, request)
from flask_basicauth import BasicAuth

app = Flask(__name__)

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
log = logging.getLogger(__name__)

# static shopping cart
@app.route('/', methods = ['GET'])
def cart():
  return render_template('cart.html')

# checkout page
@app.route('/checkout', methods = ['GET'])
def checkout():
  return render_template('checkout.html')

# get a list of already created payments
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
  json_data = request.json
  json_data['status'] = 'created'

  order_collection.insert_one(json_data)

  return make_response({}, 200)

# status webhooks
@app.route('/webhooks', methods = ['POST'])
def receive_webhook():
  log.info(request.json)
  event_name = request.json['eventName']
  if event_name == 'ORDER_PAYMENT_SUCCEEDED':
    order_id = request.json['payload']['merchantOrderId']
    update = {'$set': {'status': 'completed'}}

    # no way to tell if a webhook is for an order or payment request
    # so check each DB to see if the id already exists
    order_collection = db.get_collection('orders')
    query = {'orderId': order_id}
    if order_collection.count_documents(query) > 0:
      order_collection.update_one(query, update)
    else:
      payment_collection = db.get_collection('payment-requests')
      query = {'merchantPaymentRequestId': order_id}
      payment_collection.update_one(query, update)

  return make_response({}, 200)

# shipping webhooks
@app.route('/shipping', methods = ['POST'])
def return_shipping():
  log.info(request.json)
  shipping_address_id = request.json['shippingAddress']['shippingAddressId']

  # hardcoded for testing
  # your server should calculate shipping and tax here
  response_body = {
    'shippingAddressId': shipping_address_id,
    'currencyCode': 'USD',
    'shippingOptions': [
        {
            'id': 1,
            'name': 'Ground Freight',
            'price': 25.98
        },
        {
            'id': 2,
            'name': 'Next Day Air',
            'price': 42.50
        }
    ],
    'preferredShippingOptionId': 1,
    'tax': 10.5
  }

  return make_response(response_body, 200)

# drop all data from DB
@app.route('/reset-db', methods = ['GET'])
def db_reset():
  return db.reset()

if __name__ == '__main__':
  app.run()
