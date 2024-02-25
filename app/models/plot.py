import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO
import pandas as pd
import base64

class Plot():
    def __init__(self, filePath):
        self.filePath = filePath

    def read_dataframe(self):

        df = pd.read_csv(self.filePath, sep=';', low_memory=False)

        df.dropna(subset=["Itemname"],inplace=True)

        df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x, "%d.%m.%Y %H:%M"))

        return df
    
    def create_plot(self, eixoX, eixoY, year):

        fig, ax = plt.subplots()
        plt.barh(eixoX, eixoY)

        plt.ylabel('Itemname')
        plt.xlabel('Quantity')
        plt.title(f'Quantidade por Item - {year}')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png', transparent=True)
        buffer.seek(0)

        plot_data = base64.b64encode(buffer.read()).decode()

        buffer.close()
        plt.close()

        return plot_data

    def generate_plot(self, country):

        df = self.read_dataframe();
        
        countryDF = df[df['Country'] == country]

        # Lista de anos na Base de dados
        years = []
        for date in countryDF['Date']:
            if not date.year in years:
                years.append(date.year)

        dfFirstYear = countryDF[countryDF['Date'].apply(lambda x: x.year == years[0])]
        dfSecondYear = countryDF[countryDF['Date'].apply(lambda x: x.year == years[1])]

        dfRankingFirstYear = dfFirstYear.groupby('Itemname')['Quantity'].sum().reset_index()
        dfRankingFirstYear = dfRankingFirstYear.sort_values(by='Quantity', ascending=False).head(10)

        dfRankingSecondYear = dfSecondYear.groupby('Itemname')['Quantity'].sum().reset_index()
        dfRankingSecondYear = dfRankingSecondYear.sort_values(by='Quantity', ascending=False).head(10)

        plot_data1 = self.create_plot(dfRankingFirstYear['Itemname'][::-1], dfRankingFirstYear['Quantity'][::-1], years[0])
        plot_data2 = self.create_plot(dfRankingSecondYear['Itemname'][::-1], dfRankingSecondYear['Quantity'][::-1], years[1])

        return years[:2], plot_data1, list(dfRankingFirstYear['Itemname']), plot_data2, list(dfRankingSecondYear['Itemname'])