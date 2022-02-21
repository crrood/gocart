import time, uuid, base64, hashlib, logging, os, json
import requests
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

  log.info(raw_string)

  b64_encoded_string = base64.b64encode(raw_string.encode())
  log.info(b64_encoded_string)
  h = hashlib.new("sha256")
  h.update(b64_encoded_string)
  signature = h.hexdigest()

  log.info(signature)

  return signature

def api_request(url, method, body):
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
  log = logging.getLogger(__name__)

  config = ConfigParser()
  config.read("config.ini")
  base_url = config["API"]["BaseUrl"]

  timestamp = str(int(time.time()))
  nonce = str(uuid.uuid4())
  hmac_signature = generate_hmac_signature(url, method, timestamp, nonce, body)

  headers = {
    "X-Merchant-Id": config["API"]["MerchantId"],
    "Timestamp": timestamp,
    "Nonce": nonce,
    "Signature": hmac_signature
  }

  full_url = base_url + url
  log.info(full_url)
  log.info(body)
  r = requests.request(method, full_url, headers=headers, data=body)
  log.info(r.status_code)
  log.info(r.text)

  return r.json()