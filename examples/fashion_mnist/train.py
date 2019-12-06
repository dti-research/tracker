#!/usr/bin/python3
# Copyright (c) 2019, Danish Technological Institute (DTI Research)
# All rights reserved.
#
# This source code is licensed under the BSD-3-Clause-style license found in the
# LICENSE file in the root directory of this source tree.

import argparse

from tensorflow.keras.callbacks import TensorBoard
from tensorflow.keras.datasets import fashion_mnist
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import RMSprop
from tensorflow.keras.utils import to_categorical

parser = argparse.ArgumentParser(description='Simple feedforward test w/ TF on Fashion MNIST')
parser.add_argument('--seed', metavar='N', type=int,
                    help='Seed for the pseudo-random number generator',
                    required=True)
parser.add_argument('--epochs', metavar='N', type=int,
                    help='Number of epochs', required=True)
parser.add_argument('--batch_size', metavar='N', type=int,
                    help='Batch size', required=True)
parser.add_argument('--dropout', metavar='N', type=float,
                    help='Dropout', required=True)
parser.add_argument('--lr', metavar='N', type=float,
                    help='Learning rate', required=True)
parser.add_argument('--lr_decay', metavar='N', type=float,
                    help='Learning rate decay', required=True)
args = parser.parse_args()


# 1. Set `PYTHONHASHSEED` environment variable at a fixed value
import os
os.environ['PYTHONHASHSEED']=str(args.seed)
# 2. Set `python` built-in pseudo-random generator at a fixed value
import random
random.seed(args.seed)
# 3. Set `numpy` pseudo-random generator at a fixed value
import numpy as np
np.random.seed(args.seed)
# 4. Set `tensorflow` pseudo-random generator at a fixed value
import tensorflow as tf
tf.random.set_seed(args.seed)


(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
x_train = x_train.reshape(60000, 784)
x_test = x_test.reshape(10000, 784)
x_train = x_train.astype('float32')
x_test = x_test.astype('float32')
x_train /= 255
x_test /= 255
y_train = to_categorical(y_train, 10)
y_test = to_categorical(y_test, 10)

model = Sequential()
model.add(Dense(512, activation='relu', input_shape=(784,)))
model.add(Dropout(rate=args.dropout, seed=args.seed))
model.add(Dense(512, activation='relu'))
model.add(Dropout(rate=args.dropout, seed=args.seed))
model.add(Dense(10, activation='softmax'))

model.compile(
    loss='categorical_crossentropy',
    optimizer=RMSprop(lr=args.lr, decay=args.lr_decay),
    metrics=['accuracy'])

model.fit(
    x_train, y_train,
    batch_size=args.batch_size,
    epochs=args.epochs,
    verbose=1,
    validation_data=(x_test, y_test),
    callbacks=[TensorBoard(".")])
