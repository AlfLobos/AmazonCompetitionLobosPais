import numpy as np
from statsmodels.tsa.api import ExponentialSmoothing
import os
from sklearn import linear_model
import pandas as pd 
import csv


## Forecast Methods

def predUsingRollingHorizon(realSeriesVal, frequency =12, startPos = 60):
    totVal = len(realSeriesVal)
    toRet = np.zeros(totVal-startPos)
    for i in range(startPos, totVal):
        fit1 = ExponentialSmoothing(realSeriesVal[0:i], seasonal_periods=frequency, trend='add', seasonal='add').fit(use_boxcox=True)
        toRet[i-startPos] = fit1.forecast(1)[0]
    return toRet

def predRH_Persistence(realSeriesVal, posToPredict = 24):
    return np.array(realSeriesVal[posToPredict-1:-1])

def predRHLinearRegression(realSeriesVal, posToPredict = 24):
    pred = []
    for i in range(posToPredict):
        auxSeries = realSeriesVal[:-24-i]
        lenAux = len(auxSeries)
        lrFit = linear_model.LinearRegression().fit(np.arange(lenAux).reshape(-1, 1), auxSeries)
        pred.append(float(lrFit.predict(lenAux)))
    return np.array(pred)

## Methods to create the bias term

def createSecAmount(preds, realValues, frequency = 12, posToPredict = 24):
    def CreateErrors(preds, realValues, startPos, frequency):
        errors = []
        totPoints = len(preds)
        if startPos >=24:
            count = startPos- frequency
            while count>=0:
                errors.append(preds[count] - realValues[count])
                count -= frequency
            return np.array(errors)
        else:
            return preds[:startPos] - realValues[:startPos]
        secAmount = []
        lenOfPred = len(preds)
        for i in range(posToPredict):
            posToPredict = lenOfPred - posToPredict -1
            errors = CreateErrors(preds, realValues, posToPredict, frequency)
            secAmount.append(np.std(erros)*0.67)
        return secAmount
    secAmount = []
    lenOfPred = len(preds)
    for i in range(posToPredict):
        startPos = lenOfPred - posToPredict - i
        errors = CreateErrors(preds, realValues, startPos, frequency)
        secAmount.append(np.std(errors)*0.67)
    return secAmount


## Method to predict oth the forecast and bias term
def predMethod(realSeriesVal, frequency =12, numToPredict = 24):
    predForecast = np.zeros(numToPredict)
    secAmount = np.zeros(numToPredict)
    
    if (len(realSeriesVal) - numToPredict)<= 0:
        print('You want to predict more points than the data you have.')
    elif (len(realSeriesVal) - numToPredict)<= 12:
        print('You are using only one year of data to predict. The best prediction we can suggest is ordering the same amount as last month.')
        predForecast = predRH_Persistence(realSeriesVal, posToPredict = numToPredict)
    elif (len(realSeriesVal) - numToPredict)<= 24:
        print('You are using only two years of data to predict. Our prediction will simply be a linear regression.')
        predForecast = predRHLinearRegression(realSeriesVal, posToPredict = numToPredict)
    else:
        print('We will use HolterWinter and a bias term for our prediction.')
        aux = len(realSeriesVal) - numToPredict
        if aux<=72:
            startpos = 24
        else:
            startpos = aux - 48
        predForecast = predUsingRollingHorizon(realSeriesVal, frequency =frequency, startPos = startpos)
        secAmount = createSecAmount(predForecast, realSeriesVal[startpos:], frequency = frequency, posToPredict = numToPredict)
        predForecast = predForecast[-24:]
    return predForecast, secAmount

## Method to Create the Starting/Ending Inventory, Order Quantity, 
def createStartEndInvAndOrderQuantity(forecastPlusSec, realDemand, inv0):
    numToPred = len(realDemand)
    toRet = np.zeros((numToPred, 5))
    startInv = 0
    finalInv = inv0
    orderQuantity = 0
    for i in range(numToPred):
        startInv = finalInv
        orderQuantity = np.round(np.max(forecastPlusSec[i] - startInv, 0), decimals = 2)
        auxTerm = orderQuantity + startInv - realDemand[i]
        finalInv = np.max(auxTerm, 0)
        toRet[i,0] = startInv
        toRet[i,1] = orderQuantity
        toRet[i,2] = finalInv
        toRet[i,3] = finalInv
        toRet[i,4] = np.maximum(-auxTerm, 0.0)*3
    return toRet

