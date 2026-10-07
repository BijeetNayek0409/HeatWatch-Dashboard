import pandas as pd

def get_city_comparison(df, start_year, end_year):
    """
    Returns city-wise comparison for the selected period.
    """
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    period_df = df[mask]
    
    if period_df.empty:
        return pd.DataFrame()
        
    comp = period_df.groupby('city').agg(
        Average_Max_Temperature=('temperature_2m_max', 'mean'),
        Highest_Temperature=('temperature_2m_max', 'max'),
        Average_Rainfall=('precipitation_sum', 'mean')
    ).reset_index()
    
    comp['Average_Max_Temperature'] = comp['Average_Max_Temperature'].round(2)
    comp['Average_Rainfall'] = comp['Average_Rainfall'].round(2)
    
    # We will compute extreme events in anomaly_detection.py and join them later in the UI if needed
    # For now, just return these aggregates.
    return comp

def get_seasonal_analysis(df, city, start_year, end_year):
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    if city != "All Cities":
        mask = mask & (df['city'] == city)
        
    period_df = df[mask]
    if period_df.empty:
        return pd.DataFrame()
        
    seasonal = period_df.groupby('season').agg(
        Average_Max_Temperature=('temperature_2m_max', 'mean'),
        Average_Min_Temperature=('temperature_2m_min', 'mean'),
        Rainfall=('precipitation_sum', 'mean')
    ).reset_index()
    
    # Order seasons logically
    season_order = {'Summer': 1, 'Monsoon': 2, 'Post-Monsoon': 3, 'Winter': 4}
    seasonal['order'] = seasonal['season'].map(season_order)
    seasonal = seasonal.sort_values('order').drop('order', axis=1)
    
    return seasonal

def get_yearly_trend(df, city, start_year, end_year):
    mask = (df['year'] >= start_year) & (df['year'] <= end_year)
    if city != "All Cities":
        mask = mask & (df['city'] == city)
        
    period_df = df[mask]
    if period_df.empty:
        return pd.DataFrame()
        
    trend = period_df.groupby('year').agg(
        Average_Max_Temperature=('temperature_2m_max', 'mean'),
        Average_Min_Temperature=('temperature_2m_min', 'mean')
    ).reset_index()
    
    return trend

def compare_periods(df, city, hist_start, hist_end, rec_start, rec_end):
    if city != "All Cities":
        df = df[df['city'] == city]
        
    hist_mask = (df['year'] >= hist_start) & (df['year'] <= hist_end)
    rec_mask = (df['year'] >= rec_start) & (df['year'] <= rec_end)
    
    hist_avg = df[hist_mask]['temperature_2m_max'].mean()
    rec_avg = df[rec_mask]['temperature_2m_max'].mean()
    
    if pd.isna(hist_avg) or pd.isna(rec_avg):
        return None, None, None
        
    diff = rec_avg - hist_avg
    return hist_avg, rec_avg, diff
