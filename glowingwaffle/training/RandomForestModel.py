from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler

class RandomForestModel:

    def __init__(self, df=None):
        # put the class variables here
        self.model = None
        self.df = df
        self.feature_list = self.df.drop(['IP90', 'IP180', 'Well Authorization Number'], axis=1)
        self.target_list = self.df.filter(['IP90', 'IP180'], axis=1)
        self.well_list = self.df.filter(['Well Authorization Number'], axis=1)
        self.x_train = None
        self.x_test = None
        self.y_train = None
        self.y_test = None
        self.y_pred = None
        self.sc_x = None
        self.sc_y = None
           
      
    def split_data(self):
        self.x_train, self.x_test, self.y_train, self.y_test = train_test_split(self.feature_list,
                                                            self.target_list, test_size = 0.2,
                                                            random_state = 1)

    def train_model(self):
        # Train the model with CatBoost Regressor

        self.sc_x = StandardScaler()
        self.sc_y = StandardScaler()

        self.model = CatBoostRegressor(iterations=500, learning_rate=0.1,
                                      logging_level='Silent', random_seed=0)
        train_pool = Pool(self.x_train, self.y_train)
        self.model.fit(train_pool, eval_set=(self.x_test, self.y_test))

    def predict_initial_production(self):
        # Pass in the inputs that you want to use to predict IP90/IP180
        self.y_pred = self.sc_y.inverse_transform(self.model.predict(self.sc_x.transform(self.x_test)))
   
    def model_statistics(self):
        
        # establish baseline error from the y and x test (only checking IP90 for now)
        x_col = self.x_test.columns
        baseline_pred = self.x_test[:, x_col.index('IP90')]
        baseline_error = abs(baseline_pred - self.y_test)
        print('Average baseline error: ', round(np.mean(baseline_error), 2)) 
        
        error = mean_absolute_error(self.y_test, self.y_pred)
        print('Accuracy:', round(error, 2))
        r2 = r2_score(self.y_test, self.y_pred)
        print('R2:', round(r2, 2))

        # Calculate mean absolute percentage error (MAPE)
        mape = 100 * (abs(self.y_pred - self.y_test)/ self.y_test)
        accuracy = 100 - np.mean(mape)
        print('Accuracy:', round(accuracy, 2), '%.')

    def feature_importance(self, train_pool=None):
        x_col = self.x_train.columns
        feature_importances = self.model.get_feature_importance(train_pool)
        for score, name in sorted(zip(feature_importances, x_col), reverse=True):
            print('{}: {}'.format(name, score))
        feature_importances.plot(kind='bar');
        plt.savefig('Feature_Importance.png', dpi=300, bbox_inches='tight')





