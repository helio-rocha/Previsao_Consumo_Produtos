from database import historico, historico_estoque
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from datetime import datetime, timedelta
import util.df_util as util
import util.holt as holt

alpha = 0.21
beta = 0.61
# gamma = 0.3

def obter_df_historico(id_produto):
    df_historico = historico(id_produto)
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    return df_historico

def obter_df_estoque(id_produto):
    df_historico = historico_estoque(id_produto)
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    return df_historico

id_produto = 1

n_steps = 30

df_historico = obter_df_historico(id_produto)

df_holt = holt.forecast_holt(df_historico, n_steps, 30)

# df_estoque = obter_df_estoque(id_produto)

# df_cortado = utilcortar_df(df_estoque, 500)

util.plot(df_historico, df_holt)