
from numpy import mean
from numpy import std
from numpy import dstack
from pandas import read_csv
from matplotlib import pyplot
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Flatten
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPool1D
from tensorflow.keras.utils import to_categorical

from sklearn.metrics import confusion_matrix

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import collections
import timeit

Frecuencia = False
zurdos = False

if Frecuencia:
    directorio_dataset = '/Users/claud/OneDrive/Escritorio/DatasetFreq9.csv'
    ventana=20
else:
    ventana=40
    directorio_dataset = '/Users/claud/OneDrive/Escritorio/Dataset.csv'
    
clases=13
clases_str = ['D','R','DP','RP','GD','GR','GDP','GRP','VD','VR','B','RM','S']

import itertools

def plot_confusion_matrix(cm, classes,
                          normalize=False,
                          title='Confusion matrix',
                          cmap=plt.cm.Blues):
    """
    This function prints and plots the confusion matrix.
    Normalization can be applied by setting `normalize=True`.
    """
    plt.imshow(cm, interpolation='nearest', cmap=cmap)
    plt.colorbar()
    tick_marks = np.arange(len(classes))
    plt.xticks(tick_marks, classes, rotation=45)
    plt.yticks(tick_marks, classes)

    if normalize:
        cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]

    thresh = cm.max() / 2.
    for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
        plt.text(j, i, cm[i, j],
                 horizontalalignment="center",
                 color="white" if cm[i, j] > thresh else "black")

    plt.tight_layout()
    plt.ylabel('Actual')
    plt.xlabel('Prediction')
    plt.xticks(range(13), clases_str)
    plt.yticks(range(13), clases_str)


# load the dataset, returns train and test X and y elements
def load_dataset_group(directorio_dataset,normalize=False):
    
    datos=pd.read_csv(directorio_dataset)
    
    #si solo se quieren estudiar los jugadores diestros
    if (zurdos == False):
        diestros = datos.loc[:,'mano'] == 0
        datos = datos.loc[diestros]
    
    y=datos.loc[:, "tipo_golpe"].to_numpy()
    # Grafica con la cantidad de golpes que hay para cada tipo
    #print(collections.Counter(y))
    #plt.hist(y,bins=clases)
    #plt.plot()
    
    # Se divide el Dataset en Train y Test
    # Se barajan antes de dividirlo (shuffle=True)
    # Se dividen de forma que entrenamiento y test estén balanceados (stratify=y)
    # Se dividen de forma aleatoria, pero siempre la misma (random_state=int)
    trainingSet, testSet = train_test_split(datos, test_size=0.2,shuffle=True,stratify=y,random_state=5)
    
    #Se recoge los datos de Train y Set:
    name_ax = ["Ax"+str(i) for i in range(ventana)]
    name_ay = ["Ay"+str(i) for i in range(ventana)]
    name_az = ["Az"+str(i) for i in range(ventana)]
    name_vx = ["Vx"+str(i) for i in range(ventana)]
    name_vy = ["Vy"+str(i) for i in range(ventana)]
    name_vz = ["Vz"+str(i) for i in range(ventana)]
        
    trainX = trainingSet[name_ax+name_ay+name_az+name_vx+name_vy+name_vz]
    trainy = trainingSet[['tipo_golpe']]
    testX = testSet[name_ax+name_ay+name_az+name_vx+name_vy+name_vz]
    testy = testSet[['tipo_golpe']]
    
    trainX=trainX.to_numpy()
    trainy=trainy.to_numpy()
    testX=testX.to_numpy()
    testy=testy.to_numpy()
        
    #guardo todos los datos de cada GDL por separado
    datos_trainX=trainX.shape[0]
    trainX_accel_x = [trainX[i][0:ventana] for i in range(datos_trainX)]
    trainX_accel_y = [trainX[i][ventana:ventana*2] for i in range(datos_trainX)]
    trainX_accel_z = [trainX[i][ventana*2:ventana*3] for i in range(datos_trainX)]
    trainX_gyros_x = [trainX[i][ventana*3:ventana*4] for i in range(datos_trainX)]
    trainX_gyros_y = [trainX[i][ventana*4:ventana*5] for i in range(datos_trainX)]
    trainX_gyros_z = [trainX[i][ventana*5:ventana*6] for i in range(datos_trainX)]
    
    datos_testX=testX.shape[0]
    testX_accel_x = [testX[i][0:ventana] for i in range(datos_testX)]
    testX_accel_y = [testX[i][ventana:ventana*2] for i in range(datos_testX)]
    testX_accel_z = [testX[i][ventana*2:ventana*3] for i in range(datos_testX)]
    testX_gyros_x = [testX[i][ventana*3:ventana*4] for i in range(datos_testX)]
    testX_gyros_y = [testX[i][ventana*4:ventana*5] for i in range(datos_testX)]
    testX_gyros_z = [testX[i][ventana*5:ventana*6] for i in range(datos_testX)]
    
    
    if normalize:

        #Se divide los valores de acelerómetro y giroscopio entre sus valores maximos
        #Solo entrará en el bucle si en la funcion load_dataset_group, normalize está a True
        if Frecuencia:
            accel=datos.loc[:, "Ax0":"Az19"].to_numpy()
            gyros=datos.loc[:, "Vx0":"Vz19"].to_numpy()
        else:
            accel=datos.loc[:, "Ax0":"Az39"].to_numpy()
            gyros=datos.loc[:, "Vx0":"Vz39"].to_numpy()
        
        accel_max = np.amax(accel)
        gyros_max = np.amax(gyros)
        trainX_accel_x = trainX_accel_x/accel_max
        trainX_accel_y = trainX_accel_y/accel_max
        trainX_accel_z = trainX_accel_z/accel_max
        trainX_gyros_x = trainX_gyros_x/gyros_max
        trainX_gyros_y = trainX_gyros_y/gyros_max
        trainX_gyros_z = trainX_gyros_z/gyros_max
        
        testX_accel_x = testX_accel_x/accel_max
        testX_accel_y = testX_accel_y/accel_max
        testX_accel_z = testX_accel_z/accel_max
        testX_gyros_x = testX_gyros_x/gyros_max
        testX_gyros_y = testX_gyros_y/gyros_max
        testX_gyros_z = testX_gyros_z/gyros_max
        
        
    #se crea trainX con dimension (datos_trainX,ventana,GDL)
    trainX = np.array([trainX_accel_x,trainX_accel_y,trainX_accel_z,trainX_gyros_x,trainX_gyros_y,trainX_gyros_z])
    
    testX = np.array([testX_accel_x,testX_accel_y,testX_accel_z,testX_gyros_x,testX_gyros_y,testX_gyros_z])
       
    #Necesito una matriz de (datos_trainX, ventana, GDL), pero tengo en trainX (GDL, datos_trainX, ventana)
    trainX_ordenada = np.ones((trainX.shape[1],ventana,6))
    for i in range(trainX.shape[1]):
        for j in range(trainX.shape[2]):
            for k in range(trainX.shape[0]):
                trainX_ordenada[i][j][k] = trainX[k][i][j]
                
    #Necesito una matriz de (datos_testX, ventana, GDL), pero tengo en testX (GDL, datos_testX, ventana)
    testX_ordenada = np.ones((testX.shape[1],ventana,6))
    for i in range(testX.shape[1]):
        for j in range(testX.shape[2]):
            for k in range(testX.shape[0]):
                testX_ordenada[i][j][k] = testX[k][i][j]
    
    #Guardo la característica que me interesa del golpe para estudiar los fallos
    test_deportistas = testSet.loc[:, "id"].to_numpy()

    return trainX_ordenada, trainy, testX_ordenada, testy, test_deportistas

