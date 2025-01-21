import datetime

def get_today():
  return datetime.datetime.today()

today = get_today()
today_str = today.strftime('%Y-%m-%d')
today_underline = today.strftime('%Y_%m_%d')
