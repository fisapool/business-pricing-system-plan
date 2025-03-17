from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import ElasticNet
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import mean_absolute_error

def select_best_model(X_train, y_train, X_val, y_val):
    models = {
        'gradient_boosting': GradientBoostingRegressor(),
        'random_forest': RandomForestRegressor(),
        'elastic_net': ElasticNet(),
        'xgboost': XGBRegressor(),
        'lightgbm': LGBMRegressor()
    }
    
    best_score = float('inf')
    best_model_name = None
    best_model = None
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        predictions = model.predict(X_val)
        mae = mean_absolute_error(y_val, predictions)
        
        if mae < best_score:
            best_score = mae
            best_model_name = name
            best_model = model
    
    print(f"Best model: {best_model_name} with MAE: {best_score}")
    return best_model 