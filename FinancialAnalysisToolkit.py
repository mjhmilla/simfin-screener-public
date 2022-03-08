from errno import ENETRESET
import numpy as np
import math as math
import pandas as pd
from scipy.stats.mstats import rankdata

import simfin as sf
from simfin.names import *

import matplotlib.pyplot as plt
from matplotlib import gridspec

import ParametricModels as pm

RETURN_ON_ENTERPRISE = 'Return on Enterprise' 

#The 'p' in SimFin's tag for this should be capitalized and is not.
EARNINGS_PER_SHARE_BASIC = 'Earnings Per Share, Basic'


def calcReturnOnEnterprise(company_income,company_derived_shareprices):
    return   company_income[NET_INCOME].values \
            /company_derived_shareprices[ENTERPRISE_VALUE].values                         

def getFinancialValuesByName(company_shareprices, company_derived_shareprices, \
    company_income, company_balance, company_cashflow, company_derived,\
    name):
   
    if name == RETURN_ON_ENTERPRISE:
        return calcReturnOnEnterprise(company_income, \
                                        company_derived_shareprices), True       
    elif name in company_shareprices:
        return company_shareprices[name].values, True
    elif name in company_derived_shareprices:
        return company_derived_shareprices[name].values, True
    elif name in company_income:
        return company_income[name].values, True
    elif name in company_balance:
        return company_balance[name].values, True
    elif name in company_cashflow:
        return company_cashflow[name].values, True
    elif name in company_derived:
        return company_derived[name].values, True
    elif name in company_derived:
        return company_derived[name].values, True
    else:
        return np.zeros(np.shape(0,0)), False
    

def selectBusinessesForAnalysis(companies,  shareprices, derived_shareprices, \
                        income, balance, cashflow, derived, \
                            minimumAcceptableRecordLengthInYears, logFileName,\
                            verbose):
    
    acceptable=0
    unacceptable=0
    total=0
    companiesScreened = []

    createLogFile = False
    f=[]
    if len(logFileName)>0:
        createLogFile=True
        f=open(logFileName,'w')

    for ticker in companies.T:
        valid=True
        if ticker not in shareprices.index:
            valid=False
            if verbose:
                print(ticker + ' Missing shareprice information')
            if createLogFile:
                f.write(ticker + ' Missing shareprice information'+'\n')
        if ticker not in derived_shareprices.index:
            valid=False
            if verbose:
                print(ticker + ' Missing derived_shareprice information')
            if createLogFile:
                f.write(ticker + ' Missing derived_shareprice information'+'\n')
        if ticker not in income.index:
            valid=False
            if verbose:
                print(ticker + ' Missing income information')
            if createLogFile:
                f.write(ticker + ' Missing income information'+'\n')
        if ticker not in balance.index:
            valid=False
            if verbose:            
                print(ticker + ' Missing balance information')
            if createLogFile:
                f.write(ticker + ' Missing balance information'+'\n')
        if ticker not in cashflow.index:
            valid=False
            if verbose:
                print(ticker + ' Missing cashflow information')
            if createLogFile:
                f.write(ticker + ' Missing cashflow information'+'\n')
        if ticker not in derived.index:
            valid=False
            if verbose:
                print(ticker + ' Missing derived information')
            if createLogFile:
                f.write(ticker + ' Missing derived information'+'\n')
        if valid:
            years   = derived.loc[ticker][EQUITY_PER_SHARE].axes[0].year.values
            timeSpan = max(years) - min(years)
            if timeSpan < minimumAcceptableRecordLengthInYears:
                valid=False
                if verbose:
                    print(ticker + ': Record too short:' + str(timeSpan) \
                        + ' < ' + str(minimumAcceptableRecordLengthInYears))
                if createLogFile:
                    f.write(ticker + ': Record too short:' + str(timeSpan) \
                        + ' < ' + str(minimumAcceptableRecordLengthInYears)+'\n')
        if valid:
            acceptable=acceptable+1
            companiesScreened.append(ticker)
            if createLogFile:
                f.write(str(acceptable)+'. '+ticker+'\n')
        else:
            unacceptable=unacceptable+1
        total=total+1
    if verbose:
        print(str(acceptable)+' Acceptable')  
        print(str(unacceptable)+' Unacceptable')  
        print(str(total)+' Total') 
        if createLogFile: 
            f.write(str(acceptable)+' Acceptable\n')  
            f.write(str(unacceptable)+' Unacceptable\n')  
            f.write(str(total)+' Total\n')  
            f.close()

    return companiesScreened


