from pymongo import MongoClient
from openai import OpenAI
from dotenv import load_dotenv
import dotenv
import certifi
import sys
import os

# load environment variables
dotenv.load_dotenv()
OPEN_AI_KEY = os.getenv('OPEN_AI_KEY')
DB_STRING = os.getenv('DB_STRING')

# initialize openai client
client = OpenAI(api_key=OPEN_AI_KEY)

'''
-----------------------------------------------------------
This function is used to get the embedding of a text.
-----------------------------------------------------------
Parameters:
    text: str
    model: str
Returns:
    embedding: list
-----------------------------------------------------------
'''
def get_embedding(text : str, model="text-embedding-ada-002") -> list:
    text = text.replace("\n", " ")
    return client.embeddings.create(input = [text], model=model).data[0].embedding

'''
-----------------------------------------------------------
Return top k similar documents to the query.
-----------------------------------------------------------
Parameters:
    query: str 
Returns:
    documents: list
-----------------------------------------------------------
'''
def find_similar_documents(query: str, k: int = 3) -> list:
    # Connect to the MongoDB cluster
    client = MongoClient(DB_STRING, tlsCAFile=certifi.where())
    query_vector = get_embedding(query)
    # search the properties with the query
    try:
        db = client['properties_datacomm'] 
        collection = db['properties_embed']  
        # define the search path and the shape of return value
        pipeline = [
          {
            '$vectorSearch': {
              'index': 'vector_index', 
              'path': 'embedding', 
              'queryVector': query_vector,
              'numCandidates': 150, 
              'limit': k
            }
          }, {
            '$project': {
              '_id': 0, 
              'property_hash': 1, 
              'description': 1, 
              'price': 1,
              'amenities': 1,
              'location': 1,
              'score': {
                '$meta': 'vectorSearchScore'
              }
            }
          }
        ]

        result = collection.aggregate(pipeline)

        for i,x in enumerate(result):
            print(f'{i}: {x}')
    
        return result

    finally:
        client.close()

  
if __name__ == "__main__":
  try:
    query = sys.argv[1]
    find_similar_documents(query)
  except:
    print("Please provide a query.")
    



