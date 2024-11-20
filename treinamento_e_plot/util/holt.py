from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error
import util.df_util as util

def forecast_holt(train, n_steps, periods, type="seasonal"):
    if type == "seasonal": model = ExponentialSmoothing(train, trend="add",seasonal="add",seasonal_periods=periods).fit(optimized=True)
    else: model = ExponentialSmoothing(train, trend="add").fit(optimized=True)

    forecasting_hw = model.forecast(steps = n_steps)
    
    forecasting_hw = util.adjust_forecast_index(forecasting_hw, n_steps, train)
    
    return forecasting_hw

def des_optimizer(train, alphas, betas, test):
    step = len(test)
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

def tes_optimizer(train, abg, test):
    step = len(test)
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