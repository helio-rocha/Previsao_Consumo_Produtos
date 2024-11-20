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
from sklearn.metrics import mean_absolute_error

alpha = 0.21
beta = 0.61
gamma = 0.3

id_produto = 1

# n_steps = 30

df_historico = util.df_to_series(historico_personalizado(id_produto))

# util.plot(df_historico)

df_historico = util.ajustar_df(df_historico)

split_index = int(0.95 * len(df_historico))
train, test = util.split_test(df_historico, split_index)

n_steps = len(test)
print(n_steps)

best_mae = float("inf")

for period in range(2,100):
    df_holt = holt.forecast_holt(train, n_steps, period)
    mae = mean_absolute_error(test, df_holt)
    if mae < best_mae:
        best_period = period
        best_mae = mae
    print("Period:", period, "mae:", round(mae, 4))

df_holt = holt.forecast_holt(train, n_steps, best_period)

print("Best Period: ",best_period, "Best MAE: ", best_mae)
util.plot(df_historico, df_holt)

# df_estoque = obter_df_estoque(id_produto)
