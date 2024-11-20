import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def adjust_forecast_index(df_forecast, n_steps, df_real):
    last_date = df_real.index[-1]
    forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='5min')
    df_forecast.index = forecast_dates
    return df_forecast

def ajustar_df(df_historico):
    df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]

    df_ajustado = df_ajustado.resample('5min')
    df_ajustado = df_ajustado.ffill().bfill()
    df_ajustado = df_ajustado.interpolate(method='linear')
    # df_ajustado = df_ajustado.rolling(window=5).mean()
    # df_ajustado = df_ajustado.dropna()
    
    return df_ajustado

def split_test(df, index):
    train = df[:index]
    test = df[index:]
    
    return train, test

def plot(graph1, graph2):
    plt.figure(figsize=(12, 6))
    plt.plot(graph1, label="Real")
    plt.plot(graph2, label="Previsão", color="orange")
    plt.title("Previsão usando Holt-Winters")
    plt.legend()
    plt.show()

def cortar_df(df_historico, intervalo):
    data_final = df_historico.index[-1]
    data_inicial = data_final - timedelta(minutes=5*intervalo)
    data_inicial = pd.to_datetime(data_inicial)
    
    df_cortado = df_historico[df_historico.index >= data_inicial]
    
    return df_cortado

def df_to_series(df_historico):
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    return df_historico