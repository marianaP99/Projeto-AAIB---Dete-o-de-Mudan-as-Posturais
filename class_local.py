import time
import json
import socket
import tsfel
import pandas as pd
import joblib
  
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        host = "192.168.1.135" #put here the ip address of your mobile
        port = 4242
    
        # mov = input('Which movement is done in this acquisition? (f, b, l, r, o) ')

        Tc = 60 # Período de aquisiç
        t0 = 5000 # Tempo de aquisição
        sample = t0 // Tc
        start = input("Start acquisition? y/n ")
        
        if start == 'y':
            print('Opening socket')
            s.connect((host, port))
            print('connected')
    #        f=open(filename+'.csv', 'w')
            X_data = []
            for n in range(sample):
                #time.sleep(0.025)
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
                        #print(n)
                    except:
                        continue
            X_data = pd.DataFrame(X_data, columns = ['TIME','ACCX','ACCY','ACCZ','GYROX','GYROY','GYROZ'])
            print(X_data)
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
            print(time_features)
    
            s.close()   
            print('socket closed') 
            model = joblib.load('gnb_model.sav')
            movement= { 2 : 'left' , 4 : 'right' , 1 : 'front' , 0 : 'back' , 3 : 'still' }
            y_pred = model.predict(time_features)
            print(movement[y_pred[0]])
            print ('... end')

