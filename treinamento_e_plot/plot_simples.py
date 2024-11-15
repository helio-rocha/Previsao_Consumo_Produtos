import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Criando uma série temporal de exemplo
np.random.seed(0)
date_range = pd.date_range(start="2022-01-01", periods=100, freq="M")
data = 20 + np.random.randn(100).cumsum()
series = pd.Series(data, index=date_range)

# Ajustando o modelo Holt-Winters (multiplicativo, para uma série com sazonalidade, tendência e nível)
model = ExponentialSmoothing(series, trend="add", seasonal="add", seasonal_periods=12)
fit = model.fit()

# Fazendo a previsão para os próximos 12 meses
forecast = fit.forecast(steps=12)

# Plotando os dados
plt.figure(figsize=(12, 6))
plt.plot(series, label="Real")
plt.plot(forecast, label="Previsão", color="orange")
plt.title("Previsão usando Holt-Winters")
plt.legend()
plt.show()
