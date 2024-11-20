from database import historico, historico_estoque, historico_personalizado
import util.df_util as util
import util.arima as arima

id_produto = 1
n_seasons = 30

df_historico = util.df_to_series(historico(id_produto))
df_historico_personalizado = util.df_to_series(historico_personalizado(id_produto))
df_ajustado = util.ajustar_df(df_historico)

# split_index = int(0.95 * len(df_ajustado))
split_index = int(len(df_ajustado) - 500)

train, test = util.split_test(df_ajustado, split_index)

# tamanho = len(test)
tamanho = 1000

forecasting = arima.train_model(train, tamanho, n_seasons)

print(train)
print(forecasting)
# print(mean_absolute_error(forecasting, test))

util.plot(df_historico, forecasting)
