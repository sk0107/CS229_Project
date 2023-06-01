"""from numpy import array
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D


def prep_data():
    data = {}
    for filename in os.listdir(DATADIR):
        if not filename.lower().endswith(".csv"):
            continue # read only the CSV files
        filepath = os.path.join(DATADIR, filename)
        X = pd.read_csv(filepath, index_col="Date", parse_dates=True)
        # basic preprocessing: get the name, the classification
        # Save the target variable as a column in dataframe for easier dropna()
        name = X["Name"][0]
        del X["Name"]
        cols = X.columns
        X["Target"] = (X["Close"].pct_change().shift(-1) > 0).astype(int)
        X.dropna(inplace=True)
        # Fit the standard scaler using the training dataset
        index = X.index[X.index > TRAIN_TEST_CUTOFF]
        index = index[:int(len(index) * TRAIN_VALID_RATIO)]
        scaler = StandardScaler().fit(X.loc[index, cols])
        # Save scale transformed dataframe
        X[cols] = scaler.transform(X[cols])
        data[name] = X
def cnnpred_2d(seq_len=60, n_features=82, n_filters=(8,8,8), droprate=0.1):
    "2D-CNNpred model according to the paper"
    model = Sequential([
        Input(shape=(seq_len, n_features, 1)),
        Conv2D(n_filters[0], kernel_size=(1, n_features), activation="relu"),
        Conv2D(n_filters[1], kernel_size=(3,1), activation="relu"),
        MaxPool2D(pool_size=(2,1)),
        Conv2D(n_filters[2], kernel_size=(3,1), activation="relu"),
        MaxPool2D(pool_size=(2,1)),
        Flatten(),
        Dropout(droprate),
        Dense(1, activation="sigmoid")
    ])
    return model"""

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import seaborn as sns 
import matplotlib.pyplot as plt
from numpy import array

import tensorflow as tf
from tensorflow.keras.models import Sequential

from keras.layers import Dense,RepeatVector
from keras.layers import Flatten
from keras.layers import TimeDistributed
from keras.layers.convolutional import Conv1D
from keras.layers.convolutional import MaxPooling1D

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import utils as utils
import clean_data_final as clean

def clean_data(X_train, y_train, X_test, y_test):
    for final_array in [X_train, y_train, X_test, y_test]:
        dates = final_array[:, 0]
        difference = pd.Series(dates)-dates[0]
        df_diff = pd.DataFrame(difference) #find diff since original date
        df_diff['weeks'] = df_diff / pd.Timedelta(weeks=1) # convert to weeks
        weeks_array = pd.DataFrame(df_diff['weeks'])
        weeks_array = np.array(weeks_array.values.tolist()) # convert back to numpy


        final_array = np.delete(final_array, 0, axis=1) # remove the original datetime column
    return X_train, y_train, X_test, y_test
def cnn(df):
   # data = pd.read_csv('data.csv')

    ### BARD
    # Split the data into train and test sets
    X_train, y_train, X_test, y_test = utils.split_train_test(df, 0.8)

    X_train, y_train, X_test, y_test = clean_data(X_train, y_train, X_test, y_test)
    # Assuming you have your input data X and target variable y

    # Pad the input data to increase the input size
    # Define the input shape based on the length of the time series
    input_shape = (X_train.shape[1], 1)

    # Reshape the input data to match the expected input shape of the CNN
    X_train = X_train.reshape(X_train.shape[0], input_shape[0], input_shape[1])
    X_test = X_test.reshape(X_test.shape[0], input_shape[0], input_shape[1])

    # Create the CNN model
    model = Sequential()
    model.add(Conv1D(filters=32, kernel_size=3, activation='relu', input_shape=input_shape))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(64, activation='relu'))
    model.add(Dense(1))  # Output layer with 1 neuron for regression

    # Compile the model
    model.compile(loss='mse', optimizer='adam')

    # Train the model
    model.fit(X_train, y_train, epochs=10, batch_size=32)

    # Evaluate the model on the test data
    loss = model.evaluate(X_test, y_test)

    # Once the model is trained, you can use it for prediction
    predictions = model.predict(X_test)

    # Once the model is trained, you can use it for prediction
    # Assuming you have a new data sample X_test for prediction
    X_test_padded = np.pad(X_test, ((0, 0), (padding_size, padding_size)), mode='constant')
    X_test_padded = np.reshape(X_test_padded, (X_test_padded.shape[0], X_test_padded.shape[1], 1))
    predictions = model.predict(X_test_padded)

"""
    # Reshape the data for Keras
   # X_train = X_train.values.reshape(-1, 1, 12)
    #X_test = X_test.values.reshape(-1, 1, 12)

    # Create the model
    model = Sequential()
    model.add(Conv1D(32, 3, activation='relu', input_shape=(1, 12)))
    model.add(MaxPooling1D(2))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))

    # Compile the model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Train the model
    model.fit(X_train, y_train, epochs=10)

    # Evaluate the model
    score = model.evaluate(X_test, y_test, verbose=0)
    print('Test loss:', score[0])
    print('Test accuracy:', score[1])

    ### END BARD
    data = utils.split_train_test(df, 1, split_xy=False)[0]
    
    timestep = 30

    X= []
    Y=[]

    raw_data=data

    for i in range(len(raw_data)- (timestep)):
        X.append(raw_data[i:i+timestep])
        Y.append(raw_data[i+timestep])


    X=np.asanyarray(X)
    Y=np.asanyarray(Y)


    k = 850
    print()
    Xtrain = X[:k,:,:]  
    Ytrain = Y[:k]    

    model = Sequential()
    model.add(Conv1D(filters=128, kernel_size=2, activation='relu', input_shape=(30, 1)))
    model.add(Conv1D(filters=128, kernel_size=2, activation='relu'))
    model.add(Conv1D(filters=128, kernel_size=2, activation='relu'))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(100, activation='relu'))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    # fit model
    model.fit(Xtrain, Ytrain, epochs=200, verbose=0)"""



cnn('df_all')
print("hello")
