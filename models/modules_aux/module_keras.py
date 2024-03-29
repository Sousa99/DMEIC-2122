import os
import sys
import math
import warnings


# =================================== IGNORE CERTAIN ERRORS ===================================
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# =================================== IGNORE CERTAIN ERRORS ===================================

import tensorflow                   as tf
import numpy                        as np

from typing                         import Any, Dict, Iterable, List
from tensorflow                     import keras

import modules_aux.module_exporter  as module_exporter

NDArray = Iterable

# =================================== IGNORE CERTAIN ERRORS ===================================
tf.logging.set_verbosity(tf.logging.ERROR)

warnings.filterwarnings('ignore', module = 'tensorflow')
warnings.filterwarnings('ignore', module = 'keras')
# =================================== IGNORE CERTAIN ERRORS ===================================

# ===================================== PRIVATE FUNCTIONS =====================================

def euclidean_distance_loss(y_true, y_pred):
    """
    Euclidean distance loss
    https://en.wikipedia.org/wiki/Euclidean_distance
    :param y_true: TensorFlow/Theano tensor
    :param y_pred: TensorFlow/Theano tensor of the same shape as y_true
    :return: float
    """
    return keras.backend.sqrt(keras.backend.sum(keras.backend.square(y_pred - y_true), axis=-1))

# =================================== PRIVATE CLASS DEFINITIONS ===================================

# ----------------------------------------- Custom Layers -----------------------------------------
class LayerCustomRezaii(keras.layers.Layer):
    def __init__(self):
        super(LayerCustomRezaii, self).__init__()
    def build(self, input_shape):
        # Attributes for other layer charactheristics
        self.iteration : int = 0
        # Weights Initialization
        self.w = self.add_weight(
            name='main_weights',
            shape=(input_shape[-1], 1),
            initializer="random_normal",
            trainable=True,
        )
    def call(self, inputs):
        return tf.tensordot(inputs, self.w, [[2], [0]])

# --------------------------------------- Custom Callbacks ---------------------------------------
class CallbackWeightTreshold(keras.callbacks.Callback):

    def __init__(self, max_ephocs: int, constant_tau : int = 100) -> None:
        super().__init__()
        self.constant_tau : int = constant_tau
        self.max_ephocs : int = max_ephocs
        self.constant_denominator : int = constant_tau * max_ephocs

    def on_epoch_end(self, epoch, logs=None):
        threshold : float = ( epoch + 1 ) / self.constant_denominator

        full_weights = self.model.get_weights()
        weights : NDArray[np.float64] = full_weights[0]
        weights[weights < threshold] = 0.0
        weights = weights.astype(np.float64)

        full_weights[0] = weights
        self.model.set_weights(full_weights)

# =================================== PUBLIC CLASS DEFINITIONS ===================================

class NeuralNetworkRezaii():

    TMP_DIRECTORY = os.path.join(module_exporter.get_tmp_directory(['RezaiiNN']), 'model_checkpoint')

    def __init__(self, matrix_embeddings: NDArray[np.float64], sentence_embedding: NDArray[np.float64], ephocs: int = 5000) -> None:
        self.matrix_embeddings : NDArray[np.float64] = matrix_embeddings
        self.sentence_embedding : NDArray[np.float64] = sentence_embedding

        self.epochs : int = ephocs
        self.number_of_words : int = self.matrix_embeddings.shape[0]
        self.embedding_dimensionality : int = self.matrix_embeddings.shape[1]

        # Develop Model
        self.model = keras.Sequential()
        self.model.add(keras.layers.InputLayer(self.matrix_embeddings.transpose().shape))
        self.model.add(LayerCustomRezaii())

        self.metrics : List[keras.metrics.Metric | str] = ['cosine']
        self.callbacks : List[keras.callbacks.Callback] = [tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10),
            CallbackWeightTreshold(self.number_of_words, self.epochs),
            tf.keras.callbacks.ModelCheckpoint(filepath=self.TMP_DIRECTORY, save_weights_only=True, monitor='loss', mode='max', save_best_only=True)]

        self.model.compile(optimizer=keras.optimizers.Adam(), loss=euclidean_distance_loss, metrics=self.metrics)

    def train_model(self) -> Dict[str, Any]:
        x_train = np.transpose(self.matrix_embeddings).reshape((1, self.embedding_dimensionality, self.number_of_words))
        y_train = self.sentence_embedding.reshape((1, self.embedding_dimensionality, 1))

        history = self.model.fit(x_train, y_train, epochs=self.epochs, callbacks=self.callbacks, verbose=False)

        number_of_ephocs_ran : int = len(history.history['loss'])

        history_loss : List[float] = history.history['loss']
        history_loss_filtered : List[float] = list(filter(lambda loss_value: loss_value is not None and not math.isnan(loss_value), history_loss))
        last_loss : float = history_loss_filtered[-1]

        history_cosine_similarity : List[float] = history.history['cosine_proximity']
        history_cosine_similarity_filtered : List[float] = list(filter(lambda cosine_similarity_value: cosine_similarity_value is not None and not math.isnan(cosine_similarity_value), history_cosine_similarity))
        last_cosine_similarity : float = history_cosine_similarity_filtered[-1]

        number_of_zero_weights : int = len(np.where(self.model.weights[0] != 0.0))
        ratio_zero_weights : float = number_of_zero_weights / self.model.weights[0].shape[0].value

        return { '#ephocs': number_of_ephocs_ran, 'ratio #zero_weights': ratio_zero_weights,
            'model loss': last_loss, 'model cosine similarity': last_cosine_similarity }