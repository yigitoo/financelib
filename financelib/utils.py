import datetime

def get_today():
  return datetime.datetime.today()

today = get_today()
today_str = today.strftime('%Y-%m-%d')
today_str_underline = today.strftime('%Y_%m_%d')
today_str_slash = today.strftime('%Y/%m/%d')
today_str_slash_dmy = today.strftime('%d/%m/%Y')
today_str_dmy = today.strftime('%d-%m-%Y')

yesterday = today - datetime.timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')
yesterday_str_underline = yesterday.strftime('%Y_%m_%d')
yesterday_str_slash = yesterday.strftime('%Y/%m/%d')
yesterday_str_slash_dmy = yesterday.strftime('%d/%m/%Y')
