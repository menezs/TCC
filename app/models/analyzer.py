from ..database.db_mongo import Mongo
from datetime import datetime
from apyori import apriori
import pandas as pd
import pymongo 

class Analyzer():
    def __init__(self, filePath, docId):
        self.filePath = filePath
        self.docId = docId

    def read_dataframe(self):

        df = pd.read_csv(self.filePath, sep=';', low_memory=False)

        df.dropna(subset=["Itemname"],inplace=True)

        df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M"))

        return df
    
    def createAssociationRules(self, records, docId, country):
        association_rules = apriori(records, min_support=0.0045, min_confidence=0.4, min_lift=3, min_length=2)
        association_results = list(association_rules)

        results = []
        for item in association_results:
            
            atual = {}

            pair = item[0] 
            items = [x for x in pair]
            atual.update({"itemA": f"{str(items[0])}"})
            atual.update({"itemB": f"{str(items[1])}"})
            atual.update({"support":  f"{str(item[1])}"})
            atual.update({"confidence":  f"{str(item[2][0][2])}"})
            atual.update({"lift": f"{str(item[2][0][3])}"})
            atual.update({"docId": docId})
            atual.update({"country": country})

            results.append(atual)

        return results
    
    def getCountries(self, country):

        df = self.read_dataframe()
        
        countries = []
        for country in df['Country']:
            if not country in countries:
                countries.append(country)
                
        return countries
    
    def firstRanking(self, rankingList, country):

        collection = Mongo("aprioriResultsTest").collection

        allData = collection.find({"docId": self.docId, "country": country})

        if len(list(allData)) == 0:

            dfData = self.read_dataframe()

            compraID = list(dfData.BillNo.drop_duplicates())

            records = []
            for id in compraID:
                records.append(list(dfData[dfData.BillNo == id].Itemname))

            allData = self.createAssociationRules(records, self.docId, country)

            collection.insert_many(allData)

        dataResult = []

        for item in rankingList:

            dataDB = collection.find({"docId": self.docId, "productA": item}).sort("confidence", pymongo.DESCENDING)
            dataListDB = list(dataDB)

            if len(dataListDB) > 0:
                dataListDB[0].pop('_id')
                dataDB = dataListDB[0]
            else:
                dataDB = {
                    "productA": item,
                    "productB": "Undefined",
                    "confidence": 0,
                    "support": 0,
                    "lift": 0
                }

            dataResult.append(dataDB)

        return dataResult


        



        

        
