import os
import sys
import tensorflow as tf
import tensorflow.keras as keras
import tensorflow.keras.layers as layers
import numpy as np
import logging
from constants import kbT, beta, N_grid, inverse_f_cvt

tf_precision = tf.float32

class Config(object):
    def __init__(self, cv_dim):
        self.batch_size = 64
        self.n_displayepoch = 200
        # use Batch Normalization or not
        self.useBN = False  # True
        self.num_epoch = 3000
        self.use_mix = False
        self.old_ratio = 7
        self.n_neuron = [4,4,4]
        self.starter_learning_rate = 0.1
        self.decay_steps = 10
        self.decay_steps_inner = 0
        self.decay_rate = 0.96
        self.data_path = './data/data.raw'
        self.restart = False
        self.resnet = True
        self.graph_file = None
        self.cv_dim = cv_dim
        self.display_in_training = True
        self.drop_out_rate = 0
        self.angular_mask = [True, True]

class Reader(object):
    def __init__(self, config):
        # copy from config
        self.data_path = config.data_path
        self.num_epoch = config.num_epoch
        self.batch_size = config.batch_size
        self.cv_dim = config.cv_dim
        self.drop_out_rate = config.drop_out_rate
        self.angular_mask = config.angular_mask

    def prepare(self):
        tr_data_all = np.loadtxt(self.data_path)
        tr_data_all[:, self.cv_dim:] *= inverse_f_cvt
        self.inputs_train_all = tr_data_all[:, :]
        self.train_size_all = self.inputs_train_all.shape[0]
        
    def sample_train(self):
        self.index_count_all += self.batch_size
        if self.index_count_all > self.train_size_all:
            # shuffle the data
            self.index_count_all = self.batch_size
            ind = np.random.choice(self.train_size_all,
                                   self.train_size_all, replace=False)
            self.inputs_train_all = self.inputs_train_all[ind, :]
        ind = np.arange(self.index_count_all -
                        self.batch_size, self.index_count_all)
        return self.inputs_train_all[ind, :]

    def get_train_size(self):
        return self.train_size_all

    def get_batch_size(self):
        return self.batch_size

    def get_data(self):
        return self.inputs_train_all

