from cmath import nan
from tokenize import Exponent
from numpy.ma.core import masked_invalid
from scipy.stats.mstats import rankdata
import os
import warnings

import simfin as sf
from simfin.names import *


import math as math

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib import gridspec

import ParametricModels as pm
import FinancialAnalysisToolkit as fat

flag_SimFinApiPlusKey       = False

if flag_SimFinApiPlusKey:
    sf.set_api_key('YOUR_SIMFIN_API_PLUS_KEY_HERE')
else:
    sf.set_api_key('YOUR_FREE_SIMFIN_API_KEY_HERE')

sf.set_data_dir('simfin-data')

flag_printSpecificMarketData = True
minimumAcceptableRecordLengthInYears = 5
valueProjectionTimeInYears = 10
minimumAcceptableRateOfReturn = 0.15 
outputDirectory = 'output'

smallEnterpriseValue = 1000000000

flag_printTickers       = False
flag_printPrices        = True
flag_printDerivedPrices = True
flag_printIncomeFields  = True
flag_printBalanceFields = True
flag_printCashFields    = True
flag_printDerivedFields = True

#Otherwise the minimum of PE_TTM and 2*EPS_GROWTH is used
flag_usePETTMForFutureValuation = False
flag_usePEDefaultFutureValuation = False

flag_plotTopData           = True
numberOfTopCompaniesToPlot = 15

setting_refresh_days = 1 #Keeping the data the same for testing purposes

mktSet = ['ca','cn','de','us']
usPrintList = ['NYT','NVDA','DOC','VRTX','V','MA']

