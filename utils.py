import pandas as pd
import holidays

# function to create additional features
def create_advanced_features(data_index):
    features = pd.DataFrame(index=data_index)

    # Detailed Hourly Features 
    features['hr_morning_ramp'] = ((features.index.hour >= 6) & (features.index.hour <= 9)).astype(int)
    features['hr_midday'] = ((features.index.hour >= 10) & (features.index.hour <= 14)).astype(int)
    features['hr_evening_peak'] = ((features.index.hour >= 15) & (features.index.hour <= 22)).astype(int)

    # Weekly Feature
    features['is_weekend'] = (features.index.dayofweek >= 5).astype(int)

    # 3. Seasonal Features 
    features['is_winter'] = features.index.month.isin([12, 1, 2]).astype(int)
    features['is_summer'] = features.index.month.isin([6, 7, 8]).astype(int)
    features['is_autumn'] = features.index.month.isin([9, 10, 11]).astype(int)

    # Holiday Feature
    us_holidays = holidays.US(years=data_index.year.unique())
    features['is_holiday'] = pd.Series(features.index.date, index=features.index).isin(us_holidays).astype(int)

    return features