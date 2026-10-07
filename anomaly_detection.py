import pandas as pd
import numpy as np

def calculate_z_scores(df):
    """
    Calculates the Z-score for maximum temperature based on city and month historical baselines.
    """
    df = df.copy()
    
    # Calculate historical baseline (mean and std) per city per month
    baselines = df.groupby(['city', 'month'])['temperature_2m_max'].agg(['mean', 'std']).reset_index()
    baselines = baselines.rename(columns={'mean': 'historical_mean', 'std': 'historical_std'})
    
    # Merge baselines back to dataframe
    df = df.merge(baselines, on=['city', 'month'], how='left')
    
    # Calculate Z-score
    # Handle cases where std is 0 (e.g., very few records or exact same temps)
    df['historical_std'] = df['historical_std'].replace(0, np.nan)
    df['z_score'] = (df['temperature_2m_max'] - df['historical_mean']) / df['historical_std']
    df['z_score'] = df['z_score'].fillna(0) # fallback
    
    # Absolute Z-score for classification
    df['abs_z_score'] = df['z_score'].abs()
    
    # Classify anomalies
    def classify_status(z):
        if z < 2:
            return 'NORMAL'
        elif 2 <= z < 3:
            return 'UNUSUAL'
        else:
            return 'EXTREME'
            
    df['Status'] = df['abs_z_score'].apply(classify_status)
    df['Deviation'] = df['temperature_2m_max'] - df['historical_mean']
    
    return df

def get_extreme_events_summary(df, start_year, end_year):
    """
    Returns summary statistics for extreme events in the given period.
    """
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    period_df = df[mask]
    
    extreme = period_df[period_df['Status'] == 'EXTREME']
    unusual = period_df[period_df['Status'] == 'UNUSUAL']
    
    total_extreme = len(extreme)
    total_unusual = len(unusual)
    highest_temp = period_df['temperature_2m_max'].max() if not period_df.empty else 0
    max_positive_dev = period_df['Deviation'].max() if not period_df.empty else 0
    
    return total_extreme, total_unusual, highest_temp, max_positive_dev

def get_top_extreme_events(df, start_year, end_year, limit=10):
    """
    Returns the top N most unusual events with a human-readable explanation.
    """
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    period_df = df[mask]
    
    # Filter for unusual or extreme
    anomalies = period_df[period_df['Status'].isin(['UNUSUAL', 'EXTREME'])]
    
    # Sort by absolute z-score
    top_events = anomalies.sort_values(by='abs_z_score', ascending=False).head(limit)
    
    month_names = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
    
    reasons = []
    for _, row in top_events.iterrows():
        dev = row['Deviation']
        month = month_names[row['month']]
        if dev > 0:
            reasons.append(f"{dev:.1f}°C hotter than normal for {month}")
        else:
            reasons.append(f"{abs(dev):.1f}°C colder than normal for {month}")
            
    res = pd.DataFrame({
        'Date': top_events['date'].dt.strftime('%d %b %Y'),
        'City': top_events['city'],
        'Observed Temperature': top_events['temperature_2m_max'].round(1).astype(str) + ' °C',
        'Historical Average': top_events['historical_mean'].round(1).astype(str) + ' °C',
        'Deviation': np.where(top_events['Deviation'] > 0, '+', '') + top_events['Deviation'].round(1).astype(str) + ' °C',
        'Z-Score': top_events['z_score'].round(2),
        'Reason': reasons,
        'Status': top_events['Status']
    })
    
    return res

def calculate_live_z_score(city, current_temp, month, baselines_df):
    """
    Calculates the Z-score for a live observation using historical baselines.
    """
    # baselines_df should be the grouped object from historical data
    # Actually, we can just extract it
    pass