for indexMarket in range(0,len(mktSet)):

    mkt = mktSet[indexMarket]#'de'
    var = 'annual'

    print('0. Analyzing: '+mkt)

    #Plotting config
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.rc('axes',  labelsize=10)
    plt.rc('xtick', labelsize=8)
    plt.rc('ytick', labelsize=8)
    plt.rc('legend',fontsize=8)


    cp = sf.load_companies(market=mkt,refresh_days=setting_refresh_days)
    if flag_printTickers:
        print("Tickers")
        i=1
        for ticker in cp.T:
            print("\t"+str(i)+"\t"+ticker)
            i=i+1

    sp = sf.load_shareprices(market=mkt, refresh_days=setting_refresh_days)
    if flag_printPrices:
        print("Share Prices")
        i=1
        for col in sp.columns:
            print("\t"+str(i)+"\t"+col)  
            i=i+1     

            
    dsp = sf.load_derived_shareprices(market=mkt,refresh_days=setting_refresh_days)
    if flag_printDerivedPrices:
        print("Price Multiples")
        i=1
        for col in dsp.columns:
            print("\t"+str(i)+"\t"+col)  
            i=i+1       


    inc=sf.load_income(variant=var,market=mkt,
            index=[TICKER,REPORT_DATE],
            parse_dates=[REPORT_DATE,PUBLISH_DATE,RESTATED_DATE],
            refresh_days=setting_refresh_days)
    if flag_printIncomeFields:
        print("Income Statement Fields")
        i=1
        for col in inc.columns:
            print("\t"+str(i)+"\t"+col)  
            i=i+1      

    bal=sf.load_balance(variant=var,market=mkt,
            index=[TICKER,REPORT_DATE],
            parse_dates=[REPORT_DATE,PUBLISH_DATE,RESTATED_DATE],
            refresh_days=setting_refresh_days)

    if flag_printBalanceFields:
        print("Balance Statement Fields")
        i=1
        for col in bal.columns:
            print("\t"+str(i)+"\t"+col)  
            i=i+1       

    cf =sf.load_cashflow(variant=var,market=mkt,
            index=[TICKER,REPORT_DATE],
            parse_dates=[REPORT_DATE,PUBLISH_DATE,RESTATED_DATE],
            refresh_days=setting_refresh_days)        

    if flag_printCashFields:        
        print("Cash Flow Fields")
        i=1
        for col in cf.columns:
            print("\t"+str(i)+"\t"+col)         
            i=i+1

    #A premium key is needed for the variants        
    df =sf.load_derived(variant=var,market=mkt,
            index=[TICKER,REPORT_DATE],
            parse_dates=[REPORT_DATE,PUBLISH_DATE,RESTATED_DATE],
            refresh_days=setting_refresh_days)
    if flag_printDerivedFields:        
        print("Derived Fields")    
        i=1
        for col in df.columns:
            print("\t"+str(i)+"\t"+col)         
            i=i+1



    if flag_printSpecificMarketData:

        metricNames = []
        fittingType = []
        unitType = []
        scalingType = []
        includeInRank = []

        indexEquityPerShare     = 1
        indexEarningPerShare    = 2

        nameReturnOnEnterprise = 'Return on Enterprise'

        #From Joel Greenblatt's 'The little green book that
        #still beats the market':
        #
        #Return on enterprise is a less noisy metric of overall
        #growth that return on invested capital because what
        #counts as capital is subject to out-of-date rules that
        #do not accurately many modern businesses, particularly
        #technology companies.
        #
        metricNames.append(nameReturnOnEnterprise)
        fittingType.append('average')
        unitType.append('')
        scalingType.append('percent')
        includeInRank.append(True)

        if flag_SimFinApiPlusKey: 
            metricNames.append(EQUITY_PER_SHARE)
            fittingType.append('exponential')   
            unitType.append('currency')
            scalingType.append('percent')
            includeInRank.append(True)

        if flag_SimFinApiPlusKey:
            #There is a typo in the EPS_BASIC and EPS_DILUTED fields
            metricNames.append('Earnings Per Share, Basic')
            fittingType.append('exponential')    
            unitType.append('currency')
            scalingType.append('percent')
            includeInRank.append(True)

        if flag_SimFinApiPlusKey:
            metricNames.append(SALES_PER_SHARE)
            fittingType.append('exponential')  
            unitType.append('currency')
            scalingType.append('percent')
            includeInRank.append(True)

        if flag_SimFinApiPlusKey:
            metricNames.append(FCF_PS)
            fittingType.append('exponential') 
            unitType.append('currency')
            scalingType.append('percent')
            includeInRank.append(True)

        metricNames.append(DEBT_RATIO)
        fittingType.append('exponential') 
        unitType.append('currency')
        scalingType.append('percent')
        includeInRank.append(False)

        metricNames.append(NET_CASH_OPS)
        fittingType.append('exponential') 
        unitType.append('currency')
        scalingType.append('percent')
        includeInRank.append(False)

        metricNames.append(TOTAL_EQUITY)
        fittingType.append('exponential') 
        unitType.append('currency')
        scalingType.append('percent')
        includeInRank.append(False)




        logFileName = outputDirectory+'/'+mkt+'_log.txt'

        if os.path.exists(logFileName):
            os.remove(logFileName)

        print('1. Selecting companies to screen')
        cpScreened = fat.selectBusinessesForAnalysis(cp,sp,dsp,inc,bal,cf,df,\
            minimumAcceptableRecordLengthInYears, \
                logFileName, False)

        print('2. Building the business rating table')
        mktData,mktDataModelErrorNorm = fat.createBusinessRatingTable(cpScreened,sp,dsp,inc,bal,cf,df,\
            metricNames,fittingType,unitType,scalingType,False)


        #Rank each company based on its business metrics and margin of safety
        indexPrice=0
        indexValue=1
        indexMarginOfSafety=2
        valueData   = np.zeros((len(cpScreened),3))

        indexTicker=0
        numberOfTickers= len(cpScreened)

        print('3. Evaluting the value of the business using Phil Town s method')
        valueData = fat.calcTownValuationTable(cpScreened,sp,dsp,df,
            minimumAcceptableRateOfReturn,valueProjectionTimeInYears)


        #Rank companies from lowest (best) margin-of-safety to the biggest
        valueDataRank = np.zeros((len(cpScreened),1))
        worstMarginOfSafety = 2*max(valueData[:,indexMarginOfSafety])
        colData = np.nan_to_num(valueData[:,indexMarginOfSafety],True,worstMarginOfSafety)
        valueDataRank = rankdata(colData).astype(int)

        #Evaluate the individual metric rankings
        mktDataRank = np.zeros((len(cpScreened),len(metricNames)))
        mktDataModelErrorRank = np.zeros((len(cpScreened),len(metricNames)))
        mktDataRankOverall = np.zeros((len(cpScreened),2),dtype=int)

        #overallRank: minimum sum of the MOS and metric rank
        #             looking for a great business at a great price
        overallRank = np.zeros((len(cpScreened),2),dtype=int)

        print('4. Ranking each business')
        #Ranking by the rate of growth of each metric
        for indexMetric in range(0, len(metricNames)):
            colData = np.ma.masked_invalid(mktData[:,indexMetric]) 
            #If there is some valid data, rank it
            if np.sum(np.isnan(colData))<len(colData) and includeInRank[indexMetric]:
                mktDataRank[:,indexMetric] = len(colData)-rankdata(colData).astype(int)
                mktDataRank[:,indexMetric] = mktDataRank[:,indexMetric]\
                    -min(mktDataRank[:,indexMetric])+1
            else:
            #Otherwise assign a column of NaN's      
                mktDataRank[:,indexMetric] = np.NaN
        #Ranking by the variation of the data w.r.t. the model
        for indexMetric in range(0, len(metricNames)):
            colData = np.ma.masked_invalid(mktDataModelErrorNorm[:,indexMetric]) 
            #If there is some valid data, rank it
            if np.sum(np.isnan(colData))<len(colData) and includeInRank[indexMetric]:
                mktDataModelErrorRank[:,indexMetric] = rankdata(colData).astype(int)
                mktDataModelErrorRank[:,indexMetric] = \
                    mktDataModelErrorRank[:,indexMetric] \
                    -min(mktDataModelErrorRank[:,indexMetric])+1
            else:
            #Otherwise assign a column of NaN's      
                mktDataModelErrorRank[:,indexMetric] = np.NaN        

        #Get the overall metric ranking
        rows,cols = np.shape(mktDataRankOverall)
        numberOfNaNsInRow = np.zeros(np.shape(valueDataRank))
        for indexMetric in range(0,len(metricNames)):
            if includeInRank[indexMetric]:
                mktDataRankOverall[:,0] = mktDataRankOverall[:,0] \
                    + np.nan_to_num(mktDataRank[:,indexMetric],True,rows) \
                    + np.nan_to_num(mktDataModelErrorRank[:,indexMetric],True,rows)
                numberOfNaNsInRow = numberOfNaNsInRow + np.isnan(mktDataRank[:,indexMetric])
        mktDataRankOverall[:,1] = rankdata( mktDataRankOverall[:,0] ).astype(int)

        numberOfNaNsInRow = numberOfNaNsInRow + np.isnan(valueData[:,indexMarginOfSafety])

        #Get the overall metric + margin-of-safety ranking
        overallRank[:,0] = mktDataRankOverall[:,1] + valueDataRank[:]
        overallRank[:,1] = rankdata(overallRank[:,0]).astype(int)

        overallDataOrder = np.zeros((rows,cols),dtype=int)
        mktDataOrder     = np.zeros((rows,cols),dtype=int)
        valueDataOrder   = np.zeros((rows,cols),dtype=int)

        indexOfEntries = 0
        for i in range(0, rows):
            if numberOfNaNsInRow[i] == 0:
                overallDataOrder[indexOfEntries,0]  = int(i)
                overallDataOrder[indexOfEntries,1]  = int(overallRank[i,1])
                mktDataOrder[indexOfEntries,0]      = int(i)
                mktDataOrder[indexOfEntries,1]      = int(mktDataRankOverall[i,1])
                valueDataOrder[indexOfEntries,0]    = int(i)
                valueDataOrder[indexOfEntries,1]    = int(valueDataRank[i])
                indexOfEntries=indexOfEntries+1
        for i in range(0, rows):
            if numberOfNaNsInRow[i] > 0:
                overallDataOrder[indexOfEntries,0]=int(i)
                overallDataOrder[indexOfEntries,1]=int(overallRank[i,1])
                mktDataOrder[indexOfEntries,0]      = int(i)
                mktDataOrder[indexOfEntries,1]      = int(mktDataRankOverall[i,1])
                valueDataOrder[indexOfEntries,0]    = int(i)
                valueDataOrder[indexOfEntries,1]    = int(valueDataRank[i])            
                indexOfEntries=indexOfEntries+1
        
        overallDataOrderSorted  = overallDataOrder[np.argsort(overallDataOrder[:,1])]    
        mktDataOrderSorted      = mktDataOrder[np.argsort(mktDataOrder[:,1])]
        valueDataOrderSorted    = valueDataOrder[np.argsort(valueDataOrder[:,1])]


        cm = 1/2.54
        rows=3
        cols=3
        pageWidth  = 42.0*cm
        pageHeight = 29.7*cm

        if flag_plotTopData:
            fig, axes =plt.subplots(nrows=rows,ncols=cols,
                                figsize=(pageWidth,pageHeight))

        indexOverallRank=0
        #Output the best overall
        print('5. Writing tables and plots to file') 

        if mkt == 'us' and len(usPrintList) > 0:
            for indexTicker in range(0,len(cpScreened)):
                ticker = cpScreened[indexTicker]
                for indexPrint in range(0,len(usPrintList)):
                    if usPrintList[indexPrint]==ticker:
                      fig = fat.plotBusinessMetrics(fig, axes, ticker, sp.loc[ticker], 
                        dsp.loc[ticker],inc.loc[ticker], bal.loc[ticker],  
                        cf.loc[ticker], df.loc[ticker], metricNames, 
                        fittingType, unitType, scalingType,
                        valueData[indexTicker,indexPrice],
                        valueData[indexTicker,indexValue],
                        valueData[indexTicker,indexMarginOfSafety],
                        rows,cols,pageWidth,pageHeight,
                        outputDirectory+'/'+mkt+'/', 
                        'custom_', True)
                      for row in range(0,rows):
                        for col in range(0,cols):
                            axes[row,col].cla()    





        with open( outputDirectory+'/'+mkt+'_overall'+'.csv','wt',newline='') as csvfile:
            rowStr = 'Ticker,'
            indexMetric=0        
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth'
                indexMetric=indexMetric+1
            indexMetric=0
            rowStr = rowStr+','
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth_Rank'            
                indexMetric=indexMetric+1
            rowStr = rowStr+',Business_Score,Business_Rank,Price,Value,Price_To_Value,Price_To_Value_Rank,Overall_Rank'
            print(rowStr,file=csvfile)
        

            for indexTicker in overallDataOrderSorted[:,0]:
                ticker = cpScreened[indexTicker]
                tickerName = ticker.replace('.','_',1)
                rowStr = tickerName
                for j in range(0,mktData.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktData[indexTicker,j])
                for j in range(0,mktDataRank.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRank[indexTicker,j])
                for j in range(0,mktDataRankOverall.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRankOverall[indexTicker,j])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexPrice])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexValue])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexMarginOfSafety])
                rowStr = rowStr +','+'{:.2F}'.format(valueDataRank[indexTicker])
                rowStr = rowStr +','+'{:.2F}'.format(overallRank[indexTicker,1])
                print(rowStr,file=csvfile)


                if flag_plotTopData and indexOverallRank <= numberOfTopCompaniesToPlot:
                    fig = fat.plotBusinessMetrics(fig, axes, ticker, sp.loc[ticker], 
                        dsp.loc[ticker],inc.loc[ticker], bal.loc[ticker],  
                        cf.loc[ticker], df.loc[ticker], metricNames, 
                        fittingType, unitType, scalingType,
                        valueData[indexTicker,indexPrice],
                        valueData[indexTicker,indexValue],
                        valueData[indexTicker,indexMarginOfSafety],
                        rows,cols,pageWidth,pageHeight,
                        outputDirectory+'/'+mkt+'/', 
                        'overall_'+str(indexOverallRank)+'_', True)            
                    for row in range(0,rows):
                        for col in range(0,cols):
                            axes[row,col].cla()
                indexOverallRank=indexOverallRank+1

        #Output the best growth
        with open( outputDirectory+'/'+mkt+'_growth'+'.csv','wt',newline='') as csvfile:
            rowStr = 'Ticker,'
            indexMetric=0        
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth'
                indexMetric=indexMetric+1
            indexMetric=0
            rowStr = rowStr+','
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth_Rank'            
                indexMetric=indexMetric+1
            rowStr = rowStr+',Business_Score,Business_Rank,Price,Value,Price_To_Value,Price_To_Value_Rank,Overall_Rank'
            print(rowStr,file=csvfile)
        
            indexGrowthRank=0
            for indexTicker in mktDataOrderSorted[:,0]:
                ticker = cpScreened[indexTicker]
                tickerName = ticker.replace('.','_',1)
                rowStr = tickerName
                for j in range(0,mktData.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktData[indexTicker,j])
                for j in range(0,mktDataRank.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRank[indexTicker,j])
                for j in range(0,mktDataRankOverall.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRankOverall[indexTicker,j])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexPrice])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexValue])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexMarginOfSafety])
                rowStr = rowStr +','+'{:.2F}'.format(valueDataRank[indexTicker])
                rowStr = rowStr +','+'{:.2F}'.format(overallRank[indexTicker,1])
                print(rowStr,file=csvfile)
                if flag_plotTopData and indexGrowthRank <= numberOfTopCompaniesToPlot:
                    fig = fat.plotBusinessMetrics(fig, axes, ticker, sp.loc[ticker], 
                        dsp.loc[ticker],inc.loc[ticker], bal.loc[ticker],  
                        cf.loc[ticker], df.loc[ticker], metricNames, 
                        fittingType, unitType, scalingType,
                        valueData[indexTicker,indexPrice],
                        valueData[indexTicker,indexValue],
                        valueData[indexTicker,indexMarginOfSafety],                    
                        rows,cols,pageWidth,pageHeight,
                        outputDirectory+'/'+mkt+'/', 
                        'growth_'+str(indexGrowthRank)+'_', True)            
                    for row in range(0,rows):
                        for col in range(0,cols):
                            axes[row,col].cla()
                indexGrowthRank=indexGrowthRank+1

        #Output the best margin of safety
        with open( outputDirectory+'/'+mkt+'_mos'+'.csv','wt',newline='') as csvfile:
            rowStr = 'Ticker,'
            indexMetric=0        
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth'
                indexMetric=indexMetric+1
            indexMetric=0
            rowStr = rowStr+','
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth_Rank'            
                indexMetric=indexMetric+1
            rowStr = rowStr+',Business_Score,Business_Rank,Price,Value,Price_To_Value,Price_To_Value_Rank,Overall_Rank'
            print(rowStr,file=csvfile)
        
            indexMarginOfSafetyRank=0
            for indexTicker in valueDataOrderSorted[:,0]:
                ticker = cpScreened[indexTicker]
                tickerName = ticker.replace('.','_',1)
                rowStr = tickerName
                for j in range(0,mktData.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktData[indexTicker,j])
                for j in range(0,mktDataRank.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRank[indexTicker,j])
                for j in range(0,mktDataRankOverall.shape[1]):
                    rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRankOverall[indexTicker,j])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexPrice])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexValue])
                rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexMarginOfSafety])
                rowStr = rowStr +','+'{:.2F}'.format(valueDataRank[indexTicker])
                rowStr = rowStr +','+'{:.2F}'.format(overallRank[indexTicker,1])
                print(rowStr,file=csvfile)
                if flag_plotTopData and indexMarginOfSafetyRank <= numberOfTopCompaniesToPlot:
                    fig = fat.plotBusinessMetrics(fig, axes, ticker, sp.loc[ticker], 
                        dsp.loc[ticker],inc.loc[ticker], bal.loc[ticker],  
                        cf.loc[ticker], df.loc[ticker], metricNames, 
                        fittingType, unitType, scalingType,
                        valueData[indexTicker,indexPrice],
                        valueData[indexTicker,indexValue],
                        valueData[indexTicker,indexMarginOfSafety],                    
                        rows,cols,pageWidth,pageHeight,
                        outputDirectory+'/'+mkt+'/',
                        'marginOfSafety_'+str(indexMarginOfSafetyRank)+'_', True)            
                    for row in range(0,rows):
                        for col in range(0,cols):
                            axes[row,col].cla()
                indexMarginOfSafetyRank=indexMarginOfSafetyRank+1
            
        #small
        with open( outputDirectory+'/'+mkt+'_small'+'.csv','wt',newline='') as csvfile:
            rowStr = 'Ticker,'
            indexMetric=0        
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth'
                indexMetric=indexMetric+1
            indexMetric=0
            rowStr = rowStr+','
            for metric in metricNames:
                if indexMetric > 0:
                    rowStr = rowStr + ','
                rowStr = rowStr + metric.replace(' ','_').replace(',','')+'_Growth_Rank'            
                indexMetric=indexMetric+1
            rowStr = rowStr+',Business_Score,Business_Rank,Price,Value,Price_To_Value,Price_To_Value_Rank,Overall_Rank'
            print(rowStr,file=csvfile)
        
            indexSmall=1            
            for indexTicker in overallDataOrderSorted[:,0]:                
                ticker = cpScreened[indexTicker]
                tickerName = ticker.replace('.','_',1)
                entValue = dsp.loc[ticker][ENTERPRISE_VALUE].values[-1]
                if entValue < smallEnterpriseValue:
                    rowStr = tickerName
                    for j in range(0,mktData.shape[1]):
                        rowStr = rowStr + ',' + '{:.3F}'.format(mktData[indexTicker,j])
                    for j in range(0,mktDataRank.shape[1]):
                        rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRank[indexTicker,j])
                    for j in range(0,mktDataRankOverall.shape[1]):
                        rowStr = rowStr + ',' + '{:.3F}'.format(mktDataRankOverall[indexTicker,j])
                    rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexPrice])
                    rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexValue])
                    rowStr = rowStr +','+'{:.2F}'.format(valueData[indexTicker,indexMarginOfSafety])
                    rowStr = rowStr +','+'{:.2F}'.format(valueDataRank[indexTicker])
                    rowStr = rowStr +','+'{:.2F}'.format(overallRank[indexTicker,1])
                    print(rowStr,file=csvfile)

                    if flag_plotTopData and indexSmall <= numberOfTopCompaniesToPlot:
                        fig = fat.plotBusinessMetrics(fig, axes, ticker, sp.loc[ticker], 
                            dsp.loc[ticker],inc.loc[ticker], bal.loc[ticker],  
                            cf.loc[ticker], df.loc[ticker], metricNames, 
                            fittingType, unitType, scalingType,
                            valueData[indexTicker,indexPrice],
                            valueData[indexTicker,indexValue],
                            valueData[indexTicker,indexMarginOfSafety],
                            rows,cols,pageWidth,pageHeight,
                            outputDirectory+'/'+mkt+'/', 
                            'small_'+str(indexSmall)+'_', True)            
                        for row in range(0,rows):
                            for col in range(0,cols):
                                axes[row,col].cla()
                    indexSmall=indexSmall+1