def createBusinessRatingTable(  companies, shareprices, derived_shareprices, \
                        income, balance, cashflow, derived,\
                        metricNames, metricModel, metricUnit, metricScaling,\
                        verbose    ):

    
    indexTicker=0                     
    mktData     = np.zeros((len(companies),len(metricNames)))
    mktDataModelErrorNorm  = np.zeros((len(companies),len(metricNames)))
    for index in range(0,len(companies)):
        ticker = companies[index]

        if  ticker in shareprices.index and \
            ticker in derived_shareprices.index and \
            ticker in income.index and \
            ticker in derived.index and \
            ticker in balance.index:

            #Sufficient data
            #Copy over the company data to make the code more readable
            spX     = shareprices.loc[ticker].copy()
            dspX    = derived_shareprices.loc[ticker].copy()
            incX    = income.loc[ticker].copy()
            balX    = balance.loc[ticker].copy()
            cfX     = cashflow.loc[ticker].copy()
            dfX     = derived.loc[ticker].copy()
            years   = dfX[metricNames[1]].axes[0].year.values
            values  = np.zeros(np.shape(years))
            

            #We have enough data to evaluate
            if(verbose):
                print(ticker)

            if ticker=='ACAD':
                here=True

            indexMetric=0
            for metric in metricNames:

                values, found = getFinancialValuesByName(spX, dspX, incX, \
                                balX, cfX, dfX, metric)
                        
                if found:
                    #Fit the specified model to the data and extract the 
                    # summary statistics                    
                    scaling = 1.
                    if metricScaling[indexMetric] == 'percent':
                        scaling = 100.

                    if(metricModel[indexMetric]=='average'):
                        constMdl = pm.ConstantModel(years,values)
                        #Save the average value
                        mktData[indexTicker,indexMetric] = constMdl.a*scaling
                        mktDataModelErrorNorm[indexTicker,indexMetric]= \
                            constMdl.calcMeanSquaredError(years,values) 

                    if(metricModel[indexMetric]=='linear'):
                        linMdl = pm.LinearModel(years,values)
                        #Save the slope
                        mktData[indexTicker,indexMetric] = linMdl.b*scaling 
                        mktDataModelErrorNorm[indexTicker,indexMetric]= \
                            linMdl.calcMeanSquaredError(years,values) 

                    if(metricModel[indexMetric]=='exponential'):
                        expMdl=pm.ExponentialModel(years,values)
                        #Save the base of the exponential
                        mktData[indexTicker,indexMetric] = (expMdl.c-1.)*scaling
                        mktDataModelErrorNorm[indexTicker,indexMetric]= \
                            expMdl.calcMeanSquaredError(years,values) 
                    
                else:
                    mktData[indexTicker,indexMetric]=np.NaN

                #Normalize the mean-squared-errors
                nanItems=np.isnan(values)
                if len(values[~nanItems]) > 1:
                    if (max(values[~nanItems])-min(values[~nanItems])) > 0:
                        mktDataModelErrorNorm[indexTicker,indexMetric]= \
                            math.sqrt(mktDataModelErrorNorm[indexTicker,indexMetric])\
                                /  (max(values[~nanItems])-min(values[~nanItems]))
                    else:
                        mktDataModelErrorNorm[indexTicker,indexMetric]=math.nan    
                else:
                    mktDataModelErrorNorm[indexTicker,indexMetric]=math.nan
                indexMetric=indexMetric+1  
                        #If the data record is too short, ignore it: this is too risky.
            
        else:
            #Insufficient data
            print(ticker + ' No Data')
            for indexMetric in range(0,len(metricNames)):
                    mktData[indexTicker,indexMetric]=np.NaN

        indexTicker=indexTicker+1 

    return mktData,mktDataModelErrorNorm

