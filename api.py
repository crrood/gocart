import time, uuid, base64, hashlib, logging, os, json
import requests
from flask import make_response
from configparser import ConfigParser

def generate_hmac_signature(url, method, timestamp, nonce, body):
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
  log = logging.getLogger(__name__)

  # trim root url if present
  if url[:4] == "http":
    url = url[(url.find("/", len("https://")), 1) :]

  config = ConfigParser()
  config.read("config.ini")
  merchant_id = config["API"]["MerchantId"]
  api_key = config["API"]["ApiKey"]
  body = json.dumps(body)

  raw_string = "|".join([merchant_id, api_key, timestamp, nonce, url, method, body])
  raw_string = raw_string.upper()
  raw_string = raw_string.replace(" ", "").replace("\n", "").replace("\t", "")


  b64_encoded_string = base64.b64encode(raw_string.encode())
  h = hashlib.new("sha256")
  h.update(b64_encoded_string)
  signature = h.hexdigest()

  return signature

def request(url, method, body):
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
  log = logging.getLogger(__name__)

  config = ConfigParser()
  config.read("config.ini")
  base_url = config["API"]["BaseUrl"]
  merchant_id = config["API"]["MerchantId"]

  timestamp = str(int(time.time()))
  nonce = str(uuid.uuid4())
  hmac_signature = generate_hmac_signature(url, method, timestamp, nonce, body)

  headers = {
    "X-Merchant-Id": merchant_id,
    "Timestamp": timestamp,
    "Nonce": nonce,
    "Signature": hmac_signature,
    "Content-Type": "application/json"
  }

  full_url = base_url + url
  r = requests.request(method, full_url, headers=headers, json=body)
  
  if "Content-Type" in r.headers and r.headers["Content-Type"] == "application/json":
    response_data = r.json()
  else:
    response_data = r.text

  flask_response = make_response(response_data, r.status_code)
  flask_response.headers["API-Headers"] = r.headers

  return flask_response
