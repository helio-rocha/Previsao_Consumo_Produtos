from database import historico_teste, historico
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.holtwinters import SimpleExpSmoothing


df = historico(1)

df["data"] = pd.to_datetime(df["data"])

df = pd.Series(df["quant"].values, index=df["data"])

model = ExponentialSmoothing(endog=df, trend='add', seasonal='mul', seasonal_periods=12).fit()
# model = SimpleExpSmoothing(df).fit()

n_steps = 200

forecasting_hw = model.forecast(steps = n_steps)

last_date = df.index[-1]
forecast_dates = pd.date_range(start=last_date, periods=n_steps, freq='S')
forecasting_hw.index = forecast_dates

print(df)
print(forecasting_hw)

# Plotando os dados
plt.figure(figsize=(12, 6))
plt.plot(df, label="Real")
plt.plot(forecasting_hw, label="Previsão", color="orange")
plt.title("Previsão usando Holt-Winters")
# Ajuste dos limites do eixo X
start_date = '2024-10-31 21:58:00'  # Ajuste as datas de início e fim conforme necessário
end_date = '2024-10-31 22:07:30'
plt.xlim(pd.to_datetime(start_date), pd.to_datetime(end_date))
plt.legend()
plt.show()
