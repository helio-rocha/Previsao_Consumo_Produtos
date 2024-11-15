from database import historico
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta

alpha = 0.81
beta = 0.61
gamma = 0.2

def adjust_forecast_index(df_forecast, n_steps, df_real):
    last_date = df_real.index[-1]
    forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='min')
    df_forecast.index = forecast_dates
    return df_forecast
    
def forecast_holt(df_holt, n_steps):
    # model = ExponentialSmoothing(endog=df_holt, trend='add').fit()
    # model = ExponentialSmoothing(df_holt, trend="add", seasonal="add", seasonal_periods=3).\
    #     fit(smoothing_level=alpha, smoothing_slope=beta, smoothing_seasonal=gamma)
    model = ExponentialSmoothing(df_holt, trend="add").fit(smoothing_level=alpha, smoothing_slope=beta)

    forecasting_hw = model.forecast(steps = n_steps)
    
    forecasting_hw = adjust_forecast_index(forecasting_hw, n_steps, df_holt)
    
    return forecasting_hw
    
def forecast_arima(df_arima, n_steps):
    model = auto_arima(y=df_arima, m=12)

    forecasting_arima = pd.Series(model.predict(n_periods=n_steps))

    forecasting_arima = adjust_forecast_index(forecasting_arima, n_steps, df_arima)
    
    return forecasting_arima

def cortar_df(df_historico, intervalo):
    data_final = df_historico.index[-1]
    data_inicial = data_final - timedelta(minutes=5*intervalo)
    data_inicial = pd.to_datetime(data_inicial)
    
    df_cortado = df_historico[df_historico.index >= data_inicial]
    
    return df_cortado

def obter_df_historico(id_produto):
    df_historico = historico(id_produto)
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    # df_historico = df_historico.tail(100)
    
    return df_historico

id_produto = 1

n_steps = 30

df_historico = obter_df_historico(id_produto)

# df_historico = df_historico.tail(700)

df_cortado = cortar_df(df_historico, n_steps)

# df_arima = forecast_arima(df_historico, n_steps)

df_holt = forecast_holt(df_historico, n_steps)

print(df_holt)

# Plotando os dados
plt.figure(figsize=(12, 6))
plt.plot(df_cortado, label="Real")
plt.plot(df_holt, label="Previsão", color="orange")
plt.title("Previsão usando Holt-Winters")
plt.legend()
plt.show()