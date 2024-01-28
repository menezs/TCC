from dotenv import load_dotenv
import pymongo
import os
load_dotenv()

class Mongo():

    def __init__(self, collectionName):

        self.collection = self.__connect_db(collectionName)

    def __connect_db(self, collectionName):
        database_name = "TCC"
        
        uri = os.getenv('MONGO_URI')
        
        client = pymongo.MongoClient(uri)
        
        db = client[database_name]
        
        collection = db[collectionName]

        return collection