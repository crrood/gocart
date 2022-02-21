import time, uuid, base64, hashlib, logging
from configparser import ConfigParser

def generate_hmac_signature(url, method, body):
  logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
  log = logging.getLogger(__name__)

  # trim root url if present
  if url[:4] == "http":
    url = url[(url.find("/", len("https://")) + 1) :]

  config = ConfigParser()
  config.read("config.ini")
  merchant_id = config["credentials"]["MerchantId"]
  api_key = config["credentials"]["ApiKey"]

  timestamp = str(int(time.time()))
  nonce = str(uuid.uuid4())

  raw_string = str(merchant_id + api_key + timestamp + nonce + url + method + body)
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