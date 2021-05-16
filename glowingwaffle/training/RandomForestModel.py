from sklearn.preprocessing import StandardScaler
from catboost import CatBoostRegressor, Pool
from sklearn.metrics import r2_score, mean_absolute_error

class RandomForestModel:

    def __init__(self):
        # put the class variables here
        self.model = None

    def train_model(self, x_train=None, y_train=None, x_test=None, y_test=None):
        # Train the model with CatBoost Regressor

        regressor = CatBoostRegressor(iterations=500, learning_rate=0.1,
                                      logging_level='Silent', random_seed=0)
        train_pool = Pool(x_train, y_train)
        regressor.fit(train_pool, eval_set=(x_test, y_test))


    def predict_initial_production(self):
        # Pass in the inputs that you want to use to predict IP90/IP180
        x = 1

