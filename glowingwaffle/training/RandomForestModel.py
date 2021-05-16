from sklearn.preprocessing import train_test_split
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np


class RandomForestModel:

    def __init__(self, df=None):
        # put the class variables here
        self.model = None
        self.df = df
        self.feature_list = self.df.drop['IP90', 'IP180'] # placeholder names
        self.target_list = self.df['IP90', 'IP180'] # plaeholder names
        self.well_list = self.df['Well Autorization #']
           
      
    def split_data(self):
        x_train, x_test, y_train, y_test = train_test_split(self.feature_list, 
                                                            self.target_list, test_size = 0.2,
                                                            random_state = 1)

    def train_model(self, x_train=None, y_train=None, x_test=None, y_test=None):
        # Train the model with CatBoost Regressor

        self.model = CatBoostRegressor(iterations=500, learning_rate=0.1,
                                      logging_level='Silent', random_seed=0)
        train_pool = Pool(x_train, y_train)
        self.model.fit(train_pool, eval_set=(x_test, y_test))

    def predict_initial_production(self):
        # Pass in the inputs that you want to use to predict IP90/IP180
        pass
   
    def model_statistics(self, x_test=None, y_test=None, y_pred=None):
        
        # establish baseline error from the y and x test (only checking IP90 for now)
        x_col = x_test.columns
        baseline_pred = x_test[:, x_col.index('IP90')]
        baseline_error = abs(baseline_pred - y_test)
        print('Average baseline error: ', round(np.mean(baseline_error), 2)) 
        
        error = mean_absolute_error(y_test, y_pred)
        print('Accuracy:', round(error, 2))
        r2 = r2_score(y_test, y_pred)
        print('R2:', round(r2, 2))

        # Calculate mean absolute percentage error (MAPE)
        mape = 100 * (abs(y_pred - y_test)/ y_test)
        accuracy = 100 - np.mean(mape)
        print('Accuracy:', round(accuracy, 2), '%.')

    def feature_importance(self, train_pool=None, x_train=None):
        x_col = x_train.columns
        feature_importances = self.model.get_feature_importance(train_pool)
        for score, name in sorted(zip(feature_importances, x_col), reverse=True):
            print('{}: {}'.format(name, score))
        feature_importances.plot(kind='bar');
        plt.savefig('Feature_Importance.png', dpi=300, bbox_inches='tight')





