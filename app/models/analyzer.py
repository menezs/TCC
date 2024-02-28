from ..database.db_mongo import Mongo
from datetime import datetime
from efficient_apriori import apriori
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
    
    def createAssociationRules(self, records, docId, country, year):
        item_set, association_rules = apriori(records, min_support=0.0045, min_confidence=0.4, max_length=2) #, min_lift=3, min_length=2)

        results = []
        for rule in association_rules:
            if len(rule.lhs) == 1:
                atual = {}
                atual.update({"product": rule.lhs[0]})
                atual.update({"consequent": rule.rhs[0]})
                atual.update({"confidence": rule.confidence})
                atual.update({"support": rule.support})
                atual.update({"lift": rule.lift})
                atual.update({'country': country})
                atual.update({'docId': docId})
                atual.update({'year': year})
                results.append(atual)

        return results
    
    def getCountries(self, country):

        df = self.read_dataframe()
        
        countries = []
        for countryDF in df['Country']:
            if not countryDF in countries:
                countries.append(countryDF)
                
        return countries
    
    def firstRanking(self, rankingList, country, year):

        collection = Mongo("aprioriResults").collection

        allData = collection.find({"docId": self.docId, "country": country, "year": year})

        if len(list(allData)) == 0:

            dfData = self.read_dataframe()

            dfCountry = dfData[dfData['Country'] == country]
            dfCountryYear = dfCountry[dfCountry['Date'].apply(lambda x: x.year == year)]

            compraID = list(dfCountryYear.BillNo.drop_duplicates())

            records = []
            for id in compraID:
                records.append(list(dfData[dfData.BillNo == id].Itemname))

            allData = self.createAssociationRules(records, self.docId, country, year)

            collection.insert_many(allData)

        dataResult = []

        for item in rankingList:

            dataDB = collection.find({"docId": self.docId, "product": item, "country": country, "year": year}).sort("confidence", pymongo.DESCENDING)
            dataListDB = list(dataDB)

            if len(dataListDB) > 0:
                dataListDB[0].pop('_id')
                dataDB = dataListDB[0]
            else:
                dataDB = {
                    "product": item,
                    "consequent": "Undefined",
                    "confidence": 0,
                    "support": 0,
                    "lift": 0
                }

            dataResult.append(dataDB)

        return dataResult


        



        

        
