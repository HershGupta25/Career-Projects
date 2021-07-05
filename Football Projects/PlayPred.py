import numpy as np
import pandas as pd
from sklearn import preprocessing as pp, linear_model as lm
from sklearn.neighbors import KNeighborsClassifier as kNN
import random

basedata = pd.read_csv(r'/Users/HerschelGupta/Documents/FootballAnalytics/RawData/TXUN_base_Cuse.csv')
rzdata = pd.read_csv(r'/Users/HerschelGupta/Documents/FootballAnalytics/RawData/TXUN_redzone_Cuse.csv')
rzdata = rzdata[rzdata['pff_DOWN'] != 0]
data = pd.concat([basedata,rzdata],ignore_index=True)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

data['pff_RUNPASS'] = data['pff_RUNPASS'].replace(['R','P'],['Run','Pass'])
down = pd.get_dummies(data.pff_DOWN,prefix='Down')
personnel = pd.get_dummies(data.pff_OFFPERSONNELBASIC,prefix='Personnel')

def FieldBdry():
    # PASS BREAKDOWN
    p1 = (data['pff_RUNPASS'] == 'Pass')
    p2 = (data['pff_PASSDIRECTION'] != 'X') 
    p3 = (data['pff_HASH'] != 'C')
    p_data = data[p1 & p2 & p3]
    data['Fld_Bdry_p'] = (p_data['pff_HASH'] == p_data['pff_PASSDIRECTION'])
    data['Fld_Bdry_p'] = data['Fld_Bdry_p'].replace([1,0,np.nan],['Pass_Boundary','Pass_Field','']) 
    
    # RUN BREAKDOWN
    r1 = (data['pff_RUNPASS'] == 'Run') 
    r2 = (data['pff_HASH'] != 'C')
    r_data = data[r1 & r2]
    left = r_data.isin({'pff_POAINTENDED':['LT','LE','ML','LG','JET SWEEP LEFT','END AROUND LEFT']})
    right = r_data.isin({'pff_POAINTENDED':['RT','RE','MR','RG','JET SWEEP RIGHT','END AROUND RIGHT']})
    data['Fld_Bdry_r'] = ((left['pff_POAINTENDED']) & (r_data['pff_HASH'] == 'L')) | ((right['pff_POAINTENDED']) & (r_data["pff_HASH"] == 'R'))
    data['Fld_Bdry_r'] = data['Fld_Bdry_r'].replace([1,0,np.nan],['Run_Boundary', 'Run_Field','']) 


    data['Fld_Bdry'] = data['Fld_Bdry_p'] + data['Fld_Bdry_r'] 
    imp = ['pff_OFFPERSONNELBASIC','pff_RUNPASS','Fld_Bdry']
    impdata = data[(r1 & r2) | (p1 & p2 & p3)]
    impdata = impdata[imp]
    impdata.dropna()

FieldBdry()
data['correctedPos'] = (data['pff_FIELDPOSITION'] < 0).replace([1,0],[abs(data['pff_FIELDPOSITION']),(100 - data['pff_FIELDPOSITION'])])
data = pd.concat([data,down,personnel],axis=1)

def feature(ind):
    # feat = [1,data.loc[ind,'Down_1':],data.loc[ind,'correctedPos'],data.loc[ind,'pff_DISTANCE'],data.loc[ind,'pff_RUNPASS']]
    feat = np.concatenate([np.array([1]),np.array(data.loc[ind,'Down_1':].values),np.array([data.loc[ind,'correctedPos']]),np.array([data.loc[ind,'pff_DISTANCE']]),np.array([data.loc[ind,'pff_RUNPASS']])])
    return feat

dataset = [feature(i) for i in range(len(data))]
random.shuffle(dataset)

X = [values[:-1] for values in dataset]
y = [values[-1] for values in dataset]
# print(X)
# print(y)
N = len(X)
X_train = X[:N//2]
X_test = X[N//2:]
y_train = y[:N//2]
y_test = y[N//2:]

model = lm.LogisticRegression()
model.fit(X_train, y_train)

predictionsTrain = model.predict(X_train)
predictionsTest = model.predict(X_test)

# Whether model prediction was correct
correctPredictionsTrain = predictionsTrain == y_train
correctPredictionsTest = predictionsTest == y_test

print("LR Training Accuracy: ",sum(correctPredictionsTrain) / len(correctPredictionsTrain) )
print("LR Testing Accuracy: ",sum(correctPredictionsTest) / len(correctPredictionsTest) )

neigh = kNN(n_neighbors=20)
neigh.fit(X_train, y_train) 

# Model's predictions
predictionsTrain = neigh.predict(X_train)
predictionsTest = neigh.predict(X_test)

# Whether model prediction was correct
correctPredictionsTrain = predictionsTrain == y_train
correctPredictionsTest = predictionsTest == y_test

print("kNN Training Accuracy: ", sum(correctPredictionsTrain) / len(correctPredictionsTrain)) # Training accuracy
print("kNN Testing Accuracy: ", sum(correctPredictionsTest) / len(correctPredictionsTest)) # Test accuracy