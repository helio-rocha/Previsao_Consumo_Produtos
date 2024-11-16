import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta

alpha = 0.01
beta = 0.01
gamma = 0.01

def cortar_df(df_historico, intervalo):
    data_final = df_historico.index[-1]
    data_inicial = data_final - timedelta(minutes=5*intervalo)
    data_inicial = pd.to_datetime(data_inicial)
    df_cortado = df_historico[df_historico.index >= data_inicial]
    return df_cortado

def adjust_forecast_index(df_forecast, n_steps, df_real):
    last_date = df_real.index[-1]
    forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='min')
    df_forecast.index = forecast_dates
    return df_forecast

def forecast_holt(df_holt, n_steps,contagem):
    model = ExponentialSmoothing(df_holt, trend="add",seasonal="add",
                                 seasonal_periods=contagem).fit(smoothing_level=alpha, smoothing_trend=beta,smoothing_seasonal=gamma)

    forecasting_hw = model.forecast(steps = n_steps)

    print(forecasting_hw)
    
    #forecasting_hw = adjust_forecast_index(forecasting_hw, n_steps, df_holt)
    
    return forecasting_hw

n_steps = 30

df_historico = pd.read_csv('treinamento_e_plot\dataset.csv')
crescimento_diff = (df_historico["quant"].diff() > 0).sum()
df_historico["data"] = pd.to_datetime(df_historico["data"])
#print(df_historico)
df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
df_cortado = cortar_df(df_historico, n_steps)


df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]
df_ajustado = df_ajustado.resample('min')
df_ajustado = df_ajustado.ffill().bfill()
df_ajustado = df_ajustado.interpolate(method='polynomial', order=3)

df_holt = forecast_holt(df_ajustado, n_steps,crescimento_diff)

#print(df_holt)

#Plotando os dados

plt.figure(figsize=(12, 6))
plt.plot(df_cortado, label="Real")
plt.plot(df_holt, label="Previsão", color="orange")
plt.title("Previsão usando Holt-Winters")
plt.legend()
plt.show()