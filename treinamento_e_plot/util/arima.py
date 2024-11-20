import pandas as pd
from pmdarima.arima import auto_arima
import util.df_util as util

def train_model(train, tamanho, n_seasons):
    model = auto_arima(y=train, m=n_seasons)

    forecasting = pd.Series(model.predict(n_periods=tamanho))

    forecasting = util.adjust_forecast_index(forecasting, tamanho, train)
    
    return forecasting