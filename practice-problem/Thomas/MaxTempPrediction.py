import pandas as pd
pd.set_option('display.max_columns', None)

import numpy as np 

np.set_printoptions(precision=3)

#shows all entries in an array
import sys
np.set_printoptions(threshold=sys.maxsize)

import math

import matplotlib.pyplot as plt
import matplotlib.cm as cm # for adding colors to plots

import seaborn as sns

import datetime as dt

from datetime import datetime

# Plotly
import plotly.graph_objs as go
from plotly.offline import iplot, plot, init_notebook_mode
init_notebook_mode(connected=True)

import plotly.io as pio
pio.renderers.default = "svg"

from IPython.core.display import display, HTML
display(HTML("<style>.container { width:65% !important; }</style>"))

print('libraries loaded')
# read in csv files
df_2019 = pd.read_csv('../calgary_weather_data/en_climate_daily_AB_3031094_2019_P1D.csv')
df_2020 = pd.read_csv('../calgary_weather_data/en_climate_daily_AB_3031094_2020_P1D.csv')
df_2021 = pd.read_csv('../calgary_weather_data/en_climate_daily_AB_3031094_2021_P1D.csv')

print('dfs loaded')

display(df_2019.head())
display(len(df_2019))

display(df_2020.head())
display(len(df_2020))

display(df_2021.head())
display(len(df_2021))


# combine all dfs into one

df = df_2019

df = df.append(df_2020)

df = df.append(df_2021)

df.reset_index(inplace=True)

# confirm new df row count is same as the other 3 dfs

print('New df Row Count:',len(df))
print('New df row counts are correct:', len(df)== (len(df_2021)+len(df_2020)+len(df_2019)))

# quick describe including categorical features

df.describe(include='all')

df.columns

blank_columns = ['Data Quality','Total Rain (mm)','Total Rain Flag', 'Total Snow (cm)', 'Total Snow Flag' ,'Snow on Grnd Flag']

df.drop(labels = blank_columns,axis = 1, inplace= True)

df.groupby(by = 'Dir of Max Gust Flag').count()

df.dtypes

from datetime import date


df['Date/Time'] = pd.to_datetime(arg = df['Date/Time'], format = '%Y-%m-%d')

df['Date/Time'].dtypes

# look for NaNs, missing values, or duplicates

data = df

print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

if data.duplicated().any() == False:
    print("There are no duplicate rows")
else:
    print('There are duplicate rows')
    print(data.duplicated())

