from sklearn.model_selection import train_test_split
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import r2_score, mean_absolute_error
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import StandardScaler
import random

class RandomForestModel:

    def __init__(self, df=None):
        # put the class variables here
        self.modelip90 = None
        self.modelip180 = None
        self.df = df
        self.feature_list = self.df.drop(['IP90', 'IP180', 'Well Authorization Number'], axis=1)
        self.target_listip90 = self.df.filter(['IP90'], axis=1)
        self.target_listip180 = self.df.filter(['IP180'], axis=1)
        self.well_list = self.df.filter(['Well Authorization Number'], axis=1)
        self.x_trainip90 = None
        self.x_testip90 = None
        self.y_trainip90 = None
        self.y_testip90 = None
        self.y_predip90 = None
        self.sc_xip90 = None
        self.sc_yip90 = None
        self.y_trainip180 = None
        self.y_testip180 = None
        self.y_predip180 = None
        self.sc_yip180 = None
        self.sc_xip180 = None
        self.x_trainip180 = None
        self.x_testip180 = None
        self.trainpoolip90 = None
        self.trainpoolip180 = None
           
      
    def split_data(self):
        self.x_trainip90, self.x_testip90, self.y_trainip90, self.y_testip90 = train_test_split(self.feature_list,
                                                            self.target_listip90, test_size = 0.2,
                                                            random_state = 1)

        self.x_trainip180, self.x_testip180, self.y_trainip180, self.y_testip180 = train_test_split(self.feature_list,
                                                                                        self.target_listip180,
                                                                                        test_size=0.2,
                                                                                        random_state=1)

    def train_model(self):
        # Train the model with CatBoost Regressor

        self.sc_xip90 = StandardScaler()
        self.sc_yip90 = StandardScaler()

        self.sc_xip180 = StandardScaler()
        self.sc_yip180 = StandardScaler()

        self.x_trainip90 = self.sc_xip90.fit_transform(self.x_trainip90)
        self.y_trainip90 = self.sc_yip90.fit_transform(self.y_trainip90)

        self.x_trainip180 = self.sc_xip180.fit_transform(self.x_trainip180)
        self.y_trainip180 = self.sc_yip180.fit_transform(self.y_trainip180)

        self.modelip90 = CatBoostRegressor(iterations=1000, learning_rate=0.01,
                                      logging_level='Silent', random_seed=random.randint(0, 2500))
        self.modelip180 = CatBoostRegressor(iterations=1000, learning_rate=0.01,
                                           logging_level='Silent', random_seed=random.randint(0, 2500))
        self.trainpoolip90 = Pool(self.x_trainip90, self.y_trainip90)
        self.modelip90.fit(self.trainpoolip90, eval_set=(self.x_testip90, self.y_testip90))

        self.trainpoolip180 = Pool(self.x_trainip180, self.y_trainip180)
        self.modelip180.fit(self.trainpoolip180, eval_set=(self.x_testip180, self.y_testip180))

    def predict_initial_production(self, xip90, xip180):
        # Pass in the inputs that you want to use to predict IP90/IP180
        y_predip90 = self.sc_yip90.inverse_transform(self.modelip90.predict(self.sc_xip90.transform(xip90)))
        y_predip180 = self.sc_yip180.inverse_transform(self.modelip180.predict(self.sc_xip180.transform(xip180)))

        return y_predip90, y_predip180
   
    def model_statistics(self):
        
        error = mean_absolute_error(self.y_testip90, self.y_predip90)
        print('IP90 Accuracy:', round(error, 2))
        r2 = r2_score(self.y_testip90, self.y_predip90)
        print('IP90 R2:', round(r2, 2))

        # Calculate mean absolute percentage error (MAPE)
        mape = 100 * (abs(self.y_predip90 - self.y_testip90)/ self.y_testip90)
        accuracy = 100 - np.mean(mape)
        print('IP90 Accuracy:', round(accuracy, 2), '%.')

        error = mean_absolute_error(self.y_testip180, self.y_predip180)
        print('IP180 Accuracy:', round(error, 2))
        r2 = r2_score(self.y_testip180, self.y_predip180)
        print('IP180 R2:', round(r2, 2))

        # Calculate mean absolute percentage error (MAPE)
        mape = 100 * (abs(self.y_predip180 - self.y_testip180) / self.y_testip180)
        accuracy = 100 - np.mean(mape)
        print('IP180 Accuracy:', round(accuracy, 2), '%.')

    def feature_importance(self, iternum):
        x_col = self.feature_list.columns
        feature_importances = self.modelip90.get_feature_importance(self.trainpoolip90)
        plot_labels = ['LAT',             'LONG',
                 'CHARGE',          'GEL',
                   'ENERGIZER',              'ENERGIZERT',
              'PROP1',              'PROP2',
              'PROP3',              'PROP4',
                   'FRACT',                   'Energizer',
              'EnergizerT',       'TOP',
      'BASE',              'FRACNUM',
     'CUMFLUID',             'CHARGESIZE',
             'SHOTSPM',           'PHASING',
           'RATE', 'PRESS',
     'FGRADX',                  'PORO',
                  'GPORO',            'Oil water satrtn',
            'SAT',        'NETPAY',
        'PAYGAS',   'TreatPRESS',
      'INJRATE',     'FGRADY',
                 'FLUIDPM',              'TONPM']
        for score, name in sorted(zip(feature_importances, x_col), reverse=True):
            print('{}: {}'.format(name, score))

        #for idx, val in enumerate(feature_importances)
        plt.bar(plot_labels, feature_importances)
        plt.xticks(rotation='vertical')
        plt.savefig('Feature_Importanceip90_iter_{}.png'.format(iternum), dpi=300)
        plt.clf()

        feature_importances = self.modelip180.get_feature_importance(self.trainpoolip180)
        for score, name in sorted(zip(feature_importances, x_col), reverse=True):
            print('{}: {}'.format(name, score))
        plt.bar(plot_labels, feature_importances)
        plt.xticks(rotation='vertical')
        plt.savefig('Feature_Importanceip180_iter_{}.png'.format(iternum), dpi=300)
        plt.clf()






