from ..database.db_mongo import Mongo
import pandas as pd
import pymongo 

class Music():

    def __init__(self, filePath):
        self.filePath = filePath

    def read_dataframe(self):

        df = pd.read_csv(self.filePath, sep=",", low_memory=False)

        return df
    
    def getMusic(self):

        df = self.read_dataframe()

        listMusic = df['name'].unique()

        return list(listMusic)
    
    def getRecommendation(self, music1, music2):

        print(music1)
        print(music2)

        recommendation = []

        collection = Mongo('musicResults').collection

        dataDB = collection.find({"musicA": music1, "musicB": music2}).sort("confidence", pymongo.DESCENDING).limit(10)

        dataListDB = list(dataDB)

        if len(dataListDB) > 0:
            dataListDB[0].pop('_id')
            dataDB = dataListDB[0]

            recommendation.append(dataDB)

        print(recommendation)

        return recommendation