### MISSING DATA TABLE
total = data.isnull().sum().sort_values(ascending=False)
percent = (data.isnull().sum() / data.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total_count', 'Percent'])
missing_data

#define missing temp data df

df_miss_temp = df[df['Max Temp (°C)'].isna()]

df_miss_temp

df_miss_temp.describe(include = 'all')

# plot all dates vs temp
import plotly.io as pio
import plotly.express as px

pio.renderers.default = "browser"

data = df

fig = px.line(data, x="Date/Time", y="Max Temp (°C)")
fig.show()

# make df where rows with blank Max Temp is inputted with a large number to see where it's blank

df_max_temp = df.copy()

df_max_temp.loc[np.isnan(df['Max Temp (°C)']), 'Max Temp (°C)'] = 75


data = df_max_temp

fig = px.line(data, x="Date/Time", y="Max Temp (°C)")
fig.show()

last_date = '2021-03-16'

drop_index = df[df['Date/Time'] > last_date].index

df.drop(index=drop_index, inplace= True)

df.reset_index(drop = True, inplace=True)

len(df[df['Date/Time'] > last_date])

# check new blank row counts
data = df

### MISSING DATA TABLE
total = data.isnull().sum().sort_values(ascending=False)
percent = (data.isnull().sum() / data.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total_count', 'Percent'])
missing_data

# deal with blanks by taking average of prev 2 days and next 2 days

import math

for i in range(0, len(df) - 1, 1):

    today_temp = df.loc[i, 'Max Temp (°C)']
    print
    # if temp is blank, take average of previous and next two days
    if math.isnan(today_temp):

        prev_index = i - 2
        next_index = i + 2
        df.loc[i, 'Max Temp (°C)'] = np.nanmean(df.loc[prev_index:next_index, 'Max Temp (°C)'])

    else:
        continue

    # check new blank row counts
data = df['Max Temp (°C)']

### MISSING DATA TABLE
total = data.isnull().sum()
total

for i in range(1, len(df) - 1, 1):
    df.loc[i, 'Prev_Day_Max_Temp'] = df.loc[i - 1, 'Max Temp (°C)']

df[['Max Temp (°C)', 'Prev_Day_Max_Temp']].head(10)

for i in range(0, len(df), 1):
    date = df.loc[i, 'Date/Time']

    df.loc[i, 'day_of_year'] = date.timetuple().tm_yday

df[['Date/Time', 'day_of_year']]

# look for NaNs, missing values, or duplicates

data = df

print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

if data.duplicated().any() == False:
    print("There are no duplicate rows")
else:
    print('There are duplicate rows')
    print(data.duplicated())

### MISSING DATA TABLE
total = data.isnull().sum().sort_values(ascending=False)
percent = (data.isnull().sum() / data.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total_count', 'Percent'])
missing_data

df.columns

# initialize feature dataframe

X_columns = ['Min Temp (°C)', 'Mean Temp (°C)', 'day_of_year', 'Total Precip (mm)', 'Snow on Grnd (cm)',
             'Dir of Max Gust (10s deg)', 'Spd of Max Gust (km/h)', 'Prev_Day_Max_Temp']

X = df.loc[df['Year'] < 2021, X_columns]

# skip first row since it doesn't have any prev_temp data
X = X[1:]

display(X.head())

# initialize target dataframe

y = df.loc[df['Year'] < 2021, 'Max Temp (°C)']

# skip first row
y = y[1:]

display(y.head())

# ensure dataframes are equal length
print()
print('dfs are equal length:', len(X) == len(y))
print()

# check again for missing values

data = X

print('For Feature df')
print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

if data.duplicated().any() == False:
    print("There are no duplicate rows")
else:
    print('There are duplicate rows')
    print(data.duplicated())

### MISSING DATA TABLE
total = data.isnull().sum().sort_values(ascending=False)
percent = (data.isnull().sum() / data.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total_count', 'Percent'])
display(missing_data)

data = y
print('For Target df')
print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

# create test dataframes - ie data from 2021

# initialize feature dataframe

X_columns = ['Min Temp (°C)', 'Mean Temp (°C)', 'day_of_year', 'Total Precip (mm)', 'Snow on Grnd (cm)',
             'Dir of Max Gust (10s deg)', 'Spd of Max Gust (km/h)', 'Prev_Day_Max_Temp']

X_2021 = df.loc[df['Year'] == 2021, X_columns]

display(X_2021.head())

# initialize target dataframe

y_2021 = df.loc[df['Year'] == 2021, 'Max Temp (°C)']

display(y_2021.head())

# ensure dataframes are equal length
print()
print('dfs are equal length:', len(X_2021) == len(y_2021))
print()

# check again for missing values

data = X_2021

print('For Feature df')
print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

if data.duplicated().any() == False:
    print("There are no duplicate rows")
else:
    print('There are duplicate rows')
    print(data.duplicated())

### MISSING DATA TABLE
total = data.isnull().sum().sort_values(ascending=False)
percent = (data.isnull().sum() / data.isnull().count()).sort_values(ascending=False)
missing_data = pd.concat([total, percent], axis=1, keys=['Total_count', 'Percent'])
display(missing_data)

data = y_2021
print('For Target df')
print('There are %i NaNs' % data.isna().sum().sum())
print('There are %i missing values' % data.isnull().sum().sum())

#compute average of data as baseline
temp_average = (y).mean()

#create copy of Feature dataframe
X_2021_test = X_2021.copy()

#add average column to df which represents prediction for each day
X_2021_test['average'] = temp_average

#compute model error
X_2021_test['model_error'] = np.abs(y_2021 - X_2021_test['average'])

print('Baseline Absolute Error :', np.round(X_2021_test['model_error'].mean(),1), 'degrees C')

from catboost import CatBoostRegressor


# set up model, initially tried 100 iterations but found 25 was enough

cboost = CatBoostRegressor(iterations=25,
                          depth = 3,
                          learning_rate = 1,
                          loss_function = 'MAE',
                          )

cboost.fit(X,y, plot =True, eval_set=(X_2021,y_2021))

from sklearn.metrics import mean_absolute_error

# predict 2021 temperatures
y_pred = cboost.predict(X_2021)


print('Best Iteration:', cboost.get_best_iteration())
print('Best Test MAE:', np.round(mean_absolute_error(y_2021,y_pred),2),'degrees C')

# create df to compare real to predicted values
compare_df = pd.DataFrame()

# add date/time
compare_df['Date/Time'] = df.loc[df['Year'] == 2021,'Date/Time']

compare_df['Actual_Max_Temp'] = y_2021

compare_df.reset_index(drop=True, inplace = True)

compare_df['CatBoost_Predictions'] = y_pred

compare_df.head()

# plot all dates vs temp
import plotly.graph_objs as go

fig = go.Figure()

x_line = compare_df['Date/Time']

fig.add_trace(go.Scatter(x= x_line, y=compare_df['CatBoost_Predictions'] ,
                         mode='markers',
                         marker = dict(symbol ='diamond-dot'),
                         name='CatBoost Predictions'))

fig.add_trace(go.Scatter(x= x_line, y = compare_df['Actual_Max_Temp'],
                         mode='lines',
                         name='Recorded Max Temp'))


fig.update_layout(width = 1200,
                  title = "Prediction vs Actual",
                 xaxis_title = "Date/Time",
                 yaxis_title = "Temperature (deg C)")

fig.show()

from catboost import Pool
import shap

cat_pool = Pool(X,label = y)

shap_values = cboost.get_feature_importance(cat_pool,
                                           type ='ShapValues' )

shap_values = shap_values[:,:-1]

shap.summary_plot(shap_values, X)

lfc = cboost.get_feature_importance(cat_pool,
                                           type ='LossFunctionChange' )
lfc_df = pd.DataFrame()

lfc_df['Features'] = X.columns

lfc_df['Feature_Rank'] = lfc


lfc_df.sort_values(by='Feature_Rank', inplace=True)

fig = px.bar(lfc_df, x='Features', y='Feature_Rank')
fig.show()