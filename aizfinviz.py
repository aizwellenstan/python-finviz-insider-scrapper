from user_agent import generate_user_agent
import requests
import urllib3
from lxml import html
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import pandas as pd
import sys

STOCK_URL = "https://finviz.com/quote.ashx"
NEWS_URL = "https://finviz.com/news.ashx"
CRYPTO_URL = "https://finviz.com/crypto_performance.ashx"
STOCK_PAGE = {}

def http_request_get(
    url, session=None, payload=None, parse=True, user_agent=generate_user_agent()
):

  if payload is None:
    payload = {}

  try:
    if session:
      content = session.get(
        url,
        params=payload,
        verify=False,
        headers={"User-Agent": user_agent},
      )
    else:
      content = requests.get(
        url,
        params=payload,
        verify=False,
        headers={"User-Agent": user_agent},
      )

    content.raise_for_status()  # Raise HTTPError for bad requests (4xx or 5xx)
    if parse:
      return html.fromstring(content.text), content.url
    else:
      return content.text, content.url
  except:
    print("time out")

def get_page(ticker):
  global STOCK_PAGE

  if ticker not in STOCK_PAGE:
    STOCK_PAGE[ticker], _ = http_request_get(
        url=STOCK_URL, payload={"t": ticker}, parse=True
    )

def get_insider(ticker):
    try:
        data = []
        get_page(ticker)
        page_parsed = STOCK_PAGE[ticker]
        res = page_parsed.cssselect('table[class="body-table"]')
        if(len(res) > 0):
            table = res[0]
            headers = table[0].xpath("td//text()")
            data = [dict(zip(headers, row.xpath("td//text()"))) for row in table[1:]]
        return data
    except Exception as e:
        print("Error on line {}".format(sys.exc_info()[-1].tb_lineno))
        print(e)

insider = get_insider('AAPL')
df = pd.DataFrame(insider)
df.to_csv('./csv/insider.csv')