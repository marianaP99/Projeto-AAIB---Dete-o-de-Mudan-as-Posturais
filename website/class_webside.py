# import time
import json
import socket
# import numpy as np
import tsfel
import pandas as pd
import joblib
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from threading import Thread, Event

app = Flask(__name__)
socketio = SocketIO(app)
app.static_folder = 'static'

thread = Thread()
thread_stop_event = Event()

@app.route('/')
def sessions():
    return render_template('index.html')

@socketio.on('connecting')
def handle_connect():
   # print('handle_connect')
   socketio.emit('connected','connect')

@socketio.on('start')
def aquisition():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = "192.168.1.103" #put here the ip address of your mobile
        port = 4242
    
        Tc = 60 # Período de aquisição
        t0 = 5000 # Tempo de aquisição
        sample = t0 // Tc        
        X_data = []         
        
        # print('connected')        
        try:
            #print('Opening socket') 
            while not thread_stop_event.isSet():
                s.connect((host, port))
                for n in range(sample):
                    data = s.recv(256)
                    if data:
                        decoded_data = data.decode("utf-8").split("\n")
                        for msg in decoded_data:
                            try:
                                package = json.loads(msg)
                                # print(package)
                                t=package["accelerometer"]["timestamp"]
                                acc=package["accelerometer"]["value"]
                                gyro=package["gyroscope"]["value"]
                                X_data.append([t,acc[0],acc[1],acc[2],gyro[0],gyro[1],gyro[2]])
                                
                                
                                tt = Tc * n 
                                tt = round(tt/ 1000,2)
                                acc_x = acc[0]
                                acc_y = acc[1]
                                acc_z = acc[2]
                                gyro_x = gyro[0]
                                gyro_y = gyro[1]
                                gyro_z = gyro[2]
                                
                                emit('timeseries',{'time': tt, 'acc_x': acc_x, 'acc_y': acc_y, 'acc_z': acc_z, \
                                'gyro_x': gyro_x, 'gyro_y': gyro_y, 'gyro_z': gyro_z})
                                
                            except:
                                continue
                        #print(n)
                s.close()   
                X_data = pd.DataFrame(X_data, columns = ['TIME','ACCX','ACCY','ACCZ','GYROX','GYROY','GYROZ'])
                                    
                classify(X_data)       
                            
        except:
            emit('timeseries','Something went wrong with the acquisition')
        
        # return X_data

def classify(X_data):
    try:
        # X_data = aquisition()
        time_features = pd.DataFrame()
        time_features['acc_y|0_Mean'] = [tsfel.calc_mean(X_data.ACCY.values)]
        time_features['acc_y|0_Histogram_0'] = tsfel.hist(X_data.ACCY.values)[0]
        time_features['acc_y|0_Median'] = tsfel.calc_median(X_data.ACCY.values)
        time_features['acc_y|0_Wavelet standard deviation_7'] = tsfel.wavelet_std(signal = X_data.ACCY.values)[7]
        time_features['acc_y|0_Wavelet variance_7'] = tsfel.wavelet_var(X_data.ACCY.values)[7]    
        time_features['acc_z|0_Slope'] = tsfel.slope(X_data.ACCZ.values)    
        time_features['gyro_z|0_Mean'] = tsfel.calc_mean(X_data.GYROZ.values)
        time_features['gyro_z|0_Histogram_6'] = tsfel.hist(X_data.GYROZ.values)[6]
        time_features['gyro_y|0_ECDF Percentile_1'] = tsfel.ecdf_percentile(X_data.GYROY.values)[1]
        time_features['gyro_y|0_Interquartile range'] = tsfel.interq_range(X_data.GYROY.values)
          
        model = joblib.load('gnb_model.sav')
        movement= { 2 : 'Left-Side Bending' , 4 : 'Right-Side Bending' , 1 : 'Compression Movement' , 0 : 'Extension Movement' , 3 : 'Standing Still' }
        y_pred = model.predict(time_features)
        y_pred = movement[y_pred[0]]
        emit('prediction',y_pred)
        
        # return movement[y_pred[0]]
    except:
        emit('prediction','Something went wrong with the classification')
        #return 'Something went wrong with the acquisition'

#@socketio.on('--')
#def handle_my_costum_event():
 #   y_pred = classifier()
  #  emit('pred', {y_pred})

if __name__ == '__main__':
    socketio.run(app, debug=True)