if __name__ == '__main__':
    currentDirectory = os.getcwd()
    condFileHasNotBeingRead = True
    DFDemand = 0
    while condFileHasNotBeingRead:
        answerInputName = input('Which csv or txt in folder '+str(os.getcwd())+\
            ' has the past demand data'+"\n"+\
            '(Please add at the end of the name the .csv or .txt depending on which type you are using.' +"\n"+\
            'Make sure that your file is delimited by commas.):')
        fname = currentDirectory+'/'+answerInputName
        if os.path.isfile(fname):
            print('File Found')
            if fname[-3:] not in ['txt', 'csv']:
                print(fname + ' does not finish in csv or txt, try again.')
            else:
                pdData = pd.read_csv(fname)
                if len(list(pdData.columns)) ==3:
                    condFileHasNotBeingRead =  False
                    DFDemand = pd.read_csv(fname, names=['Year', 'Count', 'Demand'], skiprows=1)

                    # Fill NaN with previous year 
                    DFDemand = DFDemand.fillna(method='ffill')

                    # # Years to int and months from 1 to 12
                    DFDemand.Year = DFDemand.Year.astype(np.int)
                    DFDemand['Month'] = DFDemand.Count.apply(lambda x: x % 12 if x % 12 != 0 else 12)
                    # DFDemand.head(24)
                    DFDemand["Year-Month"] = DFDemand["Year"].map(str) + ["-"+str(i %12 +1) for i in range(len(DFDemand['Month']))]
                else:
                    print('The file does not have three columns')
        else:
            print(fname + ' does not exist.')
            print('Please try again.')
    print()
    print()
    inv0 = 73

    condStartingInventoryNotANumber = True
    while condStartingInventoryNotANumber:
        answerInputName = input('Which is the remaining inventory from last month:'+"\n"+\
            '(If you press enter we will use 73 as it is said in the competition .pdf):')
        if answerInputName=="":
            condStartingInventoryNotANumber = False
        else:
            try:
                float(answerInputName)
                condStartingInventoryNotANumber = False
                inv0 = float(answerInputName)
            except ValueError:
                print(answerInputName + 'is not a number. Please enter a number.')

    print()

    numToPredict = 24
    condStartingPeriodsToPredict = True
    while condStartingPeriodsToPredict:
        answerInputName = input('How many months do you want the method to predict:'+"\n"+\
            '(If you press enter we will use 24):')
        if answerInputName=="":
            condStartingPeriodsToPredict = False
        else:
            try:
                int(answerInputName)
                condStartingPeriodsToPredict = False
                numToPredict = int(answerInputName)
            except ValueError:
                print(answerInputName + 'is not a number. Please enter a number.')

    print()

    print('Running the forecast method and bias term.')
    predForecast, secAmount = predMethod(np.array(DFDemand['Demand']), frequency =12, numToPredict = numToPredict)

    dataToAdd = createStartEndInvAndOrderQuantity(predForecast+secAmount, np.array(DFDemand['Demand'])[-numToPredict:], inv0 = inv0)

    dfResults = DFDemand[len(DFDemand['Demand'])-numToPredict:].copy()

    dfResults['Beginning_Inventory'] = dataToAdd[:,0]
    dfResults['Order_Quantity'] = dataToAdd[:,1]
    dfResults['Final_Inventory'] = dataToAdd[:,2]
    dfResults['Holding_Cost'] = dataToAdd[:,3]
    dfResults['Shortage_Cost'] = dataToAdd[:,4]

    print('We will save in the current folder the results in ResultsLobosPais_OriginalFormat.csv')
    print('and ResultsLobosPais.csv, depending if you preffer to have a the results in a better format.')

    # dfOrigFormat = dfResults[['Year', 'Count', 'Demand','Beginning_Inventory', 'Order_Quantity',\
    #                         'Final_Inventory', 'Holding_Cost', 'Shortage_Cost']].copy()
    # dfOrigFormat.to_csv(index=False, path_or_buf ='ResultsLobosPais_OriginalFormat.csv')
    dfNicerFormat = dfResults[['Year-Month','Demand', 'Beginning_Inventory', 'Order_Quantity',\
                            'Final_Inventory', 'Holding_Cost', 'Shortage_Cost']].copy()
    dfNicerFormat.to_csv(index=False, path_or_buf ='Results.csv')
    dfNicerFormat.index = np.arange(len(dfNicerFormat['Demand']))

    print('We finish by showing the results in the command line')
    print(dfNicerFormat)
    
    print()


    summaryFirstRow = ['Total', str(np.sum(dataToAdd[:,3]+dataToAdd[:,4])),\
        str(np.sum(dataToAdd[:,3])), str(np.sum(dataToAdd[:,4]))]
    summarySecondRow = ['Average', str(np.average(dataToAdd[:,3]+dataToAdd[:,4])),\
        str(np.average(dataToAdd[:,3])), str(np.average(dataToAdd[:,4]))]

    with open('Summary.csv', 'w') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['', 'Cost All','Holding Cost', 'Shortage Cost'])
        writer.writerow(summaryFirstRow)
        writer.writerow(summarySecondRow)
    csvFile.close()

    print()