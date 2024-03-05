
import pymongo
from pymongo import MongoClient
import os
import dotenv
import certifi

ca = certifi.where()
dotenv.load_dotenv()
CONNECTION_STRING = os.getenv('MONGODB_STRING')

def get_database():
   # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
   client = MongoClient(CONNECTION_STRING, tlsCAFile=certifi.where())
   # Create the database for our example (we will use the same database throughout the tutorial
   return client['properties_datacomm']

def get_collection(db, collection_name):
    # This is for the collection you want to use
    return db[collection_name]


if __name__ == "__main__":
  
    # test connection and ping the server
   from pymongo.mongo_client import MongoClient
   uri = 'mongodb+srv://admin:d@cluster0.latonvh.mongodb.net/'

   # Create a new client and connect to the server
   client = pymongo.MongoClient(uri, tlsCAFile=certifi.where())

   # Send a ping to confirm a successful connection
   try:
       client.admin.command('ping')
       print("Pinged your deployment. You successfully connected to MongoDB!")
   except Exception as e:
       print(e)
