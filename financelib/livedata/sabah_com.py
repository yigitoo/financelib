# Created: 2025-03-16 15:37:42
# -*- coding: utf-8 -*-
"""
@title: sabah_com.py
@author: Yiğit GÜMÜŞ
@date: 2025-03-16 15:37:42
Description: Sabah.com.tr web sitesinden canlı borsa verilerini çeker.
"""
import requests

def get_live_stock_market_data() -> dict:
  #TODO: IMPLEMENT THIS FUNCTION (IN DEVELOPMENT)
  url: str = 'https://www.sabah.com.tr/json/canli-borsa-verileri'
  response: requests.Response = requests.get(url)
  fetched_data: str = response.text


  fetched_data = fetched_data.split("\"")
  fetched_data = str(fetched_data[3:-1])
  fetched_data = fetched_data.capitalize()
  print(fetched_data)

def get_stock_symbol_list() -> list:
  url: str = 'https://www.sabah.com.tr/json/hissesearch'
  response: requests.Response = requests.get(url)
  fetched_data: str = response.text

  print(fetched_data)
  return fetched_data

if __name__ == '__main__':
  get_live_stock_market_data()