# load the dataset, returns train and test X and y elements
def load_dataset(directorio_dataset):
	
    # carga train y test
	trainX, trainy, testX, testy, test_deportistas = load_dataset_group(directorio_dataset)
	print(trainX.shape, trainy.shape)
	print(testX.shape, testy.shape)
    
	# one hot encode y
	trainy = to_categorical(trainy)
	testy = to_categorical(testy)
	print(trainX.shape, trainy.shape, testX.shape, testy.shape)
	return trainX, trainy, testX, testy, test_deportistas


# fit and evaluate a model
def evaluate_model(trainX, trainy, testX, testy, test_deportistas, n_filters, epochs, batch_size):
    verbose = 0
	
    n_timesteps, n_features, n_outputs = trainX.shape[1], trainX.shape[2], trainy.shape[1]
    
    model = Sequential()
    model.add(Conv1D(filters=n_filters, kernel_size=5, activation='relu', input_shape=(n_timesteps,n_features)))
	#model.add(Conv1D(filters=n_filters/2, kernel_size=5, activation='relu'))
	#Dropout desactiva arbitrariamente neuronas con el fin de evitar el overfitting
    model.add(Dropout(0.5))
	#Maxpool reduce las características aprendidas para quedarse solo con las mas importantes. Se hace al final de las capas CNN1D
    model.add(MaxPool1D(pool_size=2))
    
	#Flatten convierte las características en un vector para pasarselo a la capa densa.
    model.add(Flatten())
    model.add(Dense(1000, activation='relu'))
    model.add(Dense(n_outputs, activation='softmax'))
	
    model.summary()
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

	# fit network
	#train_log = model.fit(trainX, trainy, validation_split=0.2, epochs=epochs, batch_size=batch_size, verbose=verbose)  
    starttimetrain = timeit.default_timer()
    train_log = model.fit(trainX, trainy, validation_split=0.2, epochs=epochs, batch_size=batch_size, verbose=verbose)
    train_time = starttimetrain - timeit.default_timer()
    print("el tiempo que le ha costado entrenar ha sido:")
    print(train_time)
    
    #print(testX.shape())
    
    starttimepredict = timeit.default_timer()
    model.predict(testX)
    predicttime = starttimepredict - timeit.default_timer()
    print("el tiempo que le ha costado predecir una muestra ha sido:")
    print(predicttime) 
    
	# evaluate model
    loss, accuracy = model.evaluate(testX, testy, batch_size=batch_size, verbose=0)
    

	#model.save_weights("CNN.h5")
    
    """
    # MATRIZ DE CONFUSION:
    # Predecimos las clases para los datos de test
	Y_pred = model.predict(testX)
    # Convertimos las predicciones en one hot encoding
	Y_pred_classes = np.argmax(Y_pred, axis = 1) 
    # Convertimos los datos de test en one hot encoding
	Y_true = np.argmax(testy, axis = 1) 
    # Computamos la matriz de confusion
	confusion_mtx = confusion_matrix(Y_true, Y_pred_classes) 
	#print(confusion_mtx)
    # Mostramos los resultados
	plt.figure()
	plot_confusion_matrix(cm = confusion_mtx, classes = range(13)) 
     
	#Para identificar quien ha cometido los fallos:
	fallos=identify_faults(test_deportistas,Y_true,Y_pred_classes) 
	print("Los fallos corresponden a: ",collections.Counter(fallos))

	# grafica con la función de coste
	loss = train_log.history['loss']
	val_loss = train_log.history['val_loss']
	epochs = range(1, len(loss) + 1)
	#plt.figure()
	#plt.plot(epochs, loss, 'b', label='Training loss')
	#plt.plot(epochs, val_loss, 'r', label='Validation loss')
	#plt.title('Training and validation loss')
	#plt.xlabel('Epochs')
	#plt.ylabel('Loss')
	#plt.legend()
	#plt.show()
    """
    return accuracy

