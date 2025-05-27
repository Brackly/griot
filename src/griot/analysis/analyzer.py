import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy
import numpy as np
from scipy.stats import f_oneway
from sklearn.preprocessing import OneHotEncoder

class DataAnalyzer:
    def __init__(self,
                  df:pd.DataFrame,
                  target_col:str=None,
                  categorical_columns:list=None):

        if categorical_columns:
            for col in categorical_columns:
                df[col] = df[col].astype('category')
            self.data = df
        else:
            self.data = df
        self.data.columns = [col.lower() for col in self.data.columns]
        self.target_col = target_col

    def column_details(self, sort_by='unique_count', ascending=True):
        """
        Generate detailed column summary including data types, unique counts,
        missing values, and memory usage

        Parameters:
        sort_by (str): Column to sort results by ('unique_count' or 'dtype')
        ascending (bool): Sort order

        Returns:
        pd.DataFrame: Summary dataframe sorted by specified column
        """
        # Validate input
        if self.data.empty:
            return pd.DataFrame()

        # Calculate metrics
        details = pd.DataFrame({
            'column': self.data.columns,
            'dtype': self.data.dtypes.astype(str),
            'unique_count': self.data.nunique(),
            'missing_values': self.data.isna().sum(),
            'memory_usage': self.data.memory_usage(deep=False, index=False)
        }).sort_values(by=sort_by, ascending=ascending)

        # Add categorical flag
        details['is_categorical'] = details['unique_count'] < 10
        return details.reset_index(drop=True)

    def quick_summary(self):
        """Generate high-level dataset summary"""
        summary = {
            'Total Samples': len(self.data),
            'Total Features': self.data.shape[1],
            'Missing Values (%)': self.data.isna().sum().sum() / (len(self.data) * self.data.shape[1]) * 100,
            'Duplicate Rows': self.data.duplicated().sum(),
            'Estimated Memory (MB)': self.data.memory_usage(deep=True).sum() / 1024**2
        }
        return pd.DataFrame(summary, index=['Value'])

    def plot_distributions(self, column, bins=30, figsize=(10,6)):
        """Automatically plot appropriate distribution plot"""
        plt.figure(figsize=figsize)

        if pd.api.types.is_numeric_dtype(self.data[column]):
            sns.histplot(self.data[column], kde=True, bins=bins)
            plt.title(f'Distribution of {column}')
        else:
            self.data[column].value_counts().head(20).plot(kind='bar')
            plt.title(f'Top Categories in {column}')

        plt.xticks(rotation=45)
        plt.show()

    def smart_correlation(self, threshold=0.8):
        """Find high correlations with visualization"""
        corr_matrix = self.data.select_dtypes(include=np.number).corr()

        # Plot heatmap
        plt.figure(figsize=(12,8))
        sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='coolwarm')
        plt.title('Correlation Matrix')
        plt.show()

        # Find high correlations
        high_corr = (corr_matrix.abs()
                    .stack()
                    .reset_index()
                    .query('level_0 != level_1')
                    .rename(columns={0: 'correlation'}))

        return high_corr[high_corr['correlation'] > threshold].sort_values('correlation', ascending=False)

    def missing_analysis(self, plot=True):
        """Advanced missing value analysis"""
        missing = self.data.isna().sum()
        missing_pct = missing / len(self.data) * 100

        if plot:
            missing[missing > 0].sort_values().plot(kind='barh', figsize=(10,6))
            plt.title('Missing Values per Column')
            plt.xlabel('Missing Count')
            plt.show()

        return pd.DataFrame({'missing_count': missing, 'missing_percent': missing_pct}) \
                .query('missing_count > 0') \
                .sort_values('missing_percent', ascending=False)

    def categorical_summary(self, threshold=0.5):
        """Analyze categorical columns with rare category detection"""
        cat_cols = self.data.select_dtypes(include=['object', 'category']).columns
        summary = []

        for col in cat_cols:
            value_counts = self.data[col].value_counts(normalize=True)
            n_unique = len(value_counts)
            most_common = value_counts.iloc[0]
            rare_categories = sum(value_counts < threshold/100)

            summary.append({
                'column': col,
                'unique_values': n_unique,
                'most_common': most_common,
                'rare_categories_pct': rare_categories/n_unique*100,
                'entropy': scipy.stats.entropy(value_counts)
            })

        return pd.DataFrame(summary).sort_values('entropy', ascending=False)

    def detect_outliers(self, method='iqr', threshold=1.5):
        """Identify outliers using specified method"""
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        outliers = pd.DataFrame()

        for col in numeric_cols:
            if method == 'iqr':
                Q1 = self.data[col].quantile(0.25)
                Q3 = self.data[col].quantile(0.25)
                IQR = Q3 - Q1
                lower = Q1 - threshold*IQR
                upper = Q3 + threshold*IQR
            elif method == 'zscore':
                z = np.abs(scipy.stats.zscore(self.data[col]))
                outliers[col] = z > threshold

            outliers[col] = ~self.data[col].between(lower, upper)

        return outliers.sum().sort_values(ascending=False)

    def pairwise_relationships(self, target_col, max_cols=5):
        """Analyze relationships with target variable"""
        numeric_cols = self.data.select_dtypes(include=np.number).columns
        corr_with_target = self.data[numeric_cols].corr()[target_col].sort_values(ascending=False)

        top_cols = corr_with_target.index[1:max_cols+1]

        if len(top_cols) > 0:
            sns.pairplot(self.data[[target_col] + list(top_cols)], diag_kind='kde')
            plt.show()

        return corr_with_target

    def advanced_stats(self):
        """Generate comprehensive statistical summary"""
        stats = pd.concat([
            self.data.describe(include='all').T,
            self.data.agg(['skew', 'kurtosis']).T,
            pd.DataFrame({
                'zeros': (self.data == 0).sum(),
                'negative': (self.data < 0).sum(),
                'mode': self.data.mode().iloc[0],
                'mode_freq': self.data.apply(lambda x: x.value_counts().iloc[0])
            })
        ], axis=1)

        return stats.sort_values('skew', key=abs, ascending=False)

    def data_quality_report(self):
        """Generate comprehensive data quality report"""
        report = {
            'Constant Features': [col for col in self.data.columns if self.data[col].nunique() == 1],
            'High Cardinality (>1000)': [col for col in self.data.columns if self.data[col].nunique() > 1000],
            # 'Zero Variance': [col for col in self.data.columns if self.data[col].std() == 0],
            'Potential Duplicates': self.data.duplicated().sum(),
            'Negative Values in Non-Numeric': [col for col in self.data.select_dtypes(exclude=np.number).columns
                                            if (self.data[col].astype(str).str.contains('-')).any()]
        }
        return pd.DataFrame(report.items(), columns=['Check', 'Values'])

    def generate_report(self, output_file='eda_report.html'):
        # """Generate interactive HTML report using pandas profiling"""
        # from pandas_profiling import ProfileReport

        # profile = ProfileReport(self.data, title='EDA Report', explorative=True)
        # profile.to_file(output_file)
        # return f"Report saved to {output_file}"
        pass

    def check_statistical_significance(self,feature_col:str,target_col:str):
        if self.data[feature_col].dtype == "object":
            grouped = self.data.groupby(by=feature_col)[target_col].apply(list).to_dict()
        else:
            grouped = self.data.groupby(by=target_col)[feature_col].apply(list).to_dict()
        return f_oneway(*[group for group in grouped.values() if len(group)>1])

    def get_numerical_corr(self):
        """Get correlation matrix for numerical columns"""
        return self.data[[col for col in self.data if self.data[col].dtype in ('int','float')]].corr()

    def visualize_continuous_var(self,feature_col:str,target_col:str):
        return sns.scatter(self.data, x=feature_col, y=target_col, trendline="ols", title=f"{feature_col} vs {target_col}")

    def visualize_categorical_var(self,feature_col:str,target_col:str):
        return sns.catplot(data=self.data, x=feature_col, y=target_col, kind="box", title=f"{feature_col} vs {target_col}")

    def prepare_dataset(self) -> pd.DataFrame:
        df_clean = self.data.dropna().copy()

        # Step 1: Identify categorical columns with cardinality < 10
        categorical_cols = [
            col for col in df_clean.select_dtypes(include=["object", "category"]).columns
            if df_clean[col].nunique() < 10
        ]

        # Step 2: One-hot encode them
        if categorical_cols:
            encoder = OneHotEncoder(sparse_output=False, drop='first')
            encoded = encoder.fit_transform(df_clean[categorical_cols])
            encoded_df = pd.DataFrame(encoded, columns=encoder.get_feature_names_out(categorical_cols),
                                      index=df_clean.index)

            df_clean = df_clean.drop(columns=categorical_cols)
            df_clean = pd.concat([df_clean, encoded_df], axis=1)

        # Step 3: Drop remaining categorical columns not encoded
        all_categorical_cols = df_clean.select_dtypes(include=["object", "category"]).columns
        df_clean = df_clean.drop(columns=all_categorical_cols)

        return df_clean

