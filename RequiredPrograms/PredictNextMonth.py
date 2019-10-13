import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing
import os
from sklearn import linear_model
import pandas as pd 


def predUsingRollingHorizon(realSeriesVal, frequency =12, startPos = 60):
    ## In order we try ('add' = additive, 'mul' = multiplicative)
    # 1) HolterWinter trend/seasonal = add/add all Data
    # 2) HolterWinter trend/seasonal = add/add using only the last 60 points each time (last 5 years)
    # 3) HolterWinter trend/seasonal = add/mul all Data
    # 4) HolterWinter trend/seasonal = add/mul using only the last 60 points each time (last 5 years)
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
    # elif lenMonthlyDem < 37:
    #     print('You have entered less than three years and a month of data. We will not calculate a bias term, but use HW.')
    #     fitHW = ExponentialSmoothing(monthlyDemand, seasonal_periods=freq, trend='add', seasonal='add').fit(use_boxcox=True)
    #     hwNextMonth = fitHW.forecast(1)[0]
    elif lenMonthlyDem <= 60:
        print('You have entered less than 5 years of data. The extra bias term will be calculated using all months,' + \
            ' and not just the ones corresponding to the frequency.')
        print('This may take a minute to run')
        fitHW = ExponentialSmoothing(monthlyDemand, seasonal_periods=freq, trend='add', seasonal='add').fit(use_boxcox=True)
        hwNextMonth = fitHW.forecast(1)[0]
        preds = predUsingRollingHorizon(monthlyDemand, frequency =12, startPos = 24)
        secAmount = np.std(np.array(preds) - monthlyDemand[24:])*0.67
    else:
        print('We will use the last three years of data for creating the bias term')
        print('This may take a minute to run')
        fitHW = ExponentialSmoothing(monthlyDemand, seasonal_periods=freq, trend='add', seasonal='add').fit(use_boxcox=True)
        hwNextMonth = fitHW.forecast(1)[0]
        preds = predUsingRollingHorizon(monthlyDemand, frequency =12, startPos = lenMonthlyDem-36)
        predsToUse = np.array([preds[0], preds[12], preds[24]])
        realToUse = np.array([monthlyDemand[-36], monthlyDemand[-24], monthlyDemand[-12]])
        secAmount = np.std(predsToUse- realToUse)*0.67

    print()

    print('Order Quantity For Next Month: ' +str(np.max(np.around(hwNextMonth+ secAmount - startingInventory),0)))    