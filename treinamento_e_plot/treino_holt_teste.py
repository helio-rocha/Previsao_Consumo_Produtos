from concurrent.futures import ProcessPoolExecutor
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from sklearn.metrics import mean_absolute_error
from database import historico, historico_personalizado
import numpy as np
import itertools
import util.df_util as util
import util.holt as holt
import sys

def evaluate_combination(args):
    train, test, comb = args
    step = len(test)
    try:
        tes_model = ExponentialSmoothing(
            train, trend="add", seasonal="add", seasonal_periods=comb[3]
        ).fit(
            smoothing_level=comb[0],
            smoothing_trend=comb[1],
            smoothing_seasonal=comb[2]
        )
        y_pred = tes_model.forecast(step)
        mae = mean_absolute_error(test, y_pred)
    except Exception as e:
        mae = float("inf")
    
    # Print the results and flush to ensure it appears immediately in the terminal
    print([round(comb[0], 2), round(comb[1], 2), round(comb[2], 2), round(comb[3], 2), round(mae, 2)])
    sys.stdout.flush()  # Ensures the output is flushed to the console immediately
    return comb, mae

def tes_optimizer_parallel(train, abg, test):
    best_comb, best_mae = None, float("inf")
    cont = 0

    # Prepare inputs for parallel processing
    inputs = [(train, test, comb) for comb in abg]

    # Use ProcessPoolExecutor for parallel processing
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(evaluate_combination, inputs))

    for comb, mae in results:
        if mae < best_mae:
            best_comb, best_mae = comb, mae
    
    print("Best alpha:", round(best_comb[0], 2), "Best beta:", round(best_comb[1], 2),
          "Best gamma:", round(best_comb[2], 2), "Best periods:", round(best_comb[3], 2),
          "Best MAE:", round(best_mae, 4))
    
    return best_comb[0], best_comb[1], best_comb[2], best_comb[3], best_mae

if __name__ == "__main__":
    id_produto = 1
    alphas = betas = gammas = np.arange(0.01, 1, 0.30)
    periods = np.arange(2, 200, 5)
    abg = list(itertools.product(alphas, betas, gammas, periods))

    df_historico = util.df_to_series(historico_personalizado(id_produto))

    df_ajustado = util.ajustar_df(df_historico)

    split_index = int(0.8 * len(df_ajustado))

    train, test = util.split_test(df_ajustado, split_index)

    best_alpha, best_beta, best_gamma, best_mae = tes_optimizer_parallel(train, abg, test)