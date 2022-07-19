from typing import Optional
import numpy as np
import tensorflow as tf


def get_dataset(
        data: np.ndarray,
        shuffle_buffer: int = 500,
        batch_size: int = 32,
        seed: Optional[float]
    ):
    assert data.shape[1] % 2 == 0, "Invalid data shape."
    cv_dim = int(data.shape[1] // 2)
    dataset = tf.data.Dataset.from_tensor_slices(
        (data[:, :cv_dim], data[:, cv_dim:])
    )
    dataset = dataset.shuffle(buffer_size=shuffle_buffer, seed=seed)
    dataset = dataset.batch(batch_size)
    return dataset
