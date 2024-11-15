from database import historico
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

# def adjust_forecast_index(df_forecast, n_steps, df_real):
#     last_date = df_real.index[-1]
#     forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='min')
#     df_forecast.index = forecast_dates
#     return df_forecast
    
# def forecast_holt(df_holt, n_steps):
#     model = ExponentialSmoothing(endog=df_holt, trend='add').fit()

#     forecasting_hw = model.forecast(steps = n_steps)
    
#     forecasting_hw = adjust_forecast_index(forecasting_hw, n_steps, df_holt)
    
#     return forecasting_hw

def obter_df_historico(id_produto):
    df_historico = historico(id_produto)
    
    df_historico["data"] = pd.to_datetime(df_historico["data"])

    df_historico = pd.Series(df_historico["quant"].values, index=df_historico["data"])
    
    # df_historico = df_historico.tail(100)
    
    return df_historico

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


def tes_optimizer(train, abg, step=342):
    best_alpha, best_beta, best_gamma, best_mae = None, None, None, float("inf")
    cont = 0
    for comb in abg:
        tes_model = ExponentialSmoothing(train, trend="add", seasonal="add", seasonal_periods=12).\
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
    
    print(cont)

    return best_alpha, best_beta, best_gamma, best_mae

id_produto = 1

df_historico = obter_df_historico(id_produto)

df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]

df_ajustado = 500 - df_ajustado

df_ajustado = df_ajustado.resample('MIN')
df_ajustado = df_ajustado.ffill().bfill()
df_ajustado = df_ajustado.interpolate(method='polynomial', order=3)

# plt.figure(figsize=(12, 6))
# plt.plot(df_historico, label="Real")
# plt.plot(df_ajustado, label="Previsão", color="orange")
# plt.title("Previsão usando Holt-Winters")
# plt.legend()
# plt.show()

ts_decompose(df_ajustado, stationary=True)
# 

# print(len(abg))

split_index = int(0.8 * len(df_ajustado))

train = df_ajustado[:split_index]

test = df_ajustado[split_index:]

alphas = betas = gammas = np.arange(0.20, 1, 0.10)

abg = list(itertools.product(alphas, betas, gammas))

# best_alpha, best_beta, best_gamma, best_mae = tes_optimizer(train, abg, len(test))