import tensorflow as tf
from tensorflow.python.platform import gfile
with tf.compat.v1.Session() as sess:
    model_filename ='frozen.pb'
    with gfile.FastGFile(model_filename, 'rb') as f:
        graph_def = tf.compat.v1.GraphDef()
        graph_def.ParseFromString(f.read())
        g_in = tf.compat.v1.import_graph_def(graph_def)
LOGDIR='frozen_log'
tf.compat.v1.disable_eager_execution()
train_writer = tf.compat.v1.summary.FileWriter(LOGDIR)
train_writer.add_graph(sess.graph)