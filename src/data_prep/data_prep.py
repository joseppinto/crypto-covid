import pandas as pd
from Adafruit_IO import Client
import ast
import sys
from sklearn import preprocessing
from collections import deque
import numpy as np
import random
import time
import tensorflow as tf
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense, Dropout, LSTM, CuDNNLSTM, BatchNormalization
from tensorflow.keras.callbacks import TensorBoard, ModelCheckpoint

if len(sys.argv) < 4:
    exit(-1)

# Get path for dataset we'll create
OUTPUT_DIR = sys.argv[1]

CURRENCY = sys.argv[2]
if CURRENCY not in ['bitcoin', 'ethereum', 'ripple', 'litecoin']:
    print("Invalid arguments")
    exit(-1)

PRED_PERIOD = sys.argv[3]
if PRED_PERIOD not in ['5min', 'hour', 'day']:
    print("Invalid arguments")
    exit(-1)

FUTURE_STEPS = {"5min": 1, "hour": 12, "day": 288}

IO_USERNAME = '62random'
IO_KEY = 'aio_qzCd63hW93tAubENWmQ7H8UMwgJq'
IO_FEED = 'crypto-covid'

# IO_USERNAME = os.environ.get("IO_USERNAME")
# IO_KEY = os.environ.get(IO_KEY)

# Instance adafruit client and get data from specific feed
aio = Client(IO_USERNAME, IO_KEY)
data = aio.data(IO_FEED)


df = pd.DataFrame()

for d in data:
    row = ast.literal_eval(d.value)
    row['timestamp'] = d.created_epoch
    df = df.append(row, ignore_index=True)

df = df.sort_values(['timestamp'], ascending=[1])


# Now that the dataframe is imported from adafruit, we need to
# create the target columns (fute value of prices for each row)

# Values for our target column
def price_variation(present, future):
    if float(future) > float(present):
        return 1
    else:
        return 0


# Function to process dataset
def preprocess_df(df):
    df = df.drop(['future'], axis=1)

    for col in df.columns:
        if col != "target":
            df[col] = preprocessing.scale(df[col].values)
            df[col] = df[col].astype(float).pct_change()
            df[col] = df[col].replace([np.nan], 0)
            df[col] = df[col].replace([np.inf], 1)
            df[col] = df[col].replace([-np.inf], -1)
    df.dropna(inplace=True)
    sequential_data = []
    prev_days = deque(maxlen=50*FUTURE_STEPS[PRED_PERIOD])
    for i, row in df.iterrows():
        prev_days.append([row[c] for c in df.drop(['target', 'timestamp'], axis=1).columns])
        if len(prev_days) == 50*FUTURE_STEPS[PRED_PERIOD]:
            sequential_data.append([np.array(prev_days), row['target']])
    random.shuffle(sequential_data)

    # balance to fifty fifty
    buys = []
    sells = []
    for seq, target in sequential_data:
        if target > 0:
            buys.append([seq, target])
        else:
            sells.append([seq, target])

    lower = min(len(buys), len(sells))

    buys = buys[:lower]
    sells = sells[:lower]

    sequential_data = buys + sells
    random.shuffle(sequential_data)
    xs = []
    ys = []
    for seq, target in sequential_data:
        xs.append(seq)
        ys.append(target)

    return np.array(xs), np.array(ys)



df["future"] = df[f"{CURRENCY}_usd"].shift(FUTURE_STEPS[PRED_PERIOD])
df = df.iloc[:-FUTURE_STEPS[PRED_PERIOD]]
df['target'] = list(map(price_variation, df[f"{CURRENCY}_usd"], df["future"]))


times = sorted(df.timestamp.values)
last_5pct = times[-int(0.1*len(times))]

valid = df[df['timestamp'] >= last_5pct]
train = df[df['timestamp'] < last_5pct]


train_x, train_y = preprocess_df(train)
valid_x, valid_y = preprocess_df(valid)

# Model settings
EPOCHS = 100
for BATCH_SIZE in [64, 128]:
    for LEARNING_RATE in [0.001, 0.005, 0.01, 0.05]:
        NAME = f"{CURRENCY}-{PRED_PERIOD}-LR={LEARNING_RATE:.3f}-BATCH={BATCH_SIZE:03d}"

        model = Sequential()
        model.add(LSTM(128, input_shape=(train_x.shape[1:]), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())

        model.add(LSTM(128, input_shape=(train_x.shape[1:]), return_sequences=True))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())

        model.add(LSTM(128, input_shape=(train_x.shape[1:])))
        model.add(Dropout(0.2))
        model.add(BatchNormalization())

        model.add(Dense(32, activation="relu"))
        model.add(Dropout(0.2))

        model.add(Dense(2, activation="softmax"))

        opt = tf.keras.optimizers.Adam(lr=LEARNING_RATE, decay=1e-6)
        model.compile(loss='sparse_categorical_crossentropy', optimizer=opt, metrics=['accuracy'])

        tensorboard = TensorBoard(log_dir=f'logs/{NAME}')
        filepath = "RNN_Final-{epoch:03d}-{val_acc:.3f}"
        checkpoint = ModelCheckpoint("models/{}.model".format(filepath, monitor='val_acc', verbose=1, save_best_only=True, mode='max'))

        history = model.fit(train_x, train_y,
                            batch_size=BATCH_SIZE,
                            epochs=EPOCHS,
                            validation_data=(valid_x, valid_y),
                            callbacks=[tensorboard, checkpoint])

#df.to_csv(OUTPUT_DIR + f"{CURRENCY}_{PRED_PERIOD}.csv", index=False)