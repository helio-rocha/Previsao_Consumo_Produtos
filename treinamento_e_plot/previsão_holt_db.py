from database import historico, historico_estoque, historico_personalizado
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from datetime import datetime, timedelta
import util.df_util as util
import util.holt as holt
import util.arima as arima
import util.decompose as dec
from sklearn.metrics import mean_absolute_error

def transformar_series_para_decrescente(series):
    nova_serie = pd.DataFrame(columns=['quant', 'data'])
    flag = False
    acumulado = 0
    # print(series)
    for i in range(len(series)-3, 0, -1):
        valor = series.iloc[i]
        # print(valor)
        if series.iloc[i] < series.iloc[i+1]:
            acumulado += 500
            flag = True
        if flag == True:
            valor = series.iloc[i] + acumulado
        nova_serie.loc[len(nova_serie)] = {"data": series.index[i], "quant": valor}
        # nova_serie.append(valor)
    nova_serie = util.df_to_series(nova_serie)
    return nova_serie

alpha = 0.21
beta = 0.61
gamma = 0.3

id_produto = 1

# n_steps = 30

df_historico = util.df_to_series(historico_personalizado(id_produto))

# util.plot(df_historico)

df_historico = util.ajustar_df(df_historico)

# print(df_historico.to_string())

# print(sum(df_historico))

df_novo = transformar_series_para_decrescente(df_historico)

df_historico = df_novo.iloc[::-1]
# print(df_historico.to_string())
# util.plot(df_historico, df_novo)

split_index = int(0.95 * len(df_historico))
train, test = util.split_test(df_historico, split_index)

n_steps = len(test)
print(n_steps)

best_mae = float("inf")

# dec.ts_decompose(df_historico)

for period in range(2,100):
    df_holt = holt.forecast_holt(train, n_steps, period)
    mae = mean_absolute_error(test, df_holt)
    if mae < best_mae:
        best_period = period
        best_mae = mae
    print("Period:", period, "mae:", round(mae, 4))

df_holt = holt.forecast_holt(train, n_steps, 80)

df_arima = arima.train_model(train, n_steps, 10)

print("Best Period: ",best_period, "Best MAE: ", best_mae)


# util.plot(df_historico, df_arima)

# df_estoque = obter_df_estoque(id_produto)