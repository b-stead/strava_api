import pandas as pd

df = pd.read_csv('strava_activities_all_fields.csv')

print(df.loc[[0],['upload_id']])