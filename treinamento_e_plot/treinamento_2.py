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
    
    df_historico.to_csv('dataset.csv', index=True)
    
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



id_produto = 1

df_historico = obter_df_historico(id_produto)

df_ajustado = df_historico[~df_historico.index.duplicated(keep='last')]

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

# ts_decompose(df_ajustado, stationary=True)
# 

# print(len(abg))

split_index = int(0.8 * len(df_ajustado))

train = df_ajustado[:split_index]

test = df_ajustado[split_index:]

alphas = betas = gammas = np.arange(0.01, 1, 0.10)

is_stationary(df_ajustado)

# abg = list(itertools.product(alphas, betas, gammas))

# best_alpha, best_beta, best_mae = des_optimizer(train, alphas, betas, len(test))