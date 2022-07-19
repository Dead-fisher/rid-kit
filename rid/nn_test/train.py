import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import numpy as np
from rid.nn.data import get_dataset
from rid.nn.model import ResNet


@tf.function
def train_step(images, labels, optimizer):
    with tf.GradientTape() as tape:
        # training=True is only needed if there are layers with different
        # behavior during training versus inference (e.g. Dropout).
        energy, forces = model(images, training=True)
        force_dif = labels - forces
        forces_norm = tf.reshape(tf.reduce_sum(
            forces * forces, axis=1), [-1, 1])
        forces_dif_norm = tf.reshape(tf.reduce_sum(
            force_dif * force_dif, axis=1), [-1, 1])
        l2_loss = tf.reduce_mean(forces_dif_norm, name='l2_loss')
    rel_error_k = forces_dif_norm / (1E-8 + forces_norm)

    gradients = tape.gradient(l2_loss, model.trainable_variables)
    optimizer.apply_gradients(zip(gradients, model.trainable_variables))
    error = tf.mean(tf.sqrt(l2_loss))
    rel_error = tf.mean(tf.sqrt(rel_error_k))
    return error, rel_error


def run_train(config):
    optimizer = tf.keras.optimizers.Adam(learning_rate=config.learning_rate)
    train_loss = tf.keras.metrics.Mean(name='train_loss')
    train_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='train_accuracy')
    test_loss = tf.keras.metrics.Mean(name='test_loss')
    test_accuracy = tf.keras.metrics.SparseCategoricalAccuracy(name='test_accuracy')

    epochs = 1  # In practice you need at least 20 epochs to generate nice digits.
    save_dir = "./"

    for epoch in range(epochs):
        print("\nStart epoch", epoch)

        for step, real_images in enumerate(dataset):
            # Train the discriminator & generator on one batch of real images.
            d_loss, g_loss, generated_images = train_step(real_images)

            # Logging.
            if step % 200 == 0:
                # Print metrics
                print("discriminator loss at step %d: %.2f" % (step, d_loss))
                print("adversarial loss at step %d: %.2f" % (step, g_loss))

                # Save one generated image
                img = tf.keras.preprocessing.image.array_to_img(
                    generated_images[0] * 255.0, scale=False
                )
                img.save(os.path.join(save_dir, "generated_img" + str(step) + ".png"))

            # To limit execution time we stop after 10 steps.
            # Remove the lines below to actually train the model!
            if step > 10:
                break