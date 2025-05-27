import statsmodels.api as sm


class LinearRegression:
    def __init__(self, X, y):
        self.X = sm.add_constant(X)  # Adds a constant term to the predictor
        self.y = y
        self.model = sm.OLS(self.y, self.X)

    def fit(self):
        self.results = self.model.fit()
        return self.results

    def predict(self, X_new):
        X_new = sm.add_constant(X_new)  # Adds a constant term to the new predictor
        return self.results.predict(X_new)