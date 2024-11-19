import matplotlib.pyplot as plt
import nnetsauce as ns 
import numpy as np
from sksurv.datasets import load_whas500, load_veterans_lung_cancer, load_gbsg2
from sksurv.custom import SurvivalCustom
from sksurv.tree import SurvivalTree
from sklearn.linear_model import Ridge, MultiTaskElasticNet, RidgeCV, ElasticNetCV, BayesianRidge
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sksurv.linear_model import CoxPHSurvivalAnalysis
from sksurv.metrics import brier_score, integrated_brier_score
from time import time

import pandas as pd

def encode_categorical_columns(df, categorical_columns=None):
    """
    Automatically identifies categorical columns and applies one-hot encoding.

    Parameters:
    - df (pd.DataFrame): The input DataFrame with mixed continuous and categorical variables.
    - categorical_columns (list): Optional list of column names to treat as categorical.

    Returns:
    - pd.DataFrame: A new DataFrame with one-hot encoded categorical columns.
    """
    # Automatically identify categorical columns if not provided
    if categorical_columns is None:
        categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Apply one-hot encoding to the identified categorical columns
    df_encoded = pd.get_dummies(df, columns=categorical_columns)

    # Convert boolean columns to integer (0 and 1)
    bool_columns = df_encoded.select_dtypes(include=['bool']).columns.tolist()
    df_encoded[bool_columns] = df_encoded[bool_columns].astype(int)

    return df_encoded


X, y = load_veterans_lung_cancer()
X = encode_categorical_columns(X)

X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                    test_size=0.1, 
                                                    random_state=42)

estimator = SurvivalCustom(regr=ns.CustomRegressor(BayesianRidge()))
estimator4 = SurvivalCustom(regr=ns.CustomRegressor(GaussianProcessRegressor()))

start = time()
estimator.fit(X_train, y_train)
print("Time to fit BayesianRidge: ", time() - start)
start = time()
estimator4.fit(X_train, y_train)
print("Time to fit GaussianProcessRegressor: ", time() - start)


surv_funcs = estimator.predict_survival_function(X_test.iloc[0:1,:], return_std=True)
surv_funcs4 = estimator4.predict_survival_function(X_test.iloc[0:1,:], return_std=True)

print("\n\n BayesianRidge survival func (mean)", surv_funcs.mean)
print("\n\n BayesianRidge survival func (lower)", surv_funcs.lower)
print("\n\n BayesianRidge survival func (upper)", surv_funcs.upper)

print("\n\n GaussianProcessRegressor survival func (mean)", surv_funcs4.mean)
print("\n\n GaussianProcessRegressor survival func (lower)", surv_funcs4.lower)
print("\n\n GaussianProcessRegressor survival func (upper)", surv_funcs4.upper)