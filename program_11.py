#!/bin/env python
# Add your own header comments
#
"""Due April 24, 2020
Created on Tue Apr 21 15:02:38 2020
by Hannah Walcek
Assignment 11 - Presentation Graphics

This program uses two text files WildcatCreek_Discharge_03335000_19540601-20200315.txt
and TippecanoeRiver_Discharge_03331500_19431001-20200315.txt as well as two .csv
files from Assignment 10. It generates figures for daily flow, coefficient of
variation, tqmean, r-b index, average annual monthly flow, and return period of annual
peak flow events.
"""
import pandas as pd
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def ReadData( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    raw data read from that file in a Pandas DataFrame.  The DataFrame index
    should be the year, month and day of the observation.  DataFrame headers
    should be "agency_cd", "site_no", "Date", "Discharge", "Quality". The 
    "Date" column should be used as the DataFrame index. The pandas read_csv
    function will automatically replace missing values with np.NaN, but needs
    help identifying other flags used by the USGS to indicate no data is 
    availabiel.  Function returns the completed DataFrame, and a dictionary 
    designed to contain all missing value counts that is initialized with
    days missing between the first and last date of the file."""
    
    # define column names
    colNames = ['agency_cd', 'site_no', 'Date', 'Discharge', 'Quality']

    # open and read the file
    DataDF = pd.read_csv(fileName, header=1, names=colNames,  
                         delimiter=r"\s+",parse_dates=[2], comment='#',
                         na_values=['Eqp'])
    DataDF = DataDF.set_index('Date')
    
    # remove negative values
    DataDF.loc[~(DataDF['Discharge']>0), 'Discharge'] = np.nan
    
    # quantify the number of missing values
    MissingValues = DataDF["Discharge"].isna().sum()
    
    return( DataDF, MissingValues )
    
def ClipData( DataDF, startDate, endDate ):
    """This function clips the given time series dataframe to a given range 
    of dates. Function returns the clipped dataframe and and the number of 
    missing values."""
    
    # clip data to whatever time span
    DataDF = DataDF.loc[startDate:endDate]
    MissingValues = DataDF["Discharge"].isna().sum()
    return( DataDF, MissingValues )
    
def ReadMetrics( fileName ):
    """This function takes a filename as input, and returns a dataframe with
    the metrics from the assignment on descriptive statistics and 
    environmental metrics.  Works for both annual and monthly metrics. 
    Date column should be used as the index for the new dataframe.  Function 
    returns the completed DataFrame."""
    
    DataDF = pd.read_csv(fileName, header=0, delimiter=',', parse_dates = ['Date'])
    DataDF = DataDF.set_index('Date')    
    
    return( DataDF )


# the following condition checks whether we are running as a script, in which 
# case run the test code, otherwise functions are being imported so do not.
# put the main routines from your code after this conditional check.

if __name__ == '__main__':

    # define full river names as a dictionary so that abbreviations are not used in figures
    riverName = { "Wildcat": "Wildcat Creek",
                  "Tippe": "Tippecanoe River" }
        # define filenames as a dictionary
        
    ##code from lab 10
    # NOTE - you could include more than jsut the filename in a dictionary, 
    #  such as full name of the river or gaging site, units, etc. that would
    #  be used later in the program, like when plotting the data.
    fileName = { "Wildcat": "WildcatCreek_Discharge_03335000_19540601-20200315.txt",
                 "Tippe": "TippecanoeRiver_Discharge_03331500_19431001-20200315.txt" }
    
    # filenames for metrics
    metrics = {"Annual": "Annual_Metrics.csv",
               "Monthly": "Monthly_Metrics.csv"}
    
    # plot colors
    color = {"Wildcat": 'blue',
             "Tippe": 'red'}
    
    # define blank dictionaries (these will use the same keys as fileName)
    DataDF = {}
    MissingValues = {}
     
    #set seaborn to make everything a bit more pretty
    sns.set()
    # process input datasets
    for file in fileName.keys():
        DataDF[file], MissingValues[file] = ReadData(fileName[file])        
        # clip to last 5 years
        DataDF[file], MissingValues[file] = ClipData( DataDF[file], '2014-10-01', '2019-09-30' )
        #plot daily flow  
        plt.plot(DataDF[file]['Discharge'], label=riverName[file], color=color[file], alpha=0.6)
    plt.title('Daily Flow for the Last 5 Years of Record')
    plt.legend(loc=(1.04,0))
    plt.ylabel('Discharge (cfs)')
    plt.xlabel('Time')
    plt.savefig('daily_flow.png', bbox_inches="tight")
    plt.close()
    
    #create annual dataframe
    DataDF['Annual'] = ReadMetrics(metrics['Annual'])
    annual = DataDF['Annual'].groupby('Station')
    
    #annual coefficient of variation
    for name, data in annual:
        plt.scatter(data.index.values, data['Coeff Var'].values, label=riverName[name], color=color[name], marker = 'o', alpha=.6)
    plt.title('Coefficient of Variation for the Last 5 Years of Record')
    plt.legend(loc=(1.04,0))
    plt.ylabel('Coefficient of Variation')
    plt.xlabel('Time')
    plt.savefig('coeff_var.png', bbox_inches = 'tight')
    plt.close()
    
    #annual TQmean
    for name, data in annual:
        plt.scatter(data.index.values, data['Tqmean'].values, label=riverName[name], color=color[name], marker = 'o', alpha=.6)
    plt.title('TQmean for the Last 5 Years of Record')
    plt.legend(loc=(1.04,0))
    plt.ylabel('TQmean')
    plt.xlabel('Time')
    plt.savefig('tqmean.png', bbox_inches = 'tight')
    plt.close()
    
    #annual R-B Index
    for name, data in annual:
        plt.scatter(data.index.values, data['R-B Index'].values, label=riverName[name], color=color[name], marker = 'o', alpha=.6)
    plt.title('R-B Index for the Last 5 Years of Record')
    plt.legend(loc=(1.04,0))
    plt.ylabel('R-B Index')
    plt.xlabel('Time')
    plt.savefig('r-b_index.png', bbox_inches = 'tight')
    plt.close()
        
    #thank you to Avnika for help with the last couple of calculations!
    
    #create monthly dataframe
    DataDF['Monthly'] = ReadMetrics(metrics['Monthly'])
    monthly = DataDF['Monthly'].groupby('Station')
    #annual monthly average values
    for name, data in monthly:
        cols=['Mean Flow']
        m=[3,4,5,6,7,8,9,10,11,0,1,2]
        index=0
        MonthlyAverages=pd.DataFrame(0,index=range(1,13),columns=cols)
        #output
        for i in range(12):
            MonthlyAverages.iloc[index,0]=data['Mean Flow'][m[index]::12].mean()
            index+=1
        #plot values
        plt.plot(MonthlyAverages.index.values, MonthlyAverages['Mean Flow'].values, label=riverName[name], color=color[name], alpha=.6)
    plt.legend(loc=(1.04,0))
    plt.title('Average Annual Monthly Flow')
    plt.ylabel('Discharge (cfs)')
    plt.xlabel('Month')
    plt.savefig('annual_monthly_flow.png', bbox_inches = 'tight')
    plt.close()
    
    #return period of annual peak flow events
    DataDF['Annual'] = DataDF['Annual'].drop(columns=['site_no','Mean Flow','Tqmean','Median Flow','Coeff Var','Skew','R-B Index','7Q','3xMedian'])
    peak = DataDF['Annual'].groupby('Station')
    # Plot return period 
    for name, data in peak:
        #sort in decending
        flow = data.sort_values('Peak Flow', ascending=False)
        # Calculate the rank and reversing the rank to give the largest discharge rank of 1
        ranks1 = stats.rankdata(flow['Peak Flow'], method='average')
        ranks2 = ranks1[::-1]
        #calculate exceedence probability using Weibull plotting position
        weibull = [100*(ranks2[i]/(len(flow)+1)) for i in range(len(flow))]
        # Plot the exceedance probability
        plt.scatter(weibull, flow['Peak Flow'],label=riverName[name], color=color[name], marker='o', alpha=.6)
    plt.legend(loc=(1.04,0))
    plt.title('Return Period of Annual Peak Flow Events')
    plt.ylabel('Peak Discharge (cfs)')
    plt.xlabel('Exceedance Probability (%)')
    plt.savefig('return_period.png', bbox_inches = 'tight')
    plt.close()
    
    
    
      
             
    
 