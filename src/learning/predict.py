import pandas as pd
from collections import deque
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LSTM
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
from tensorflow.keras.optimizers import Adam
import sys

session_config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
sess = tf.compat.v1.Session(config=session_config)

COIN = sys.argv[1]
TIME_SERIES_LENGTH = 7


df = pd.read_csv('../../data/processed_dataset.csv')

df['future'] = df[f"{COIN}_usd"].shift(-1)
df.dropna(inplace=True)


# Values for our target column
def price_variation(present, future):
    if float(future) > float(present):
        return 1
    else:
        return 0


drops = ['target', 'timestamp']
# Set to True to test training without data on the pandemic
no_covid = False
if no_covid:
    for c in df.columns:
        if 'death' in c or 'confirmed' in c:
            drops.append(c)


def preprocess_df(df):
    df = df.drop(['future'], axis=1)

    sequential_data = []
    prev_days = deque(maxlen=TIME_SERIES_LENGTH)
    for i, row in df.iterrows():
        prev_days.append([row[c] for c in df.drop(drops, axis=1).columns])
        if len(prev_days) == TIME_SERIES_LENGTH:
            sequential_data.append([np.array(prev_days), row['target']])
    random.shuffle(sequential_data)

    random.shuffle(sequential_data)
    xs = []
    ys = []
    for seq, target in sequential_data:
        xs.append(seq)
        ys.append(target)

    return np.array(xs), np.array(ys)


df['target'] = list(map(price_variation, df[f"{COIN}_usd"], df["future"]))

x, y = preprocess_df(df)



