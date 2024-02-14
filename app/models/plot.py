import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
import base64

class Plot():
    def __init__(self, filePath):
        self.filePath = filePath

    def generate_plot(self):
        df = pd.read_csv(self.filePath, sep=';', low_memory=False)

        dfRanking = df.groupby('Itemname')['Quantity'].sum().reset_index()
        dfRanking = dfRanking.sort_values(by='Quantity', ascending=False).head(10)

        fig, ax = plt.subplots()
        plt.barh(dfRanking['Itemname'][::-1], dfRanking['Quantity'][::-1])

        # plt.xticks(rotation=90)
        plt.ylabel('Itemname')
        plt.xlabel('Quantity')
        plt.title('Quantidade por Item')
        plt.tight_layout()

        buffer = BytesIO()
        plt.savefig(buffer, format='png', transparent=True)
        buffer.seek(0)

        plot_data = base64.b64encode(buffer.read()).decode()

        buffer.close()
        plt.close()

        return plot_data, list(dfRanking['Itemname'])