# models.py

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

db_url = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DBNAME')}"

# Reflect the existing database schema
engine = create_engine(db_url)
Base = automap_base()
Base.prepare(engine, reflect=True)

# Access the existing tables
InstagramAccount = Base.classes.instagram_account
InstagramOutsourced = Base.classes.instagram_outsourced
SalesRep = Base.classes.sales_rep_salesrep
SalesRepInstagram = Base.classes.sales_rep_salesrep_instagram
DjangoCeleryBeatCrontabSchedule = Base.classes.django_celery_beat_crontabschedule
DjangoCeleryBeatPeriodicTask = Base.classes.django_celery_beat_periodictask