def calcTownValuationTable(companies, shareprices, shareprices_derived, derived,\
    minimumAcceptableRateOfReturn, valueProjectionTimeInYears):

    indexTicker=0                     
    valueData   = np.zeros((len(companies),3))
    indexPrice=0
    indexValue=1
    indexMarginOfSafety=2    

    for indexTicker in range(0,len(companies)):
        ticker=companies[indexTicker]
        if  ticker in shareprices.index and \
            ticker in shareprices_derived.index and \
            ticker in derived.index :

            #Sufficient data
            #Copy over the company data to make the code more readable
            spX     = shareprices.loc[ticker].copy()
            dspX    = shareprices_derived.loc[ticker].copy()
            dfX     = derived.loc[ticker].copy()
            years   = dfX[EQUITY_PER_SHARE].axes[0].year.values
            
            currentPrice = spX[CLOSE].values[-1]

            currentValue = calcTownValuation(dspX, dfX, \
                minimumAcceptableRateOfReturn,valueProjectionTimeInYears)

            currentValue = max(currentValue,0)

            currentMarginOfSafety = np.NaN
            if currentValue > 0:
                currentMarginOfSafety=currentPrice/currentValue

            valueData[indexTicker,indexPrice] = currentPrice
            valueData[indexTicker,indexValue] = currentValue
            valueData[indexTicker,indexMarginOfSafety] = currentMarginOfSafety
        else:
            nrowsValue,ncolsValue = np.shape(valueData)
            for indexValueMetric in range(0,ncolsValue):
                valueData[indexTicker,indexValueMetric] = np.NaN 
        indexTicker=indexTicker+1  

    return valueData

# Use the method described by Phile Town in 'Rule #1 Investing' to 
# evaluate the value of the stock. This is a very simple method which
# assumes that earnings will continue to grow exponentially with the
# rate of equity. Obviously if the company is both big and growing 
# quicky this method can produce non-sensical results such as a single
# company becoming a significant fraction of the economny.
def calcTownValuation(company_shareprice_derived, company_derived, minimumAcceptableRateOfReturn,\
    valueProjectionTimeInYears):

    years   = company_derived[EQUITY_PER_SHARE].axes[0].year.values
    values  = company_derived[EQUITY_PER_SHARE].values
    expMdl  = pm.ExponentialModel(years,values)
    equityPerShareGrowth = (expMdl.c-1.)

    if(expMdl.c < 1.0):
        here=True

    #year = company_derived[PE_TTM].axis[0].year.values[0]

    #Trailing 12 month PE
    priceToEarningTTM = company_shareprice_derived[PE_TTM].values[-1]
    priceToEarningTTM_years = company_shareprice_derived[PE_TTM].axes[0].year.values

    #Hueristic value of a fair PE
    currentEarningsPerShare = company_derived[EARNINGS_PER_SHARE_BASIC].values[-1]
    currentEarningsPerShare_years = company_derived[EARNINGS_PER_SHARE_BASIC].axes[0].year.values
    #assert(len(currentEarningsPerShare)==1)
    priceToEarningDefault   = max(equityPerShareGrowth*100.*2.0,1.0)

    futurePriceToEarning = min(priceToEarningTTM, priceToEarningDefault)

    futureEarningsPerShare = currentEarningsPerShare \
        * math.pow(1.+equityPerShareGrowth,valueProjectionTimeInYears)

    futurePrice = futureEarningsPerShare*futurePriceToEarning

    currentValue = futurePrice \
        / math.pow(1.+minimumAcceptableRateOfReturn, valueProjectionTimeInYears)    
    
    return currentValue


