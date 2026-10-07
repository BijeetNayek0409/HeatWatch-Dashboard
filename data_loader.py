import pandas as pd

def load_historical_data(filepath="weather_data.csv"):
    """
    Loads and cleans the historical weather dataset.
    """
    df = pd.read_csv(filepath)
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Define seasons
    # Summer: Mar-May, Monsoon: Jun-Sep, Post-Monsoon: Oct-Nov, Winter: Dec-Feb
    def get_season(month):
        if month in [3, 4, 5]:
            return "Summer"
        elif month in [6, 7, 8, 9]:
            return "Monsoon"
        elif month in [10, 11]:
            return "Post-Monsoon"
        else:
            return "Winter"
            
    df['season'] = df['month'].apply(get_season)
    
    return df
