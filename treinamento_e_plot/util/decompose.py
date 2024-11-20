import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
import statsmodels.api as sm
from pandas.plotting import autocorrelation_plot
import statsmodels.api as sm
from statsmodels.tsa.seasonal import STL

def is_stationary(y):
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
    
def plot_acf(df):
    sm.graphics.tsa.plot_acf(df)
    plt.show()

def plot_pacf(df):
    sm.graphics.tsa.plot_pacf(df)
    plt.show()

def decompose(df, periods):
    seasonal_decompose(df, 'additive', period=periods).plot()

def stl(df, periods):
    stl = STL(df, period=periods)
    res = stl.fit()
    res.plot()

def autocorrelation(df):
    autocorrelation_plot(df)