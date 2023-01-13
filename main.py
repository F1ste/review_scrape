import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import csv
import os
import time
import lxml

# request to page and saving page

urlTemplateBooksPage = "https://www.amazon.com/b?node=283155"

# todo strategy of parse all genres
# take refinement item and get all siblings in node list
# we need all refinements? how we can get all genres of book and use it


urlTemplateSingleBook = "https://www.livelib.ru/critique/discussions-retsenzii-kritikov"
# todo link template for many books
urlTemplateExpertsAll = "https://www.livelib.ru"

headers = {
    'Accept': '*/*',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36'
}

def getAllCategories(url):

  req = requests.get(urlTemplateSingleBook, headers = headers)
  req.encoding = 'utf-8'
  src = req.text
  #print(src)
  if not os.path.exists('data-livelib'):
    os.mkdir('data-livelib')

  with open('data-livelib/mainpage.html', 'w', encoding="utf-8") as file:
    file.write(src)

def procedeCategories():
  with open('data-livelib/mainpage.html', encoding="utf8") as file:
    src = file.read()

  soup = bs(src, 'lxml')

  expertsRedaction = soup.find_all('a', class_='link-black')

  for i in expertsRedaction:
    nameRedaction = i.text
    urlRedaction = urlTemplateExpertsAll + i['href']
    print(i.text, urlTemplateExpertsAll + i['href'])

    req = requests.get(urlRedaction, headers = headers)
    req.encoding = 'utf-8'

    if not os.path.exists('data-livelib/redactions'):
      os.mkdir('data-livelib/redactions')

    with open(f'data-livelib/redactions/{nameRedaction}.html', 'w', encoding="utf-8") as file:
      file.write(req.text)

    time.sleep(3)

def main():
  getAllCategories(urlTemplateSingleBook)
  procedeCategories()

if __name__ == '__main__':
  main()

