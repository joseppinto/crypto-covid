import pandas as pd
from collections import deque
import numpy as np
import random
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization, LSTM
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint
from tensorflow.keras.optimizers import Adam

session_config = tf.compat.v1.ConfigProto(gpu_options=tf.compat.v1.GPUOptions(allow_growth=True))
sess = tf.compat.v1.Session(config=session_config)

COIN = 'bitcoin'
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

nsamples = 60  # a month

train_x = x[:-nsamples]
train_y = y[:-nsamples]
valid_x = x[-nsamples:]
valid_y = y[-nsamples:]


# balance test set to 50-50
values, counts = np.unique(valid_y, return_counts=True)
major = np.argmax(counts)
minor = np.argmin(counts)

major_indices = np.array(range(valid_y.size))[np.isin(valid_y, values[major])]
minor_indices = np.array(range(valid_y.size))[np.isin(valid_y, values[minor])]

major_indices = np.random.choice(major_indices, minor_indices.size)

valid_x = valid_x[np.concatenate([major_indices, minor_indices])]
valid_y = valid_y[np.concatenate([major_indices, minor_indices])]


EPOCHS = 2500
BATCH_SIZE = 128
LEARNING_RATE = 0.0001

number = train_x.shape[1] * train_x.shape[2]

print(number)

NAME = f"{COIN}{'-no_covid' if no_covid else ''}-SL={TIME_SERIES_LENGTH}-LR={LEARNING_RATE:.5f}-BATCH={BATCH_SIZE:03d}"

model = Sequential()
model.add(LSTM(number, return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(LSTM(number, return_sequences=True))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(LSTM(int(number / 2)))
model.add(Dropout(0.2))
model.add(BatchNormalization())

model.add(Dense(int(number / 8), activation="relu"))

model.add(Dense(2, activation="softmax"))

opt = Adam(lr=LEARNING_RATE)
model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

tensorboard = TensorBoard(log_dir=f'logs/{NAME}')
filepath = "RNN_Final-{epoch:04d}-{val_accuracy:.3f}"
checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_accuracy', verbose=1, save_best_only=True, mode='max'))

history = model.fit(train_x, train_y,
                    batch_size=BATCH_SIZE,
                    epochs=EPOCHS,
                    verbose=1,
                    validation_data=(valid_x, valid_y),
                    callbacks=[tensorboard, checkpoint])

