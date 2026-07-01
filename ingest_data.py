from dotenv import load_dotenv
from datetime import datetime
import pandas as pd
import os
import requests
import boto3

load_dotenv(override=False)

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

s3 = boto3.client('s3')

def fetch_data():
    req = requests.get(
        'https://api.openweathermap.org/data/2.5/weather',
        params={
            'q': 'London',
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
    )

    response = req.json()
    df_normalized = pd.json_normalize(response)
    print(df_normalized.columns.tolist())
    df_normalized['weather_description'] = df_normalized['weather'].apply(lambda x: x[0]['description'])
    df_normalized['weather_main'] = df_normalized['weather'].apply(lambda x: x[0]['main'])
    df_normalized = df_normalized.drop(columns=['weather'])

    df_normalized.columns = [col.replace('main.', '') for col in df_normalized.columns]
    df_normalized.columns = [col.replace('wind.', 'wind_') for col in df_normalized.columns]
    df_normalized.columns = [col.replace('clouds.', 'clouds_') for col in df_normalized.columns]
    df_normalized.columns = [col.replace('sys.', '') for col in df_normalized.columns]
    df_normalized.columns = [col.replace('coord.', '') for col in df_normalized.columns]
    df_normalized['dt'] = df_normalized['dt'].apply(lambda x: datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))

    return df_normalized

def save_local(df, dt):
    path = f'/tmp/date={dt}/weather_data.csv'
    os.makedirs(f'/tmp/date={dt}', exist_ok=True)
    df.to_csv(path, index=False)
    return path

def upload_to_s3(local_path, bucket, key):
    s3.upload_file(local_path, bucket, key)

def main():
    df = fetch_data()
    dt = datetime.today().strftime('%Y-%m-%d')
    path = save_local(df, dt)
    upload_to_s3(
        path,
        'weather-data-analysis-bucket',
        f'landing/date={dt}/weather_data.csv'
    )

def handler(event, context):
    main()

if __name__ == '__main__':
    main()