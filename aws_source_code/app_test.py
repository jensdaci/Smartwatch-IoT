from flask import Flask, Response, request
from flask import jsonify
from flask_pymongo import PyMongo
import json
from joblib import dump, load
import numpy as np
import pandas as pd
from sklearn import svm

app = Flask(__name__)

app.config['MONGO_DBNAME'] = 'esp_gestures_test'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/esp_gestures_test'
mongo = PyMongo(app)


@app.route("/",methods=['POST'])
def get_training_data():


    data = json.loads(request.data)
    x_safe = data['x']
    y_safe = data['y']

    if len(data['x'])>vector_length:
        x = [int(i) for i in data['x'][:vector_length]]
        y = [int(i) for i in data['y'][:vector_length]]
    else:
        x_ = [int(i) for i in data['x']]
        x = x_ + [0]*(vector_length - len(x_))
        y_ = [int(i) for i in data['y']]
        y = y_ + [0]*(vector_length - len(x_))


    data['x'] = np.split(np.array(x),N)
    data['y'] = np.split(np.array(y),N)

    data['x'] = [np.real(np.fft.rfft(i)) for i in data['x']]
    data['y'] = [np.real(np.fft.rfft(i)) for i in data['y']]

    x = []
    y = []
    for i in range(1,len(data['x'])):
        x.append(np.concatenate([data['x'][i],data['x'][i-1]]))
        y.append(np.concatenate([data['y'][i],data['y'][i-1]]))

    test_data = []
    test_data += [np.mean(i) for i in x]
    test_data += [np.mean(i) for i in y]
    test_data += [np.std(i) for i in x]
    test_data += [np.std(i) for i in y]
    test_data += [np.sum(np.square(i))/(2*N) for i in x]
    test_data += [np.sum(np.square(i))/(2*N) for i in y]


    pred = clf.predict(np.array(test_data).reshape(1, -1))
    data_dump = {'x': x_safe,'y':y_safe,'label':str(pred[0])}
    training = mongo.db.testing.insert(data_dump)

    print('Received and Predicted')

    return jsonify({'prediction':str(pred[0])})

if __name__ == '__main__':
    vector_length = 80

    clf = load('../svm.joblib')
    N=20

    app.run(host='0.0.0.0',port=5001,debug=True)
