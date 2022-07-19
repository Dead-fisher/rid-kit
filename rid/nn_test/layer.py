from typing import List, Union, Sequence
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class Linear(keras.layers.Layer):
    def __init__(
        self, 
        units: int = 32,
        name: str = "Linear",
    ):
        super(Linear, self).__init__(name=name)
        self.units = units

    def build(self, input_shape):
        initer_w = tf.random_normal_initializer(
                    stddev=stddev/np.sqrt(shape[1]+outputs_size), seed=seed)
        self.w = self.add_weight(
            shape=(input_shape[-1], self.units),
            initializer=initializer,
            trainable=True,
        )
        self.b = self.add_weight(
            shape=(self.units,), initializer=initializer, trainable=True
        )

    def call(self, inputs):
        return tf.matmul(inputs, self.w) + self.b


class DataTransform(keras.layers.Layer):
    def __init__(
        self,
        angular_mask: Union[Sequence, np.ndarray],
        name: str = "transform"
    ):
        super(DataTransform, self).__init__(name=name)
        angular_mask = tf.constant(angular_mask)
        self.angular_mask_boolean = (angular_mask == 1)
        self.non_angular_mask_boolean = (angular_mask == 0)
    
    def call(self, inputs):
        angular_cv = tf.boolean_mask(
                inputs, self.angular_mask_boolean, axis=1, name='angular_cv'
                )
        non_angular_cv = tf.boolean_mask(
                inputs, self.non_angular_mask_boolean, axis=1, name='non_angular_cv'
                )
        return tf.concat([tf.cos(angular_cv), tf.sin(angular_cv), non_angular_cv], 1)        



# linear_layer = Linear(4)

# inputs = keras.Input(shape=(1,2))

# y = linear_layer(inputs)
# print(linear_layer.w)
# print(linear_layer.b)
x = tf.ones((1, 2))
linear_layer = Linear(4)
y = linear_layer(x)
print(y)