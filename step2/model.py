import keras
from keras.layers import Embedding, Dense, Bidirectional, LSTM
import pickle
import config as cfg
import sklearn
import numpy as np
import matplotlib.pyplot as plt

class CharRNN():
    def __init__(self):
        self.checkpoint_path = 'model.h5'

    def build_model(self, numClass = 200):
        self.model = keras.Sequential()
        self.model.add(Embedding(256, 32, mask_zero=True))
        self.model.add(Dense(32, activation='relu'))
        self.model.add(Bidirectional(LSTM(32, return_sequences=False)))
        # self.model.add(Dense(128, activation='relu'))
        self.model.add(Dense(numClass))
    
    def load_model(self):
        self.model = keras.models.load_model(self.checkpoint_path)

    def train(self):
        X, y = None, None
        with open(cfg.preprocessed_file, "rb") as f:
            X, y = pickle.load(f)
            
        X, y = sklearn.utils.shuffle(X, y)
        '''
        size = len(y)
        split = int(size * 0.7)
        X_train, y_train = X[:split], y[:split]
        X_test, y_test = X[split:], y[split:]
        '''
        print(X.shape)
        self.build_model(np.max(y)+1)

        num_epochs = 20
        self.model.compile(keras.optimizers.Adam(), loss='sparse_categorical_crossentropy', metrics=['accuracy'])

        self.model.summary()

        cp_callback = keras.callbacks.ModelCheckpoint(
            filepath=self.checkpoint_path, 
            verbose=1)

        history = self.model.fit(x=X, y=y, 
                                epochs=num_epochs, 
                                validation_split=0.3, 
                                callbacks=[cp_callback, keras.callbacks.EarlyStopping(monitor='val_loss',
                                                                        min_delta=0,
                                                                        patience=10,
                                                                        verbose=0,
                                                                        mode='auto')])
        plt.figure(figsize=(5, 2))
        try:
            plt.plot(history.history['loss'])
            plt.plot(history.history['val_loss'])
            plt.title('Model loss')
            plt.ylabel('Loss')
            plt.xlabel('Epoch')
            plt.legend(['Train', 'Validation'], loc='upper right')
            plt.savefig('history.png')
        except Exception as e:
            print("\nException caught:\n", e, "\n")
        finally:
            plt.close()

    def predict(self, X):
        y = self.model.predict(X)
        return np.argmax(y, axis=1)

if __name__ == '__main__':
    model = CharRNN()
    model.train()
    
