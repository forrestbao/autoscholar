import tensorflow as tf
from tensorflow import keras
# import keras
from tensorflow.keras.layers import Embedding, Dense, Bidirectional, LSTM
import pickle
import config as cfg
import sklearn
import numpy as np
import matplotlib.pyplot as plt

class CharRNN():
    def __init__(self):
        self.num_epochs = 60
        self.batch_size = 64
        self.learning_rate = 1e-3
        self.checkpoint_path = 'model.h5'
        cp_callback = keras.callbacks.ModelCheckpoint(
            filepath=self.checkpoint_path, 
            monitor='val_acc',
            save_best_only=True,
            verbose=1)
        es_callback = keras.callbacks.EarlyStopping(monitor='loss',
                                                    min_delta=0,
                                                    patience=10,
                                                    verbose=0,
                                                    mode='auto')
        self.fit_callbacks = [cp_callback, es_callback]

    def build_model(self, numClass = 200):
        self.model = keras.Sequential()
        self.model.add(Embedding(256, 256, mask_zero=True))
        # self.model.add(Dense(32, activation='relu'))
        self.model.add(LSTM(1024, return_sequences=False, dropout=0.5))
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

        self.model.compile(keras.optimizers.Adam(learning_rate=self.learning_rate), 
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True), 
            metrics=['accuracy'])

        self.model.summary()

        history = self.model.fit(x=X, y=y, batch_size=self.batch_size,
                                epochs=self.num_epochs, 
                                validation_split=0.3, 
                                callbacks=self.fit_callbacks)
        plt.figure(figsize=(5, 6))
        try:
            ax1 = plt.subplot(211)
            plt.plot(history.history['loss'])
            if 'val_loss' in history.history:
                plt.plot(history.history['val_loss'])
            ax1.set_title('Model loss')
            ax1.set_ylabel('Loss')
            ax1.set_xlabel('Epoch')
            ax1.legend(['Train loss', 'Validation loss'], loc='upper right')
            ax2 = plt.subplot(212)
            plt.plot(history.history['acc'])
            plt.plot(history.history['val_acc'])
            ax2.set_title('Model Acc')
            ax2.set_ylabel('Acc')
            ax2.set_xlabel('Epoch')
            ax2.legend(['Train acc', 'Validation acc'], loc='upper right')
            plt.savefig('history.png')
        except Exception as e:
            print("\nException caught:\n", e, "\n")
        finally:
            plt.close()

    def predict(self, X):
        y = self.model.predict(X)
        return np.argmax(y, axis=1)

if __name__ == '__main__':
    gpus = tf.config.experimental.list_physical_devices('GPU')
    if gpus:
        try:
            # Currently, memory growth needs to be the same across GPUs
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
                logical_gpus = tf.config.experimental.list_logical_devices('GPU')
                print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Memory growth must be set before GPUs have been initialized
            print(e)
    model = CharRNN()
    model.train()
    
