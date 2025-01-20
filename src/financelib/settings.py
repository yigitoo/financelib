from selenium import webdriver
import dotenv, os

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)

NEWS_API_APIKEY = None

def news_api_setup(api_key: str = None, api_key_from_dotenv: bool = True, dotenv_path: str = "") -> None:
  global NEWS_API_APIKEY

  if not api_key and api_key_from_dotenv:

    if dotenv_path == "":
      dotenv.load_dotenv()

    else:
      dotenv.load_dotenv(dotenv_path)

    NEWS_API_APIKEY = os.getenv("NEWS_API_APIKEY")
  else:
    NEWS_API_APIKEY = api_key

# This settings is for my pc. Please set this for your own pc.
if __name__ == "__main__":
  news_api_setup(api_key_from_dotenv=True, dotenv_path='.env.local')
