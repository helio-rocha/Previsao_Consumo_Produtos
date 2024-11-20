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

id_produto = 1

df_historico = util.df_to_series(historico_personalizado(id_produto))

df_historico = util.ajustar_df(df_historico)

df_historico.to_csv('dataset.csv', index=True)