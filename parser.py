from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import os, requests, json, shutil

HOST = 'https://www.truckscout24.de'

url = 'https://www.truckscout24.de/transporter/gebraucht/kuehl-iso-frischdienst/renault'

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
}

options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument(
    f"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 "
    f"Safari/537.36")
options.add_argument("--window-size=1920,1080")
options.add_argument("--headless")


driver = webdriver.Chrome(options=options)
actions = ActionChains(driver)

def get_pages(url):
    driver.get(url=url)
    source_page = driver.page_source
    soup = BeautifulSoup(source_page, 'lxml')
    pages_count = int(soup.find('ul', class_='sc-pagination').find_all('li')[-2].text)
    pages = []
    for page in range(1, pages_count + 1):
        if '?' not in url:
            r = requests.get(url + f'?currentpage={page}', headers=headers).text
        else:
            r = requests.get(url + f'&currentpage={page}', headers=headers).text
        soup = BeautifulSoup(r, 'lxml')
        href = HOST + soup.find('div', class_='listItem').find('div', class_='ls-titles').find('a').get('href')
        pages.append(href)
    return pages

def get_data(pages):
    try:
        shutil.rmtree('data')
    except Exception as ex:
        # print(ex)
        pass
    try:
        os.mkdir('data')
    except Exception as ex:
        # print(ex)
        pass
    result = {}
    data = []
    for id, page in enumerate(pages):
        id += 1
        print(f"Обрабатываю страницу {id}/{len(pages)}")
        try:
            os.mkdir(f'data/car_{id}')
        except Exception as ex:
            print(ex)
        driver.get(url=page)
        try:
            more = driver.find_element(By.XPATH, '//*[@id="content-container-root"]/div[2]/div[5]/div/div[1]/a[1]')
            actions.move_to_element(more).click(more)
            actions.perform()
            long_desc = True
        except Exception as ex:
            long_desc = False
            # print(ex)
            pass
        source_page = driver.page_source
        soup = BeautifulSoup(source_page, 'lxml')
        try:
            title = soup.find('div', class_='header').find('h1', class_='sc-ellipsis').text
        except:
            title = ""
        try:
            price = soup.find('div', class_='d-price').find('h2').text.rstrip(',-')
        except:
            price = ''
        try:
            mileage = soup.find('div', class_='data-basic1').find_all('div', class_='itemspace')[1].find('div', class_='itemval').text
        except:
            mileage = 0
        try:
            color = soup.find('div', text='Farbe').parent.text.split()[1]
        except:
            color = ''
        try:
            power = soup.find('div', text='Leistung').parent.text.split('Leistung')[1].split('(')[0].strip()
        except:
            power = ''
        if long_desc:
            try:
                desc = soup.find_all('div', class_='sec-wrap')[-1].find('div', class_='short-description').text
            except:
                desc = ''
        else:
            try:
                desc = soup.find_all('div', class_='sec-wrap')[-1].find('div', class_='sc-expandable-box__content').text
            except:
                desc = ''
        try:
            for i, obj in enumerate(soup.find('div', class_='as24-pictures__container').find_all('div', class_='as24-carousel__item')[0:3]):
                img = obj.find('img').get('data-src')
                r = requests.get(img)
                with open(f'data/car_{id}/img_{i}.jpg', 'wb') as file:
                    file.write(r.content)
        except Exception as ex:
            print(ex)

        data.append({
            "id": id,
            "href": page,
            "title": title,
            "price": price,
            "mileage": mileage,
            "color": color,
            "power": power,
            "description": desc,
        })
    result['ads'] = data
    return result

def main():
    try:
        result = get_data(get_pages(url=url))
        with open('data/data.json', 'w', encoding="utf-8") as file:
            json.dump(result, file, indent=4, ensure_ascii=False)
        print("Сборка данных успешно завершена")
    except Exception as ex:
        print('Упс')
        print(ex)

if __name__ == '__main__':
    main()

