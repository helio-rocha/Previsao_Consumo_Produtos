import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from pmdarima.arima import auto_arima
from datetime import datetime, timedelta
from sklearn.metrics import mean_absolute_error
import statsmodels.api as sm
import itertools

def is_stationary(y):

    # "HO: Non-stationary"
    # "H1: Stationary"

    p_value = sm.tsa.stattools.adfuller(y)[1]
    if p_value < 0.05: 
        print(F"Result: Stationary (H0: non-stationary, p-value: {round(p_value, 3)})")
    else: 
        print(F"Result: Non-Stationary (H0: non-stationary, p-value: {round(p_value, 3)})")


def ts_decompose(y, model="additive", stationary=False):
    result = seasonal_decompose(y, model=model, period=60)
    fig, axes = plt.subplots(4, 1, sharex=True, sharey=False)
    fig.set_figheight(10)
    fig.set_figwidth(15)

    axes[0].set_title("Decomposition for " + model + " model")
    axes[0].plot(y, 'k', label='Original ' + model)
    axes[0].legend(loc='upper left')

    axes[1].plot(result.trend, label='Trend')
    axes[1].legend(loc='upper left')

    axes[2].plot(result.seasonal, 'g', label='Seasonality & Mean: ' + str(round(result.seasonal.mean(), 4)))
    axes[2].legend(loc='upper left')

    axes[3].plot(result.resid, 'r', label='Residuals & Mean: ' + str(round(result.resid.mean(), 4)))
    axes[3].legend(loc='upper left')
    plt.show(block=True)

    if stationary:
        is_stationary(y)


def des_optimizer(train, alphas, betas, step=48):
    best_alpha, best_beta, best_mae = None, None, float("inf")
    for alpha in alphas:
        for beta in betas:
            des_model = ExponentialSmoothing(train, trend="add").fit(smoothing_level=alpha, smoothing_trend=beta)
            y_pred = des_model.forecast(step)
            mae = mean_absolute_error(test, y_pred)
            if mae < best_mae:
                best_alpha, best_beta, best_mae = alpha, beta, mae
            print("alpha:", round(alpha, 2), "beta:", round(beta, 2), "mae:", round(mae, 4))
    print("best_alpha:", round(best_alpha, 2), "best_beta:", round(best_beta, 2), "best_mae:", round(best_mae, 4))
    return best_alpha, best_beta, best_mae

def tes_optimizer(train, abg, step=342, contagem = 1):
    best_alpha, best_beta, best_gamma, best_mae = None, None, None, float("inf")
    cont = 0
    for comb in abg:
        tes_model = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=contagem).\
            fit(smoothing_level=comb[0], smoothing_trend=comb[1], smoothing_seasonal=comb[2])
        y_pred = tes_model.forecast(step)
        try:
            mae = mean_absolute_error(test, y_pred)
        except:
            cont+= 1
            mae = float("inf")
        if mae < best_mae:
            best_alpha, best_beta, best_gamma, best_mae = comb[0], comb[1], comb[2], mae
        print([round(comb[0], 2), round(comb[1], 2), round(comb[2], 2), round(mae, 2)])

    print("best_alpha:", round(best_alpha, 2), "best_beta:", round(best_beta, 2), "best_gamma:", round(best_gamma, 2),
          "best_mae:", round(best_mae, 4))
    

    return best_alpha, best_beta, best_gamma, best_mae

df_historico = pd.read_csv('treinamento_e_plot\dataset.csv')
crescimento_diff = (df_historico["quant"].diff() > 0).sum()
df_historico["data"] = pd.to_datetime(df_historico["data"])
df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])

df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]
print (df_historico)
print ("--------------------------------------------------------")
print (df_ajustado)

# df_ajustado = 500 - df_ajustado

df_ajustado = df_ajustado.resample('min')
df_ajustado = df_ajustado.ffill().bfill()
df_ajustado = df_ajustado.interpolate(method='polynomial', order=3)

# plt.figure(figsize=(12, 6))
# plt.plot(df_historico, label="Real")
# plt.plot(df_ajustado, label="Previsão", color="orange")
# plt.title("Previsão usando Holt-Winters")
# plt.legend()
# plt.show()

#ts_decompose(df_ajustado, stationary=True)
# 

# print(len(abg))

split_index = int(0.8 * len(df_ajustado))

train = df_ajustado[:split_index]

test = df_ajustado[split_index:]

alphas = betas = gammas = np.arange(0.01, 1, 0.1)

is_stationary(df_ajustado)

print(crescimento_diff)
abg = list(itertools.product(alphas, betas, gammas))

best_alpha, best_beta, best_gamma, best_mae = tes_optimizer(train, abg, len(test),crescimento_diff)
#best_alpha, best_beta, best_mae = des_optimizer(train, alphas, betas, len(test))