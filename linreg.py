import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import clean_data as clean_data

X_array, Y_array = clean_data.create_arrays()


# Fit the regression
model = LinearRegression()
model.fit(X_array, Y_array)
r_sq = model.score(X_array, Y_array)
print(f"coefficient of determination: {r_sq}")
print(f"intercept: {model.intercept_}")
print(f"slope: {model.coef_}")