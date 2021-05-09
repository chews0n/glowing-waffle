# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 21:40:43 2021

@author: Pierce
"""
#import required packagaes
import pandas as pd
import numpy as np
import catboost as cb
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

def CleanWeatherData(*args):
    """
    Funcation to Clean and prep weather data
    Will merge data files into one data frame
    Files to be entered in order starting with the oldest
    Parameters
    ----------
    *args : TYPE- String
        File Path to csv with weather data

    Returns
    -------
    df : DataFrame 
        Cleaned dataframe with missing values removed or calculated
        Only Features for training left       
    """
    df = pd.DataFrame()
    for x in args:
        dfloop = pd.read_csv(x)
        df = pd.concat([df,dfloop], ignore_index = True)
    selectedFeatures = [ 'Date/Time', 'Year','Month', 'Day', 'Max Temp (°C)','Min Temp (°C)',
                      'Mean Temp (°C)', 'Total Precip (mm)', 'Snow on Grnd (cm)',
                      'Dir of Max Gust (10s deg)','Spd of Max Gust (km/h)']
    df = df[selectedFeatures]
    df['Date/Time'] = df['Date/Time'].astype('datetime64')
    #fill data with missing data for snow and wind with 0
    FillValues = ['Snow on Grnd (cm)','Dir of Max Gust (10s deg)','Spd of Max Gust (km/h)']
    df[FillValues] = df[FillValues].fillna(0) 
    #Remove rows with missing Max TempData
    df = df.dropna(subset = ['Max Temp (°C)','Min Temp (°C)',
                      'Mean Temp (°C)', 'Total Precip (mm)'])
    #add Max temp of closest previous day in dataset
    df['Prev Max Temp (°C)'] = df['Max Temp (°C)'].shift()
    #remove first day due to not having previous value
    df = df[1:]
    return df

def SplitFeatureTarget(x,y):
    """
    Funtion to split data Features and Target

    Parameters
    ----------
    x : DataFrame
        Cleaned weather data with no missing values
    y : String
        Column name of Target Variable

    Returns
    -------
    Tuple of Numpy Arrarys
    First Arrays being the Features
    Second Array being Target Variable

    """
    TargetArray = np.array(x[y])
    Features = x.drop([y,'Date/Time'], axis = 1)
    FeaturesArray = np.array(Features)
    return (FeaturesArray,TargetArray)

#define file paths for each year
path2019 = '../calgary_weather_data/en_climate_daily_AB_3031094_2019_P1D.csv'
path2020 = '../calgary_weather_data/en_climate_daily_AB_3031094_2020_P1D.csv'
path2021 = '../calgary_weather_data/en_climate_daily_AB_3031094_2021_P1D.csv'

#Create Data Frame for training data
df = CleanWeatherData(path2019,path2020)

#Create Features and Target for Training Data
Features, Target = SplitFeatureTarget(df, 'Max Temp (°C)')

#Split Training and Testing Data of Training Data
Xtrain, Xtest, Ytrain, Ytest = train_test_split(Features, Target, test_size = 0.2)

#Get a baselineMSE by taking estimating the mean of the Max Temp of the training dataset
BaselineMSE = (np.square(Ytest-Ytrain.mean())).mean()

#Create CatBoost Regression Model Based on gridsearch parameters in experiment notebook
model = cb.CatBoostRegressor(depth = 2, iterations=800, learning_rate = 0.3)
model.fit(Xtrain, y = Ytrain)
preds = model.predict(Xtest)

#Calcualte Model MSE 
ModelMSE = (np.square(Ytest-preds)).mean()

#Clean 2021 Data
df2021 = CleanWeatherData(path2021)

#Create Feature and Target Array for 2021 Data
Features2021, Target2021 = SplitFeatureTarget(df2021, 'Max Temp (°C)')

#Apply Model to 2021 Data to calculate prediction
Pred2021 = model.predict(Features2021)

#Calculate MSE for 2021 Prediction
MSE2021 = (np.square(Target2021-Pred2021)).mean()

#Create Plot to show the results of the prediction vs Actuals
Actual2021 = pd.DataFrame(data = {'Date':df2021['Date/Time'],
                                  'Actual Max Temp':Target2021})
DfPred2021 = pd.DataFrame(data = {'Date':df2021['Date/Time'],
                                  'Predicted Max Temp':Pred2021})
plt.plot(Actual2021['Date'],
         Actual2021['Actual Max Temp'],
         'b-',
         label = 'actual')
plt.plot(DfPred2021['Date'],
         DfPred2021['Predicted Max Temp'],
         'ro',
         label = 'prediction')
plt.xticks(rotation = '60');
plt.legend()

plt.xlabel('Date'); plt.ylabel('Max Temp (°C)');
plt.title('Actual and Predicted Values');

#Save Plot in file
plt.savefig('MaxTempPredResults.png')

#print MSE Results
print("This is the MSE if the average Max Temperature was guessed each day:\n",
      BaselineMSE)
print("The model MSE is:\n",ModelMSE)
print("The 2021 Prediction MSE is:\n",MSE2021)