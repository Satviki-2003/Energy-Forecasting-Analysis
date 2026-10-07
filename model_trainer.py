import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from utils import create_advanced_features
import pickle

# Reading file
df=pd.read_excel('dataset/PJMW_MW_Hourly.xlsx',parse_dates=['Datetime'])

# sorting data according to timestamps to preserve chronology
df.sort_values(by='Datetime',inplace=True)

# set datetime as index
df.set_index('Datetime',inplace=True)

# dropping duplicate indexes
df=df[~df.index.duplicated()]

# checking for any missing timestamps
full_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq='h')
df = df.reindex(full_range)
# Filling nulls
df.interpolate(method='linear',inplace=True)

df.index.freq='h'

# Define the cutoff point: exactly 365 days before the maximum date in the dataset
test_cutoff = df.index.max() - pd.Timedelta(days=365)

# Split the data chronologically
train = df[df.index <= test_cutoff].copy()
y_train = train['PJMW_MW']

# Taking small portion
y_train_small=y_train.iloc[-2160:]

# Build the advanced matrices
X_train_exog_adv = create_advanced_features(y_train_small.index)

# Fit the model using both the raw target data and the training features
sarimax_with_features = SARIMAX(y_train_small,
                                exog=X_train_exog_adv,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 1, 24)).fit()

# Saving model
with open('model/model.pkl', 'wb') as file:
    pickle.dump(sarimax_with_features, file)