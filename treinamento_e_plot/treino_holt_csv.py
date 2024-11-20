import numpy as np
import pandas as pd
import itertools
import util.df_util as util
import util.holt as holt

df_historico = pd.read_csv('treinamento_e_plot\dataset.csv')
df_historico = util.df_to_series(df_historico)
df_ajustado = util.ajustar_df(df_historico)

util.plot(df_historico, df_ajustado)

split_index = int(0.8 * len(df_ajustado))
train, test = util.split_test(df_ajustado, split_index)

alphas = betas = gammas = np.arange(0.01, 1, 0.1)

abg = list(itertools.product(alphas, betas, gammas))

best_alpha, best_beta, best_gamma, best_mae = holt.tes_optimizer(train, abg, test)
best_alpha, best_beta, best_mae = holt.des_optimizer(train, alphas, betas, test)