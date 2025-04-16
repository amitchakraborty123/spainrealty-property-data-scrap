'''
Author: Amit Chakraborty
Project: Spainrealty Website Property  Data Scraper
Profile URL: https://github.com/amitchakraborty123
E-mail: mr.amitc55@gmail.com
'''

import datetime
import time
import pandas as pd
from bs4 import BeautifulSoup
import warnings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os

warnings.filterwarnings("ignore")

def driver_conn():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")      # Make the browser Headless. if you don't want to see the display on chrome just uncomment this
    chrome_options.add_argument("--log-level=3")    # Removes error/warning/info messages displayed on the console
    chrome_options.add_argument("--disable-infobars")  # Disable infobars ""Chrome is being controlled by automated test software"  Although is isn't supported by Chrome anymore
    chrome_options.add_argument("start-maximized")     # Make chrome window full screen
    chrome_options.add_argument('--disable-gpu')       # Disable gmaximizepu (not load pictures fully)
    # chrome_options.add_argument("--incognito")       # If you want to run browser as incognito mode then uncomment it
    chrome_options.add_argument("--disable-notifications")  # Disable notifications
    chrome_options.add_argument("--disable-extensions")     # Will disable developer mode extensions

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)  # you don't have to download chromedriver it will be downloaded by itself and will be saved in cache
    return driver


driver = driver_conn()

# ================================================================================
#                         Get Links
# ================================================================================
def get_url():
    all_link = []
    print('==================== Getting url ====================')
    url = "https://spainrealty.es/en/property-search-on-the-spanish-coast/page/"
    pag = 0
    while True:
        pag += 1
        print(">>>>>>>>>>>>>>>>>>>>>> Page: " + str(pag))
        driver.get(f'{url}{pag}/')
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            lis = soup.find('div', {'class': 'property-items-container'}).find_all('article', {'class': 'property-item'})
        except:
            lis = []
        print("Items here: ", len(lis))
        if len(lis) < 1:
            break
        for li in lis:
            link = ''
            price = ''
            try:
                link = li.find('a')['href']
            except:
                pass
            try:
                tempp = li.find('h5', {'class': 'price'}).text.replace('\n', '')
                temp = str(tempp).split('€')[0]
                tem = str(temp).split(' ')[-1]
                price = str(tem).replace(',', '')
            except:
                pass
            data = {
                'Links': link,
                'Price': price,
            }
            if data not in all_link:
                all_link.append(data)
                df = pd.DataFrame(all_link)
                df = df.rename_axis("Index")
                df.to_csv('url.csv', encoding='utf-8-sig')
        df = pd.DataFrame(all_link)
        df = df.rename_axis("Index")
        df.to_csv('url.csv', encoding='utf-8-sig')


def get_data():
    print('====================== Getting Data ====================')
    df = pd.read_csv('url.csv')
    all_links = df['Links'].values
    prices = df['Price'].values
    cnt = 0
    for i in range(0, len(df)):
        cnt += 1
        print(f'Getting Data {cnt} out of {len(df)}')
        price = prices[i]
        all_link = all_links[i]
        title = ''
        pro_id = ''
        location = ''
        sq_m = ''
        bedrooms = ''
        bathrooms = ''
        garage = ''
        description = ''
        lat = ''
        lang = ''
        type = ''
        linkedin_partner = ''

        driver.get(all_link)
        time.sleep(2)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        try:
            pro_id = soup.find('article', {'class': 'property-item'}).find('h4', {'class': 'title'}).text.replace('Property ID :', '').replace('\n', '').strip()
        except:
            pass
        try:
            title = soup.find('h1', {'class': 'page-title'}).text.replace('\n', '')
        except:
            pass
        try:
            type = soup.find('article', {'class': 'property-item'}).find('h5', {'class': 'price'}).find('small').text.replace('-', '').replace('\n', '').strip()
        except:
            pass
        try:
            location = soup.find('nav', {'class': 'property-breadcrumbs'}).find_all('li')[1].text.replace('\n', '')
        except:
            pass
        try:
            tempp = soup.find('div', {'class': 'property-meta'}).find_all('span')
            for temp in tempp:
                if str('m²') in str(temp):
                    sq_m = temp.text.replace('\n', '').replace(' m²', '')
                if 'Bedrooms' in str(temp):
                    bedrooms = temp.text.replace('\n', '').replace(' Bedrooms', '')
                if 'Bathrooms' in str(temp):
                    bathrooms = temp.text.replace('\n', '').replace(' Bathrooms', '')
                if 'Garage' in str(temp):
                    garage = temp.text.replace('\n', '').replace(' Garage', '')
        except:
            pass
        try:
            description = soup.find('div', {'class': 'wpb_wrapper'}).text.replace('\n', ' ').strip()
        except:
            pass
        try:
            temmp = soup.find('div', {'id': 'property_map'}).find('a', {'title': 'Report errors in the road map or imagery to Google'})['href']
            one = str(temmp).split('https://www.google.com/maps/@')[-1]
            lat = str(one).split(',')[0]
            two = str(one).split('/')[0]
            three = str(two).split('-')[-1]
            lang = str("-") + str(three).split(',')[0]
        except:
            pass
        try:
            linkedin_list = []
            temp_3 = soup.find('ul', {'class': 'slides'}).find_all('li')
            n = 0
            for dd in temp_3:
                n += 1
                lll = dd.find('a')['href']
                data_1 = str(f'<image id="') + str(n) + str('">') + lll + str('</image>')
                linkedin_list.append(data_1)
            linkedin_partner = ('\n'.join(linkedin_list))
        except:
            pass

        data = {
            'link': all_link,
            'title': title,
            'pro_id': pro_id,
            'price': price,
            'type': type,
            'Location': location,
            'sq_m': sq_m.replace(' m²', ''),
            'bedrooms': bedrooms.replace(' Bedrooms', ''),
            'bathroom': bathrooms.replace(' Bathrooms', ''),
            'garage': garage.replace(' Garage', '').replace(' Garages', '').replace('s', ''),
            'description': description,
            'lat': lat,
            'lang': lang,
            'image': linkedin_partner,

        }
        df = pd.DataFrame([data])
        df.to_csv('Kitbate.csv', mode='a', header=not os.path.exists('Kitbate.csv'), encoding='utf-8-sig', index=False)

if __name__ == '__main__':
    get_url()
    get_data()