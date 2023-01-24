import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import csv
import json
import os
import time
from random import randrange
import lxml
from selenium import webdriver

# request to page and saving page

urlTemplateBooksPage = "https://www.amazon.com/b?node=283155"

# todo strategy of parse all genres

urlTemplateSingleBook = "https://www.livelib.ru/critique/discussions-retsenzii-kritikov"
# todo link template for many books
templateDomainLivelib = "https://www.livelib.ru"

headers = {
    'Accept': '*/*',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru,en;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Mobile Safari/537.36',
    'sec-ch-ua': '"Chromium";v="106", "Yandex";v="22", "Not;A=Brand";v="99"'
}

def getAllCategories(url):
  
  if not os.path.exists('data-livelib'):
    os.mkdir('data-livelib')

  if(os.path.exists('data-livelib/mainpage.html')):
    print('mainpage.html is already exist, if you want renew data, please delete current file')
  else:
    req = requests.get(urlTemplateSingleBook, headers = headers)
    req.encoding = 'utf-8'
    src = req.text

    with open('data-livelib/mainpage.html', 'w', encoding="utf-8") as file:
      file.write(src)

def procedeCategories():
  with open('data-livelib/mainpage.html', encoding="utf8") as file:
    src = file.read()

  soup = bs(src, 'lxml')

  expertsRedaction = soup.find_all('a', class_='link-black')

  for i in expertsRedaction:
    pageCounter = 1
    nameRedaction = i.text

    if not os.path.exists('data-livelib/redactions'):
      os.mkdir('data-livelib/redactions')

    if(os.path.exists(f'data-livelib/redactions/{nameRedaction}~1.html')):
      print(f'{nameRedaction} is already exist, if you want renew data, please delete files of {nameRedaction}')
      continue
    else:
      while True:
        urlRedaction = templateDomainLivelib + i['href'] + f'~{pageCounter}'

        req = requests.get(urlRedaction, headers = headers)
        req.encoding = 'utf-8'

        time.sleep(randrange(1,3))

        emptyCheck = bs(req.text, 'lxml')
        checky = emptyCheck.find_all('div', class_='with-mpad')
        checkCaptcha = emptyCheck.find_all(id='captcha-show')

        if(checky):
          print('End redaction')
          break
        
        if(checkCaptcha):
          print('Captcha Error, try later')
          break
        
        print(i.text, templateDomainLivelib + i['href'] + f'~{pageCounter}')
        with open(f'data-livelib/redactions/{nameRedaction}~{pageCounter}.html', 'w', encoding="utf-8") as file:
          file.write(req.text)

        pageCounter += 1
        time.sleep(randrange(2,5))

      time.sleep(randrange(15,20))

def collectReviewsData():
  #reviewUrls = []
  reviewData = []

  count = 0
  s = requests.Session()

  for page in os.listdir('data-livelib/redactions'):
      with open(f'data-livelib/redactions/{page}', encoding="utf-8") as file:
        src = file.read()
        soup = bs(src, 'lxml')

      reviewUrl = soup.find_all('h3', class_='lenta-card__title')
      for i in reviewUrl:
        reviewTextData = []
        count += 1
        reviewUrl = templateDomainLivelib + i.find('a').get('href')
        req = s.get(url=reviewUrl, headers=headers)
        req.encoding = 'utf-8'
        soup = bs(req.text, 'lxml')

        print(req)
        print(reviewUrl)

        if(soup.find('div', class_='scifi-review-author') != None):
          reviewBook = soup.find('div', class_='scifi-review-author').find('a').text.strip()
        else:
          reviewBook = soup.find('div', class_='lentaasdasd-card__text').find('a').text.strip()
        
        print(reviewBook)
        reviewText = soup.find('div', class_='lenta-card__text').find_all('p')
        for i in reviewText[1:-1]:
          reviewTextData.append(i.text.strip())

        print(''.join(reviewTextData))

        reviewData.append(
          {
            'book_title': reviewBook,
            'review_text': (''.join(reviewTextData)),
          }
        )
        #print(reviewUrl)
        #reviewUrls.append(templateDomainLivelib + i.find('a').get('href'))
        print(f'--------------------BOOK {count} READY ------------------------------------')
        time.sleep(randrange(1,5))
        if(count % 100 == 0):
          time.sleep(randrange(100,150))
  

  with open("data-livelib/reviewsData.json", "a", encoding="utf-8") as file:
    json.dump(reviewData, file, indent=4, ensure_ascii=False)

  #with open("data-livelib/reviewUrls.json", "w", encoding="utf-8") as file:
    #json.dump(reviewUrls, file, indent=4, ensure_ascii=False)

  print('collect urls is finish,', 'num of results', count)


def main():
  getAllCategories(urlTemplateSingleBook)
  procedeCategories()
  collectReviewsData()

if __name__ == '__main__':
  main()



