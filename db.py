import os
from pymongo import MongoClient

DATABASE = 'gocart'

# connect to DB
def get_client():
  client = MongoClient(os.environ['MONGODB_CONNSTRING'])
  return client

def get_database():
  client = get_client()
  return client[DATABASE]

def get_collection(collection):
  client = get_database()
  return client[collection]

# drop the DB
def reset():
  client = get_client()
  client.drop_database(DATABASE)

  return 'db reset'