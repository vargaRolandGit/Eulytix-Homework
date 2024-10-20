# -*- coding: utf-8 -*-
"""eulytix_homework.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/12smCva2WZ1pv08HyhpRYmWMK_O-f-fQu
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import RandomOverSampler

df = pd.read_csv('dataset.csv')

df['is_democrat'] = df['party_affiliation'].apply(lambda x: 1 if x == 'D' else 0)
df['is_republican'] = df['party_affiliation'].apply(lambda x: 1 if x == 'R' else 0)
df['voted_yea'] = df['vote_record'].apply(lambda x: 1 if x == 'Yea' else 0)

grouped_votes = df.groupby(['measure_number', 'result']).agg({
    'is_democrat': 'sum',
    'is_republican': 'sum',
    'voted_yea': 'sum'
}).reset_index()

grouped_votes.head()

# only checking if the vote passed or not
grouped_votes['vote_passed'] = grouped_votes['result'].apply(lambda x: 1 if 'passed' in x.lower() else 0)
grouped_votes['vote_passed']

df = grouped_votes
X = df[['is_democrat', 'is_republican', 'voted_yea']]
y = df['vote_passed']

scaler = StandardScaler()
X = scaler.fit_transform(X)
data = np.hstack((X, np.reshape(y, (-1,1))))
over = RandomOverSampler()
X, y = over.fit_resample(X,y)

X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.4, random_state=42)
X_valid, X_test, y_valid, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

for i in range(len(df.columns[:-1])):
  label = df.columns[i]
  plt.hist(df[df['vote_passed'] == 1][label], color = 'blue', label = 'positive', alpha = 0.7, density = True, bins=15)
  plt.hist(df[df['vote_passed'] == 0][label], color = 'red', label  = 'negative', alpha = 0.7, density = True, bins=15)
  plt.title = label
  plt.ylabel('N')
  plt.xlabel(label)
  plt.legend()
  plt.show()

model = tf.keras.Sequential([
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(16, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])

model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.003), loss='binary_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
model.evaluate(X_train, y_train)

model.evaluate(X_test, y_test)

