def detect_enso_events(oni_df):
    """
    Detects El Niño and La Niña events within a storm year based on the ONI index.
    An El Niño event is defined as having 5 consecutive months with ONI > 0.5.
    A La Niña event is defined as having 5 consecutive months with ONI < -0.5.

    Parameters:
    oni_df (pd.DataFrame): DataFrame containing the ONI index with a datetime index.

    Returns:
    pd.DataFrame: DataFrame with ENSO mode classification.
    """
    oni_df['ONI Mode'] = 'Neutral'
    oni_df['year_storm'] = oni_df.index.year
    oni_df.loc[oni_df.index.month < 5, 'year_storm'] -= 1
    
    # El Nino: mark a month as El Nino if it's part of any 5-month period where all months exceed 0.5
    el_nino_rolling = (oni_df['ONI'] > 0.5).rolling(window=5, min_periods=5).sum() == 5
    # Expand to mark all months within the 5-month window
    oni_df['El Nino'] = False
    for i in range(len(oni_df)):
        if el_nino_rolling.iloc[i]:
            # Mark current month and previous 4 months
            start_idx = max(0, i - 4)
            oni_df.iloc[start_idx:i+1, oni_df.columns.get_loc('El Nino')] = True
    
    # La Nina: mark a month as La Nina if it's part of any 5-month period where all months are below -0.5
    la_nina_rolling = (oni_df['ONI'] < -0.5).rolling(window=5, min_periods=5).sum() == 5
    # Expand to mark all months within the 5-month window
    oni_df['La Nina'] = False
    for i in range(len(oni_df)):
        if la_nina_rolling.iloc[i]:
            # Mark current month and previous 4 months
            start_idx = max(0, i - 4)
            oni_df.iloc[start_idx:i+1, oni_df.columns.get_loc('La Nina')] = True

    # Set ONI Mode based on results
    oni_df.loc[oni_df['La Nina'] == True, 'ONI Mode'] = 'La Nina'
    oni_df.loc[oni_df['El Nino'] == True, 'ONI Mode'] = 'El Nino'
    
    return oni_df