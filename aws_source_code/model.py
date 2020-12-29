import pymongo
import numpy as np
import pandas as pd
from sklearn import svm
from joblib import dump, load
import math
from sklearn import svm
from joblib import dump, load


N = 20

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["esp_gestures"]
mycol = mydb['training2']

data = {}

rows = mycol.find()

#append all rows of the same run into 1
for row in rows:

    if row['run_id'] in data.keys():
        data[row['run_id']]['x'] += list(row['x'])
        data[row['run_id']]['y'] += list(row['y'])
    else:
        data[row['run_id']] = {'x':list(row['x']),'y':list(row['y']),'label':row['label']}

#find the max length
lengths = []
for run in data:
    lengths.append(len(data[run]['x']))
max_length = N * (math.ceil(max(lengths)/N))

print('Len: ',max_length)

#trim all rows to that length and split into N segments
for row in data:
    length_ = len(data[row]['x'])
    data[row]['x'] = np.split(np.array(data[row]['x']+[0]*(max_length-length_)),N)
    data[row]['x'] = [np.real(np.fft.rfft(i)) for i in data[row]['x']] # np.fft.rfft(i) take fft
    #data[row]['x'] = [np.array(i) for i in data[row]['x']]
    data[row]['y'] = np.split(np.array(data[row]['y']+[0]*(max_length-length_)),N)
    #data[row]['y'] = [np.array(i) for i in data[row]['y']]
    data[row]['y'] = [np.real(np.fft.rfft(i)) for i in data[row]['y']]

# combine these segments into frames, and calculate important features.
training_data = {}
labels = {}

for row in data:
    temp_x = []
    temp_y = []
    for i in range(1,len(data[row]['x'])):
        temp_x.append(np.concatenate([data[row]['x'][i],data[row]['x'][i-1]]))
        temp_y.append(np.concatenate([data[row]['y'][i],data[row]['y'][i-1]]))
    data[row]['x'] = temp_x
    data[row]['y'] = temp_y

    training_data[row] = {}
    labels[row] = data[row]['label']

    training_data[row]['x_mean'] = np.array([np.mean(i) for i in data[row]['x']])
    training_data[row]['y_mean'] = np.array([np.mean(i) for i in data[row]['y']])
    training_data[row]['x_std'] = np.array([np.std(i) for i in data[row]['x']])
    training_data[row]['y_std'] = np.array([np.std(i) for i in data[row]['y']])
    training_data[row]['x_energy'] = np.array([np.sum(np.square(i))/(2*N) for i in data[row]['x']])
    training_data[row]['y_energy'] = np.array([np.sum(np.square(i))/(2*N) for i in data[row]['y']])

features = {}
for row in training_data:
    features[row] = []
    for vec in training_data[row].values():
        features[row] += list(vec)


x_train = pd.DataFrame.from_dict(features,orient='index').reset_index(drop=True)
y_train = pd.DataFrame.from_dict(labels,orient='index').reset_index(drop=True)


clf = svm.SVC()
clf.fit(x_train.values,y_train.values.ravel())

x_test = x_train.sample(n=5)
y_test = y_train.loc[x_test.index]

dump(clf,'svm.joblib')

y_pred = clf.predict(x_test.values)

print('prediction: ',y_pred)
print('true: ',[i[0] for i in y_test.values])


