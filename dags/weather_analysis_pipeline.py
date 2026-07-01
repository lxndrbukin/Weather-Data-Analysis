from airflow.decorators import dag, task
import sys
import os
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
)
from ingest_data import main
from datetime import datetime

@dag(
    'weather_analysis',
    start_date=datetime(2026,6,1),
    schedule_interval='@daily',
    catchup=False,
    description=''
)
def weather_analysis_pipeline():
    @task
    def ingest_data():
        main()

    ingest_data()

weather_analysis_pipeline()