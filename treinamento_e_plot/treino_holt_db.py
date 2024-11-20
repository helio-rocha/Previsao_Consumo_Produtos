from database import historico, historico_personalizado
import numpy as np
import itertools
import util.df_util as util
import util.holt as holt

id_produto = 1
alphas = betas = gammas = np.arange(0.01, 1, 0.10)
abg = list(itertools.product(alphas, betas, gammas))

# df_historico = util.df_to_series(historico(id_produto))
df_historico = util.df_to_series(historico_personalizado(id_produto))

df_ajustado = util.ajustar_df(df_historico)

util.plot(df_historico, df_ajustado)

split_index = int(0.8 * len(df_ajustado))

train, test = util.split_test(df_ajustado, split_index)

best_alpha, best_beta, best_gamma, best_mae = holt.tes_optimizer(train, abg, test, 165)
best_alpha, best_beta, best_mae = holt.des_optimizer(train, alphas, betas, test)