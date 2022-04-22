from gc import callbacks
import os
from tabnanny import verbose

# =================================== IGNORE CERTAIN ERRORS ===================================
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
# =================================== IGNORE CERTAIN ERRORS ===================================

import numpy            as np
import tensorflow       as tf
import numpy.typing     as npt

from typing             import Any, List
from tensorflow         import keras

# =================================== CONSTANTS DEFINITIONS ===================================

NUMBER_OF_WORDS : int = 100
EMBEDDING_DIMENSIONALITY : int = 200
MAX_EPHOCS : int = 5000

# =================================== CREATION OF WORD EMBEDDINGS ===================================

word_embeddings : List[npt.NDArray[np.float64]] = []
for _ in range(NUMBER_OF_WORDS):
    random_array : npt.NDArray[np.float64] = np.random.rand(EMBEDDING_DIMENSIONALITY).astype(np.float64)
    word_embeddings.append(random_array / np.linalg.norm(random_array))
#for (index, word_embedding) in enumerate(word_embeddings): print(f"📄 Word Embedding {index}:", word_embedding)

# =================================== ACHIEVE REAL SENTENCE EMBEDDING ===================================

matrix_embeddings : npt.NDArray[np.float64] = np.array(word_embeddings)
sum_embeddings : npt.NDArray[np.float64] = np.sum(matrix_embeddings, axis=0)
sentence_embedding : npt.NDArray[np.float64] = sum_embeddings / np.linalg.norm(sum_embeddings)
#print(f"📄 Sentence Embedding:", sentence_embedding)

# =================================== NEURAL NETWORK DEVELOPMENT - BUILD ===================================

class LayerCustom(keras.layers.Layer):

    def __init__(self):
        super(LayerCustom, self).__init__()

    def build(self, input_shape):
        # Attributes for other layer charactheristics
        self.iteration : int = 0
        # Weights Initialization
        self.w = self.add_weight(
            shape=(input_shape[-1], 1),
            initializer="random_normal",
            trainable=True,
        )

    def call(self, inputs):
        return tf.matmul(inputs, self.w)

#print()
model = keras.Sequential()
model.add(keras.layers.Input(matrix_embeddings.transpose().shape))
model.add(LayerCustom())

# =================================== NEURAL NETWORK DEVELOPMENT - SAVE ===================================

#model.summary()
#dot_img_file = './model_1.png'
#keras.utils.plot_model(model, to_file=dot_img_file, show_shapes=True)

# =================================== NEURAL NETWORK DEVELOPMENT - Compile ===================================

def euclidean_distance_loss(y_true, y_pred):
    """
    Euclidean distance loss
    https://en.wikipedia.org/wiki/Euclidean_distance
    :param y_true: TensorFlow/Theano tensor
    :param y_pred: TensorFlow/Theano tensor of the same shape as y_true
    :return: float
    """
    return keras.backend.sqrt(keras.backend.sum(keras.backend.square(y_pred - y_true), axis=-1))

model.compile(
    optimizer=keras.optimizers.RMSprop(),
    loss=euclidean_distance_loss,
    metrics=[keras.metrics.CosineSimilarity()]
)

# =================================== NEURAL NETWORK DEVELOPMENT - TRAIN ===================================

class CallbackWeightTreshold(keras.callbacks.Callback):

    def __init__(self, max_ephocs: int, constant_tau : int = 100) -> None:
        super().__init__()
        self.constant_tau : int = constant_tau
        self.max_ephocs : int = max_ephocs
        self.constant_denominator : int = constant_tau * max_ephocs

    def on_epoch_end(self, epoch, logs=None):
        threshold : float = ( epoch + 1 ) / self.constant_denominator

        full_weights = self.model.get_weights()
        weights : npt.NDArray[np.float64] = full_weights[0]
        weights[weights < threshold] = 0.0
        weights = weights.astype(np.float64)

        full_weights[0] = weights
        self.model.set_weights(full_weights)

x_train = np.transpose(matrix_embeddings).reshape((1, EMBEDDING_DIMENSIONALITY, NUMBER_OF_WORDS))
y_train = sentence_embedding.reshape((1, EMBEDDING_DIMENSIONALITY, 1))

callbacks : List[keras.callbacks.Callback] = [tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10, restore_best_weights=True),
    CallbackWeightTreshold(NUMBER_OF_WORDS, MAX_EPHOCS)]
history = model.fit(x_train, y_train, epochs=MAX_EPHOCS, callbacks=callbacks, verbose=False)

number_of_ephocs_ran : int = len(history.history['loss'])
last_loss : float = history.history['loss'][-1]
last_cosine_similarity : float = history.history['cosine_similarity'][-1]

number_of_weights : int = model.weights[0].shape[0]
number_of_zero_weights : int = len(np.where( model.weights != 0.0 ))

print(f"💯 Best 'number of epochs ran': {number_of_ephocs_ran}")
print(f"💯 Best 'loss': {last_loss}")
print(f"💯 Best 'cosine_similarity': {last_cosine_similarity}")

print(f"💯 Count 'Non-zero weights': {number_of_zero_weights} / {number_of_weights}")