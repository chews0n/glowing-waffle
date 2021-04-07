# Predicting Max Temp for tomorrow with CatBoost
# Lots of this code is based off of the below TDS article
# https://towardsdatascience.com/random-forest-in-python-24d0893d51c0

# Importing the libraries
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import r2_score, mean_absolute_error
from datetime import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import sys

# Importing the datasets

class weatherData:
    def __init__(self, files):
        self.files = files

    def createModel(self):
        dfs = []

        for filename in self.files:
            dfs.append(pd.read_csv(filename))

        df = pd.concat(dfs, keys=["x", "y", "z"])

        #this is a change
        # Remove any rows where Max Temp = NaN
        # NaN's are removed as making a prediction for
        df = df.dropna(subset = ['Max Temp (°C)'])

        # See stats to ensure that rest of the data set is good
        stat = df.describe()

        # Save Date/Time values for future visualization
        date_19_20 = df['Date/Time'].loc[['x', 'y']]
        date_21 = df['Date/Time'].loc['z']

        # Drop columns that are not part of the feature list
        df = df.drop(columns = ['Date/Time', 'Longitude (x)', 'Latitude (y)', 'Climate ID',
                                'Station Name', 'Data Quality', 'Max Temp Flag',
                                'Min Temp Flag', 'Mean Temp Flag','Heat Deg Days Flag',
                                'Cool Deg Days Flag', 'Total Rain Flag', 'Total Snow Flag',
                                'Total Precip Flag', 'Snow on Grnd Flag','Dir of Max Gust Flag',
                                'Spd of Max Gust Flag', 'Total Rain (mm)', 'Total Snow (cm)',
                                'Heat Deg Days (°C)', 'Cool Deg Days (°C)'], axis = 1)

        # Create new column with max Temp from teh previous day
        # If day is missing, we use the next available day
        df['Max Temp Prev (°C)'] = df['Max Temp (°C)'].shift(periods = 1)

        # List of columns for reference
        col = df.columns

        # Separate out the 2019, 2020 (train) and 2021 data (test)
        df_train = df.loc[['x', 'y']]
        df_test = df.loc[['z']]

        # Create a y and x for train_pool. Will not use for splitting into test/train
        y = np.array(df[['Max Temp (°C)']])
        x = np.array(df.drop(['Max Temp (°C)'], axis = 1))

        # Split the dataset into features(x) and target(y)
        # Do not need to use scikit learn as we have a predetermined test and train set
        y_test = np.array(df_test['Max Temp (°C)'])
        x_test = np.array(df_test.drop(['Max Temp (°C)'], axis = 1))

        y_train = np.array(df_train[['Max Temp (°C)']])
        x_train = np.array(df_train.drop(['Max Temp (°C)'], axis = 1))

        x_col = list(col.drop(['Max Temp (°C)']))
        y_col = list(['Max Temp (°C)'])

        # Establishing Baseline Error to see how well our model performed
        baseline_pred = x_test[:, x_col.index('Mean Temp (°C)')]
        baseline_error = abs(baseline_pred - y_test)
        print('Average baseline error: ', round(np.mean(baseline_error), 2))

        # Feature Scaling

        sc_x = StandardScaler()
        sc_y = StandardScaler()
        x_train = sc_x.fit_transform(x_train)
        y_train = sc_y.fit_transform(y_train)

        # Train the model with CatBoost Regressor

        regressor = CatBoostRegressor(iterations = 500, learning_rate = 0.1,
                                      logging_level = 'Silent', random_seed=0)
        train_pool = Pool(x_train, y_train)
        regressor.fit(train_pool, eval_set=(x_test, y_test))

        # Predict the results
        y_pred = sc_y.inverse_transform(regressor.predict(sc_x.transform(x_test)))

        # Evaluating the Model Performance

        error = mean_absolute_error(y_test, y_pred)
        print('Accuracy:', round(error, 2))
        r2 = r2_score(y_test, y_pred)
        print('R2:', round(r2, 2))

        # Calculate mean absolute percentage error (MAPE)
        mape = 100 * (abs(y_pred - y_test)/ y_test)
        accuracy = 100 - np.mean(mape)
        print('Accuracy:', round(accuracy, 2), '%.')

        # Feature importance
        feature_importances = regressor.get_feature_importance(train_pool)
        for score, name in sorted(zip(feature_importances, x_col), reverse=True):
            print('{}: {}'.format(name, score))

        # Format the dates and combine with the predictions, test variables
        # https://stackoverflow.com/questions/53863600/reduce-number-of-ticks-on-x-axis-where-labels-are-date

        date_21 = [dt.strptime(dstr,'%Y-%m-%d') for dstr in date_21]

        true_data = pd.DataFrame(data = {'date': date_21, 'actual': y_test})
        pred_data = pd.DataFrame(data = {'date': date_21, 'prediction': y_pred})

        return true_data, pred_data

# Visualize the predictions vs the results
def plot_output(true_data, pred_data):
    plt.plot(true_data['date'], true_data['actual'], 'b-', label = 'actual')
    plt.plot(pred_data['date'], pred_data['prediction'], 'ro', label = 'prediction')
    plt.gca().xaxis.set_major_locator(mdates.DayLocator((1,15)))
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.setp(plt.gca().get_xticklabels(), rotation=60, ha="right")
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Maximum Temperature (C)')
    plt.title('Actual and Predicted Values')

    # save the outputted figure
    plt.savefig('plot.png', dpi=300, bbox_inches='tight')

if __name__ == "__main__":

    files = list()
    # process the input csv files
    for i in range(1, len(sys.argv)):
        # i is a number, from 1 to len(inputArgs)-1
        files.append(sys.argv[i])

    weatherModel = weatherData(files)
    true_data, pred_data = weatherModel.createModel()
    plot_output(true_data, pred_data)