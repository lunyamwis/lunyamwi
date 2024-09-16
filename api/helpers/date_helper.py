from datetime import datetime

def datetime_to_cron_expression(dt):
    cron_expression = f"{dt.minute} {dt.hour} {dt.day} {dt.month} *"
    return cron_expression

