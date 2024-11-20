import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta
import util.df_util as util
import util.holt as holt

alpha = 0.71
beta = 0.41
# gamma = 0.6

def obter_df_historico():
    df_historico = pd.read_csv('treinamento_e_plot\dataset.csv')
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    return df_historico

n_steps = 30

df_historico = obter_df_historico()

df_ajustado = util.ajustar_df(df_historico)

split_index = int(len(df_ajustado)-n_steps)
train, teste = util.split_test(df_ajustado, split_index)

df_cortado = util.cortar_df(df_ajustado, n_steps)

df_holt = holt.forecast_holt(train, n_steps, 60)

util.plot(df_cortado, df_holt)