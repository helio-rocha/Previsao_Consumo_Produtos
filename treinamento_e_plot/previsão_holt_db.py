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

alpha = 0.21
beta = 0.61
gamma = 0.3

id_produto = 1

n_steps = 30

df_historico = util.df_to_series(historico_personalizado(id_produto))

util.plot(df_historico)

df_historico = util.ajustar_df(df_historico)

df_holt = holt.forecast_holt(df_historico, n_steps, 165)

util.plot(df_historico, df_holt)


# df_estoque = obter_df_estoque(id_produto)
