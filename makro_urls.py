import scraping_helper_functions as shf

import pandas as pd
import requests
import re
from bs4 import *
from datetime import date

from tqdm import tqdm_notebook as tqdm

def define_urls_makrocoza():
    categories = pd.DataFrame(columns=['name', 'link'])
    sub_categories = pd.DataFrame(columns=['category', 'name', 'link'])
    sub_sub_categories = pd.DataFrame(columns=['category', 'sub_category', 'name', 'link'])

    response = requests.get(f"https://www.makro.co.za")
    html = response.text
    soup = BeautifulSoup(html, 'lxml')

    ### product and price
    response = soup.find_all("a", class_='mak-footer-v2__category-name')
    names = [x.text.strip() for x in response]
    links = [x['href'] for x in response]
    categories = pd.DataFrame({'name':names, 'link':links})


    for i in tqdm(range(0, len(categories))):
        response = requests.get(f"https://www.makro.co.za/{categories['link'][i]}")
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        response = soup.find_all("div", class_='col-xs-6 col-sm-3 col-md-2 feature-image-text')

        names = [x.text.strip() for x in response]
        links = [x.a['href'] for x in response]
        tmp = pd.DataFrame({'category':categories['name'][i], 'name':names, 'link':links})
        sub_categories = pd.concat([sub_categories, tmp])

    sub_categories = sub_categories.reset_index(inplace=False).iloc[:, 1:]

    for i in tqdm(range(0, len(sub_categories))):
        response = requests.get(f"https://www.makro.co.za/{sub_categories['link'][i]}")
        html = response.text
        soup = BeautifulSoup(html, 'lxml')

        response = soup.find_all("div", class_='col-xs-6 col-sm-3 col-md-2 feature-image-text')
        names = [x.text.strip() for x in response]
        links = [x.a['href'] for x in response]

        tmp = pd.DataFrame({'category':shf.link_category(sub_categories, sub_categories['link'][i]), 'sub_category':sub_categories['name'][i], 'name':names, 'link':['https://www.makro.co.za' + link for link in links]})
        sub_sub_categories = pd.concat([sub_sub_categories, tmp])


    sub_sub_categories = sub_sub_categories.reset_index(inplace=False).iloc[:, 1:]
    return sub_sub_categories['link']
#scrape_extract(define_urls_makrocoza()).to_csv('C:\\Users\\regan\\OneDrive - 22Seven Digital\\5-scripts\\scraping_output.csv', index=False)

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

            df = pd.DataFrame({'date':date.today(), 'link':link_list, 'price':priceList, 'name':nameList, 'delivery':deliveryAvailability, 'store':storeAvailability}).reset_index(inplace=True)        # print(mdf)
        mdf = pd.concat([df, mdf])
    return mdf


