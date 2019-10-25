import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing
import os
from sklearn import linear_model
import pandas as pd 


def predUsingRollingHorizon(realSeriesVal, frequency =12, startPos = 60):
    totVal = len(realSeriesVal)
    toRet = np.zeros(totVal-startPos)
    for i in range(startPos, totVal):
        fit1 = ExponentialSmoothing(realSeriesVal[0:i], seasonal_periods=frequency, trend='add', seasonal='add').fit(use_boxcox=True)
        toRet[i-startPos] = fit1.forecast(1)[0]
    return toRet


if __name__ == '__main__':
    currentDirectory = os.getcwd()
    condFileHasNotBeingRead = True
    monthlyDemand = 0
    pdData = 0
    while condFileHasNotBeingRead:
        answerInputName = input('Which csv or txt in folder '+str(os.getcwd())+\
            ' has the past demand data'+"\n"+\
            '(Please add at the end of the name the .csv or .txt depending on which type you are using, and make sure that your is delimited by commas.):')
        fname = currentDirectory+'/'+answerInputName
        if os.path.isfile(fname):
            print('File Found')
            if fname[-3:] not in ['txt', 'csv']:
                print(fname + ' does not finish in csv or txt, try again.')
            else:
                pdData = pd.read_csv(fname)
                if len(list(pdData.columns)) ==3:
                    condFileHasNotBeingRead =  False
                    monthlyDemand = np.array(pdData.iloc[:,2], dtype =float)
                else:
                    print('The file does not have three columns')
        else:
            print(fname + ' does not exist.')
            print('Please try again.')
    print()
    print()
    startingInventory = 0

    condStartingInventoryNotANumber = True
    while condStartingInventoryNotANumber:
        answerInputName = input('Which is the remaining inventory from last month:')
        try:
            float(answerInputName)
            condStartingInventoryNotANumber = False
            startingInventory = float(answerInputName)
        except ValueError:
            print(answerInputName + 'is not a number. Please enter a number.')

    print()
    print()

    freq = 12
    

    hwNextMonth = 0
    secAmount  = 0 
    lenMonthlyDem = len(monthlyDemand)

    if lenMonthlyDem <= 12:
        print('You have entered less than one year of data. The best prediction we can suggest is ordering the same amount as last month.')
        hwNextMonth = monthlyDemand[-1]
    elif lenMonthlyDem <= 24:
        print('You have entered less than two years of data. Our prediction will simply be a linear regression.')
        lrFit = linear_model.LinearRegression().fit(np.arange(len(monthlyDemand)).reshape(-1, 1),monthlyDemand)
        hwNextMonth = float(lrFit.predict(lenMonthlyDem))
    else:
        print('We will use HolterWinter and a bias term.')
        print('This may take a minute to run')
        fitHW = ExponentialSmoothing(monthlyDemand, seasonal_periods=freq, trend='add', seasonal='add').fit(use_boxcox=True)
        hwNextMonth = fitHW.forecast(1)[0]
        preds = predUsingRollingHorizon(monthlyDemand, frequency =12, startPos = 24)
        errors = []
        if len(preds)>=24:
            count = len(preds)-12
            while count>=0:
                errors.append(monthlyDemand[24 + count] - preds[count])
                count -= 12
        else:
            errors = monthlyDemand[24:]-np.array(preds)
        secAmount = np.std(np.array(errors))*0.67

    print()

    print('Final Inventory : '+str(startingInventory)+\
        ', HolterWinter/LR/Persistence (as corresponds) '+str(hwNextMonth)+', Bias Term: '+str(secAmount))

    print('Order Quantity For Next Month: ' +\
        str(np.maximum(np.round(hwNextMonth+ secAmount - startingInventory,decimals = 2),0)))    