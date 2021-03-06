import numpy as np
import itertools
import pandas as pd
import os
from lightgbm import LGBMRegressor
#from fastFM import sgd
from rgf.sklearn import RGFRegressor

from sklearn.linear_model import Ridge
from sklearn.svm import SVR
from sklearn.ensemble import ExtraTreesRegressor
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression, SGDRegressor
from sklearn.neighbors import KNeighborsRegressor

from sklearn.model_selection import KFold, train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.pipeline import make_pipeline

from mlxtend.regressor import StackingRegressor
from mlxtend.feature_selection import ColumnSelector

from sklearn.datasets import load_boston
class(object):

    ejectCAS = ['10124-36-4', '108-88-3', '111991-09-4', '116-29-0', '120-12-7', '126833-17-8', '13171-21-6',
                        '1333-82-0', '137-30-4', '148-79-8', '1582-09-8', '1610-18-0', '2058-46-0', '2104-64-5',
                        '21725-46-2',
                        '2303-17-5', '25311-71-1', '25812-30-0', '298-00-0', '298-04-4', '314-40-9', '330-54-1',
                        '4170-30-3',
                        '4717-38-8', '50-00-0', '52645-53-1', '55406-53-6', '56-35-9', '56-38-2', '60207-90-1', '6051-87-2',
                        '62-53-3', '6317-18-6', '69-72-7', '7440-02-0', '7447-40-7', '7722-84-1', '7733-02-0', '7758-94-3',
                        '80844-07-1', '82657-04-3', '84852-15-3', '86-73-7', '9016-45-9', '99-35-4']
    os.chdir(r'G:\マイドライブ\Data\Meram Chronic Data')


    def calcRMSE(pred,real):
      RMSE = (np.sum((pred-real.tolist())**2)/len(pred))**(1/2)
      return RMSE
    def calcCorr(pred,real):
      corr = np.corrcoef(real, pred.flatten())[0,1]
      return corr

    def test(self):
        df =pd.read_csv('MorganMACCS.csv')
        baseDf = df
        extractDf =  df['CAS'].isin(ejectCAS)
        df = df[~df['CAS'].isin(ejectCAS)]
        y = df['logTox']
        dropList = ['CAS','toxValue','logTox','HDonor', 'HAcceptors', 'AromaticHeterocycles', 'AromaticCarbocycles', 'FractionCSP3']
                    #dropList = ['CAS','toxValue','logTox']
        X = df.drop(columns=dropList)
        #Normalize
        for name in X.columns:
            if str.isdecimal(name)==True:
              if X[str(name)].sum() == 0:
                   print(name)
                   X = X.drop(columns=name)
            else:
                std =X[name].std()
                mean = X[name].mean()
                X[name] = X[name].apply(lambda x: ((x - mean) * 1 / std + 0))
        X_train, X_test, y_train, y_test = train_test_split( X, y, test_size=0.1, random_state=2)

        cols = np.arange(1,550,1).tolist()
        cols = X.columns.tolist()
        cols = [1,2,3]
        # Initializing Classifiers
        reg1 = Ridge(random_state=1)
        #reg2 = ExtraTreesRegressor()
        reg2 = ExtraTreesRegressor(n_estimators=50,max_features= 50,min_samples_split= 5,max_depth= 50, min_samples_leaf= 5)
        reg3 = SVR(gamma='auto',kernel='linear')
        reg4 = LGBMRegressor(boosting_type='gbdt', num_leaves= 60,learning_rate=0.06)
        pls = PLSRegression(n_components=3)
        pipe1 = make_pipeline(ColumnSelector(cols=cols), ExtraTreesRegressor(n_estimators=50))
        #linear =SGDRegressor(max_iter=1000)
        rgf = RGFRegressor(max_leaf=1000, algorithm="RGF",test_interval=100, loss="LS",verbose=False,l2=1.0)
        nbrs = KNeighborsRegressor(2)
        pipe2 = make_pipeline(ColumnSelector(cols=cols), KNeighborsRegressor(31))

        meta = ExtraTreesRegressor(n_estimators=50,max_features= 7,min_samples_split= 5,max_depth= 50, min_samples_leaf= 5)

        stackReg = StackingRegressor(regressors=[reg1,reg2, reg3,pipe1,pls,nbrs,rgf], meta_regressor=meta,verbose=1)
        stackReg.fit(X_train, y_train)
        y_pred = stackReg.predict(X_train)
        y_val = stackReg.predict(X_test)
        print("Root Mean Squared Error train: %.4f" % calcRMSE(y_pred,y_train))
        print("Root Mean Squared Error test: %.4f" % calcRMSE(y_val,y_test))
        print('Correlation Coefficient train: %.4f' % calcCorr(y_pred,y_train))
        print('Correlation Coefficient test: %.4f' % calcCorr(y_val,y_test))

        reg4.fit(X_train, y_train)
        y_pred = reg4.predict(X_train)
        y_val = reg4.predict(X_test)
        print("Root Mean Squared Error train: %.4f" % calcRMSE(y_pred,y_train))
        print("Root Mean Squared Error test: %.4f" % calcRMSE(y_val,y_test))
        print('Correlation Coefficient train: %.4f' % calcCorr(y_pred,y_train))
        print('Correlation Coefficient test: %.4f' % calcCorr(y_val,y_test))