class Resnet(keras.Model):
    def __init__(self, config):
        super(Resnet, self).__init__()
        self.data_path = config.data_path
        self.n_neuron = config.n_neuron
        self.useBN = config.useBN
        self.n_displayepoch = config.n_displayepoch
        self.starter_learning_rate = config.starter_learning_rate
        self.decay_steps = config.decay_steps
        self.decay_steps_inner = config.decay_steps_inner
        self.decay_rate = config.decay_rate
        self.display_in_training = config.display_in_training
        self.restart = config.restart
        self.resnet = config.resnet
        self.graph_file = config.graph_file
        self.cv_dim = int(config.cv_dim)
        self.angular_mask = np.array(config.angular_mask)
        self.angular_dim = np.sum(self.angular_mask, dtype=int)
        self.non_angular_dim = self.cv_dim - self.angular_dim
        self.angular_mask_boolean = (self.angular_mask == 1)
        self.non_angular_mask_boolean = (self.angular_mask == 0)
        self.graph = False
        
        self.blocklist=[]
        self.dropout_rate = config.drop_out_rate

        self.n_neuron.insert(0, self.cv_dim)
        for i in range(len(self.n_neuron)-1):
            self.blocklist.append(self._one_layer(inputs_size=self.n_neuron[i],outputs_size =self.n_neuron[i+1],
                                                  activation_fn=tf.nn.tanh, stddev=1.0, bavg=0.0, name="linear", seed=1))
        self.final_layer = self._final_layer(self.n_neuron[-1],1,activation_fn=None, stddev=1.0,
                                             name = "o_energy", seed=2)
    
    def _one_layer(self,
                inputs_size,
                outputs_size,
                activation_fn=tf.nn.tanh,
                stddev=1.0,
                bavg=0.0,
                name='linear',
                seed=None):
        initer_w = keras.initializers.RandomNormal(stddev=stddev/np.sqrt(inputs_size+outputs_size), seed = seed)
        initer_b = keras.initializers.RandomNormal(mean=bavg, stddev=stddev, seed=seed)
        layer = layers.Dense(outputs_size,activation=activation_fn,use_bias=True,
                                kernel_initializer=initer_w, bias_initializer=initer_b)
        return layer
    
    def _final_layer(self,
                     inputs_size,
                     outputs_size,
                     activation_fn=None,
                     stddev=1.0,
                     name="linear",
                     seed=None):
        initer_w = keras.initializers.RandomNormal(stddev=stddev/np.sqrt(inputs_size+outputs_size), seed = seed)
        layer = layers.Dense(outputs_size,activation=activation_fn,use_bias=False,
                                kernel_initializer=initer_w)
        return layer
    
    @tf.function
    def call(self, cvs, training= False):
        angles = tf.boolean_mask(cvs, self.angular_mask_boolean, axis=1, name='angles')
        angles = tf.reshape(angles, [-1, self.angular_dim])
        dists = tf.boolean_mask(cvs, self.non_angular_mask_boolean, axis=1, name='dists')
        dists = tf.reshape(dists, [-1, self.non_angular_dim])
        inputs = tf.concat([tf.cos(angles), tf.sin(angles), dists], 1)
        with tf.GradientTape() as t:
            t.watch(cvs)
            x = inputs
            for ii in range(len(self.blocklist)):
                if self.resnet and self.n_neuron[ii] == self.n_neuron[ii+1]:
                    x = x + self.blocklist[ii](x)
                else:
                    x = self.blocklist[ii](x)
                if self.useBN:
                    x = layers.BatchNormalization(axis=-1,momentum=0.99,epsilon=1e-6)(x)
                if training:
                    # print("dropout!")
                    x = layers.Dropout(self.dropout_rate)(x)
                    # print("prediction!")
            energy = self.final_layer(x)
        force = tf.gradients(energy, cvs)
        return force
    
    def train(self, reader):
        reader.prepare()
        inputs = reader.inputs_train_all
        avg_input, scl_input = self.compute_statistic(reader)
        cvs = tf.slice(inputs, [0, 0], [-1, self.cv_dim], name='cvs')
        cvs = (cvs - avg_input) * scl_input
        
        forces_hat = tf.slice(inputs, [0, self.cv_dim], [-1, self.cv_dim], name='forces')
        
        lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
        initial_learning_rate=self.starter_learning_rate, decay_steps=self.decay_steps,
        decay_rate=self.decay_rate, staircase=True)
        self.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=lr_schedule), loss="mse", metrics="mae")
        
        if (self.restart == True):
            self.load_weights('./old_model/checkpoint')
            print("Weights restored.")
        
        if (self.graph == True):
            self = keras.models.load_model("./old_model/saved_model")
            print("Model restored!")
        
        checkpoint_filepath = './old_model/checkpoint'
        model_checkpoint_callback = keras.callbacks.ModelCheckpoint(
            checkpoint_filepath,
            monitor='val_loss',
            verbose=0,
            save_best_only=False,
            save_weights_only=True,
            mode='auto',
            save_freq='epoch',
            options=None,
            initial_value_threshold=None)
        self.fit(cvs, forces_hat, batch_size=200, epochs = 5, callbacks=[model_checkpoint_callback])
        self.save("./old_model/saved_model.h5")
        self.summary()
        
    def compute_statistic(self, reader):
        max_scale = 3.

        dold = reader.get_data()
        da = np.average(dold[:, 0:self.cv_dim], axis=0)
        ds = np.std(dold[:, 0:self.cv_dim], axis=0)
        # da[:self.cv_dih_dim] = 0.0
        da[self.angular_mask_boolean] = 0.0
        if all(ds != 0):
            ds = 1./(ds)
        # ds[:self.cv_dih_dim] = 1.0
        ds[self.angular_mask_boolean] = 1.0
        non_angular_cv = ds[self.non_angular_mask_boolean]
        non_angular_cv[non_angular_cv>max_scale] = max_scale
        ds[self.non_angular_mask_boolean] = non_angular_cv
        
        return da, ds
            

cv_dim = 2
config = Config(cv_dim)
reader = Reader(config)
mynet = Resnet(config)
mynet.train(reader)

angles = tf.reshape(tf.constant([-2.5,2.4]),[1,2])
angles2 = tf.reshape(tf.constant([-2.5,2.4+2*np.pi]),[1,2])
y = mynet(angles, training=False)
y2 = mynet(angles2, training=False)
print("y is", y)
print("y2 is", y2)


# mynet.load_weights(checkpoint_filepath)
# mynet.fit(input, output, batch_size=200, epochs = 1,callbacks=[model_checkpoint_callback])

# x = np.arange(1,11).astype(float).reshape(1,10)
# y = mynet(x, training=False)
# print("y is", y)
        