def identify_faults(test_deportistas, dataY, predictions):
    deportista=[]
    for i in range(len(dataY)):
        if dataY[i]!=predictions[i]:
            deportista.append(test_deportistas[i])
            #print("Error: Realidad:",dataY[i],"Prediccion:",predictions[i])
        
    return deportista

# summarize scores
def summarize_results(scores, filters, epochs, batch_size):
	# Esta funcion saca una grafica con un diagrama de bigotes de los resultados
	# Saca la gráfica para los distintos numero de filtros provados para una misma configuracion, por lo que epoch y batch_size serán fijos en la gráfica
	# Si se está realizando la busqueda en rejilla con distintos valores para epoch y batch, sacará una gráfica distinta para cada combinación
	# summarize mean and standard deviation
   
	best_accuracy = 0
	best_params = []
	for i in range(len(scores)):
		m, s = mean(scores[i]), std(scores[i])
		print('Epoch=%d; Batch_size=%d; Filtros=%d: %.3f%% (+/-%.3f)' % (epochs, batch_size, filters[i], m, s))
		if m>best_accuracy:
			best_accuracy = m
			best_params = [m, s, epochs, batch_size, filters[i]]
	# boxplot of scores
	#pyplot.figure( figsize=(10,7))
	print("scores es",scores)
	pyplot.figure()
	pyplot.boxplot(scores, labels=filters)
	pyplot.title('Accuracy para Epoch=%d, Batch_size=%d, Filtros capa CNN1D=%d, Kernel=5' % (epochs, batch_size, filters[i]))
	#pyplot.title('Accuracy para Epoch=%d, Batch_size=%d, Filtros capa CNN1D=%d, Kernel=8, Filtros capa densa=1000' % (epochs, batch_size, filters[i]))
	pyplot.xlabel("Número de filtros")
	pyplot.ylabel("Accuracy (%)")
	pyplot.grid(linestyle='-', linewidth=0.3)
	#pyplot.savefig('exp_cnn_filters.png')
    
	return best_params


# run an experiment
def run_experiment(filters, epochs, batch_size, repeats=1):
	# load data
	trainX, trainy, testX, testy, test_deportistas = load_dataset(directorio_dataset)
	# test each parameter
	best_accuracy = 0
	best_params = []
	for i in epochs:
		for j in batch_size:      
			all_scores = list()
			for p in filters:
				# repeat experiment
				scores = list()
				for r in range(repeats):
					score = evaluate_model(trainX, trainy, testX, testy, test_deportistas, p, i, j)
					score = score * 100.0
					print('>p=%d #%d: %.3f' % (p, r+1, score))
					scores.append(score)
				all_scores.append(scores)
			# summarize results
			params = summarize_results(all_scores, filters, i, j)
			if params[0]>best_accuracy:
				best_accuracy = params[0]
				best_params = params
                

	print("Best params:")
	print('Epoch=%d; Batch_size=%d; Filtros=%d: %.3f%% (+/-%.3f)' % (best_params[2], best_params[3], best_params[4], best_params[0], best_params[1],))
	 
    
    
# run the experiment
epochs = [150]
batch_size = [30]
filters = [512]


# =============================================================================
# epochs = [40, 70, 150, 250]
# batch_size = [30, 50, 70]
# filters = [64, 128, 256, 512]
# =============================================================================

zurdos = False
dos_conv = False
dos_dense = True
run_experiment(filters, epochs, batch_size)