def plotBusinessMetrics(fig, axes, tickerName, company_shareprices, \
    company_derived_shareprices, company_income, company_balance, \
    company_cashflow, company_derived, metricNames, metricModel, \
    metricUnit, metricScaling, price, value, marginOfSafety, \
    rows,cols, pageWidth, pageHeight, \
    outputDirectory, prependToName, savePlot):

    years   = company_derived[metricNames[1]].axes[0].year.values

    indexMetric=0
    valuationDataWritten=False
    for metric in metricNames:
                
        #if metric in company_derived or metric == RETURN_ON_ENTERPRISE:
        #Extract the raw data   
        values, found = getFinancialValuesByName(company_shareprices, \
            company_derived_shareprices, company_income, company_balance,\
            company_cashflow, company_derived, metric)

        
        if found:

            row = int(np.floor(indexMetric/cols))
            col = int(indexMetric-row*cols)

            if len(values) > 0:
                nanItems = np.isnan(values)
                if len(values[~nanItems]) > 0:
                    #Plot the raw data
                    axes[row,col].set_title(metric) 
                    axes[row,col].plot(years[~nanItems], values[~nanItems],
                                        '-ob',label='Data') 

            #Fit the specified model to the data and extract the 
            # summary statistics                    
            modelValues = values
            scaling = 1.
            if metricScaling[indexMetric] == 'percent':
                scaling = 100.

            if(metricModel[indexMetric]=='average'):
                constMdl = pm.ConstantModel(years,values)
                modelValues = constMdl.calcValue(years)
                modelLabel = constMdl.getEquationLabel(scaling)
            elif(metricModel[indexMetric]=='linear'):
                linMdl = pm.LinearModel(years,values)
                modelValues = linMdl.calcValue(years)
                modelLabel = linMdl.getEquationLabel(scaling)
            elif(metricModel[indexMetric]=='exponential'):
                expMdl=pm.ExponentialModel(years,values)
                modelValues = expMdl.calcValue(years)
                modelLabel = expMdl.getEquationLabel(scaling)
            else:
                raise KeyError('Metric model not found: '+metricModel[indexMetric])

            axes[row,col].plot(years, modelValues,'r',label='Fitted') 

            itemsYears=np.isfinite(years)
            itemsValues=np.isfinite(values)

            if len( years[itemsYears]) > 1 and \
               len(values[itemsValues]) > 1 :            
                yearsUpd=years[itemsYears]
                valuesUpd=values[itemsValues]
                xpos = yearsUpd[0]
                ypos = max(valuesUpd)
                axes[row,col].text(xpos,ypos,modelLabel)

            if valuationDataWritten==False:
                valid=False
                y1=1
                y0=0
                xpos = 0
                if  len( years[itemsYears]) > 1 and \
                    len(values[itemsValues]) > 1 :            
                    yearsUpd=years[itemsYears]
                    valuesUpd=values[itemsValues]
                    y1=max(valuesUpd)
                    y0=min(valuesUpd)    
                    xpos=min(yearsUpd)                               
                    valid=True 
                ypos = y0+0.2*(y1-y0)
                    
                    

                fontcolor = 'black'
                if marginOfSafety <= 0.5:
                    fontcolor='blue'
                font={'color':fontcolor}
                infoStr = '{:.2F}: price\n{:.2F}: value\n{:.2F}: margin of safety\n'.format(price, value,marginOfSafety)

                if valid:
                    axes[row,col].text(xpos,ypos,infoStr,fontdict=font)
                else:
                    axes[row,col].text(xpos,ypos,'empty evaluation data',fontdict=font)
                valuationDataWritten=True

            if(metricUnit == 'currency'):
                axes[row,col].set_xlabel(company_derived[CURRENCY].iloc[-1])

            fig.subplots_adjust(top=0.8)
            #fig.tight_layout()

        indexMetric=indexMetric+1
    
    if(savePlot):
        fname = tickerName.replace('.','_',1)
        fname = prependToName+fname + '.png'
        fig.savefig(outputDirectory+fname)
    
    return fig
