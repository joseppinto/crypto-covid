import pandas as pd
import numpy as np
from sklearn import preprocessing

df = pd.read_csv("../../data/dataset.csv", index_col='timestamp')


coins = ['bitcoin_usd', 'ethereum_usd', 'ripple_usd', 'litecoin_usd']
df = df.replace({0: np.nan, 0.0: np.nan})

# Only track price records from the moment all coins are available
df = df.filter(df[~np.isnan(df['ethereum_usd'])].index, axis=0)


df_covid = df.filter(df[df['China_confirmed'] != 0].index, axis=0)


# Not gonna use sentiment data for now
df.drop(['bitcoin_web', 'ethereum_web', 'ripple_web', 'litecoin_web'], axis=1, inplace=True)


# Scale data
x = df.values
min_max_scaler = preprocessing.MinMaxScaler()
x_scaled = min_max_scaler.fit_transform(x)
df_normalized = pd.DataFrame(x_scaled, columns=df.columns, index=df.index)

df = df.pct_change().fillna(0)
df = (df - df.mean()) / (df.max() - df.min())


df.to_csv("../../data/processed_dataset.csv")
