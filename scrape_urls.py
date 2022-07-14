import re
import requests
from bs4 import *
import pandas as pd
from datetime import date
import scraping_helper_functions as shf

def scrape_extract(urls):
    mdf = pd.DataFrame(columns=['date', 'link', 'price', 'name', 'delivery', 'store'])
    for url in urls:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        pattern = '.\d$'
        try:
            lastPage = int(re.search(pattern, soup.find('div', class_='mak-pagination-new').ul.text)[0])
            toggle = True
        except:
            lastPage = 1
            toggle = False

        for i in range(0, lastPage):
            response = shf.paginationResponse(toggle, url, page=i)
            soup = BeautifulSoup(response.text, 'lxml')

            ### product and price
            result = soup.find_all('div', class_='mak-product-tiles-container__product-tile')
            
            
            priceList = ["".join(re.findall('\d', x.find('p', class_='col-xs-12').text)) for x in result]
            nameList = [x.find('a', class_='product-tile-inner__productTitle').span.text for x in result]

            # extract in-store and delivery availability 
            storePattern = 'Store'
            deliveryPattern = 'Delivery'
            availability = [str(x.find_all('span', {'class' : 'fulfillment'})) for x in result]
            storeAvailability = [shf.available(storePattern, x) for x in availability]
            deliveryAvailability = [shf.available(deliveryPattern, x) for x in availability]

            # extract product page link
            link_list = ['www.makro.co.za' + x.find_all('a', class_='product-tile-inner__img', href=True)[0]['href'] for x in result]

            # extract rating
            # rating = [x.find_all('div', class_='bv_text') for x in result]

            df = pd.DataFrame({'date':date.today(), 'link':link_list, 'price':priceList, 'name':nameList, 'delivery':deliveryAvailability, 'store':storeAvailability})        # print(mdf)
        mdf = pd.concat([df, mdf]).reset_index()
    return mdf