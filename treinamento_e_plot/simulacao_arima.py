from database import historico_teste, historico
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# from statsmodels.tsa.holtwinters import ExponentialSmoothing
# from statsmodels.tsa.holtwinters import SimpleExpSmoothing
from datetime import datetime, timedelta
print("TEste")
from pmdarima.arima import auto_arima
print("TEste")


data_limite = '2024-11-01 22:00:00'
# data_limite = datetime.now() + timedelta(minutes=5)
data_limite = pd.to_datetime(data_limite)

df = historico(1)

df["data"] = pd.to_datetime(df["data"])

df = pd.Series(df["quant"].values, index=df["data"])

df_cortado = df[df.index < data_limite]

print(df_cortado)

model = auto_arima(y= df_cortado, m=12)
print(model)
# model = ExponentialSmoothing(endog=df_cortado, trend='mul', seasonal='add', seasonal_periods=12).fit()
# model = SimpleExpSmoothing(df).fit()

n_steps = 600

forecasting_hw = pd.Series(model.predict(n_periods=n_steps))

# forecasting_hw = model.forecast(steps = n_steps)

last_date = df_cortado.index[-1]
forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='min')
forecasting_hw.index = forecast_dates

print(forecast_dates)

espaco = timedelta(minutes=10)

# Plotando os dados
plt.figure(figsize=(12, 6))
plt.plot(df, label="Real")
plt.plot(forecasting_hw, label="Previsão", color="orange")
plt.title("Previsão usando Holt-Winters")
# Ajuste dos limites do eixo X
# start_date = datetime.now() - espaco  # Ajuste as datas de início e fim conforme necessário
start_date = '2024-11-01 21:00:00'
end_date = '2024-11-01 23:00:00'
# end_date = datetime.now() + espaco
plt.xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
plt.legend()
plt.show()
