# importing pre-requisite packages
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from flask import Flask
from flask import render_template, request, url_for, redirect
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/search/<search_term>')
def search(search_term):
    plus_separator = search_term.replace(' ', '+')
    amazon_url = 'https://www.amazon.in/s?k=' + plus_separator + '&ref=nb_sb_noss_2'
    myntra_search_term = search_term.replace(' ', '-')
    myntra_url = 'https://www.myntra.com/' + myntra_search_term
    flipkart_url = 'https://www.flipkart.com/search?q=' + plus_separator
    snapdeal_url = 'https://www.snapdeal.com/search?keyword=' + plus_separator
    url =  '['+'{ "amazon": "'+amazon_url+'"},'+'{ "myntra": "'+myntra_url+'"},'+'{ "flipkart": "'+flipkart_url+'"},'+'{ "snapdeal": "'+snapdeal_url+'"}'+']'
    return url

@app.route('/myntra/<search_input>/<option>')
@app.route('/myntra/<search_input>')
def myntra_web_scrapper(search_input,option="default"):
    # Starting up the Web Driver (in our case firefox)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="./dependencies/geckodriver")

    search_term = search_input.replace(' ', '-')
    url = 'https://www.myntra.com/' + search_term
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    records = []

    results = soup.findAll('li', 'product-base')
    for item in results:
        description = str(item.find('h3', 'product-brand').text) + ' - ' + str(item.find('h4', 'product-product').text)
        url = 'https://www.myntra.com/' + item.find('a')['href']
        try:
            product_img = item.find('img')['src']
        except TypeError:
            product_img = '../static/image_not_found.png'
        try:
            price = int(re.findall(r'[\d]+', str(item.find('span', 'product-discountedPrice')))[2])
        except IndexError:
            continue
        result = {'source': 'Myntra','product_image': product_img, 'description': description, 'price': price, 'product_url': url}
        if result:
            records.append(result)
    driver.close()
    
    if records:
        if option == 'default':
            df = pd.DataFrame(data=records)
            #result = df.head(10).to_html(escape=False, index=False)
            result = df.head(10).to_json(orient='records')
        elif option == 'dataframe':
            df = pd.DataFrame(data=records)
            result = df.head(10)
        elif option == 'price-desc':
            df = pd.DataFrame(data=records)
            df['Product url'] = df['Product url'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=False).to_html(escape=False, index=False)
        elif option == 'price-asc':
            df = pd.DataFrame(data=records)
            df['Product url'] = df['Product url'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=True).to_html(escape=False, index=False)
        else:
            result='Wrong Parameter Passed'
    return result

@app.route('/flipkart/<search_input>/<option>')
@app.route('/flipkart/<search_input>')
def flipkart_web_scrapper(search_input,option="default"):
    # Starting up the Web Driver (in our case firefox)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="./dependencies/geckodriver")

    search_term = search_input.replace(' ', '+')
    url = 'https://www.flipkart.com/search?q=' + search_term

    records = []
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    result = {}
    template = soup.findAll('div', '_13oc-S')
    for item in template:
        try:
            description = item.find('div', '_2WkVRV').text + ' - ' + item.find('a', 'IRpwTa')['title']
        except AttributeError:
            continue
        price = item.find('div', '_30jeq3').text
        price = int(re.sub(r'[^\w]', '', price))
        url = 'https://www.flipkart.com' + item.find('a', 'IRpwTa')['href']
        product_img = item.find('img', '_396cs4')['src']

        result = {'product_image': product_img, 'description': description, 'price': price, 'product_url': url}
        if result:
            records.append(result)
    driver.close()
    if records:
        if option == 'default':
            df = pd.DataFrame(data=records)
            #result = df.head(10).to_html(escape=False, index=False)
            result = df.to_json(orient='records')
        elif option == 'dataframe':
            df = pd.DataFrame(data=records)
            result = df
        elif option == 'price-desc':
            df = pd.DataFrame(data=records)
            df['Product CheckOut URL'] = df['Product CheckOut URL'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=False).to_html(escape=False, index=False)
        elif option == 'price-asc':
            df = pd.DataFrame(data=records)
            df['Product CheckOut URL'] = df['Product CheckOut URL'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=True).to_html(escape=False, index=False)
        else:
            result='Wrong Parameter Passed'
    return result

@app.route('/snapdeal/<search_input>/<option>')
@app.route('/snapdeal/<search_input>')
def snapdeal_web_scrapper(search_input, option="default"):
    # Starting up the Web Driver (in our case firefox)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="./dependencies/geckodriver")

    search_term = search_input.replace(' ', '+')
    template = 'https://www.snapdeal.com/search?keyword=' + search_term

    driver.get(template)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    records = []
    results = soup.findAll('div', 'product-tuple-listing')
    for item in range(0, len(results)):
        try:
            product_desc = results[item].find('p', 'product-title')['title']
        except TypeError:
            continue
        product_price = results[item].find('span', 'product-price').text
        product_price = int(re.sub(r'[^\d]', '', product_price))
        product_link = results[item].find('a', 'dp-widget-link')['href']
        try:
            product_image = results[item].find('img', 'product-image')['src']
        except TypeError:
            continue
        except KeyError:
            continue

        record = {'source': 'Snapdeal','description': product_desc, 'price': product_price, 'product_url': product_link,
                  'product_image': product_image}
        if record:
            records.append(record)

    driver.close()
    if records:
        if option == 'default':
            df = pd.DataFrame(data=records)
            #result = df.to_html(escape=False, index=False)
            result = df.to_json(orient='records')
        elif option == 'dataframe':
            df = pd.DataFrame(data=records)
            result = df
        elif option == 'price-desc':
            df = pd.DataFrame(data=records)
            df['product_image'] = df['product_image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            df['link'] = df['link'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            result = df.sort_values('price',ascending=False).to_html(escape=False, index=False)
        elif option == 'price-asc':
            df = pd.DataFrame(data=records)
            df['product_image'] = df['product_image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            df['link'] = df['link'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            result = df.sort_values('price',ascending=True).to_html(escape=False, index=False)
        else:
            result='Wrong Parameter Passed'
    return result


def extract_amazon_record(item):
    # description and product url
    atag = item.h2.a
    description = atag.text.strip()
    product_url = 'https://www.amazon.in' + atag.get('href')

    try:
        # price
        price_parent = item.find('span', 'a-price')
        price = price_parent.find('span', 'a-offscreen').text
        price = int(re.sub(r'[^\d]', '', price))
    except AttributeError:
        return

    # product image
    try:
        # product_image = item.find('div', 'a-section aok-relative s-image-fixed-height').find('img')['src']
        product_image = item.find('img', 's-image')['src']
    except AttributeError:
        product_image = ''

    result = {'source': 'Amazon','product_image': product_image, 'description': description, 'price': price, 'product_url': product_url}

    return result

@app.route('/amazon/<search_input>/<option>')
@app.route('/amazon/<search_input>')
def amazon_web_scrapper(search_input, option="default"):
    # Starting up the Web Driver (in our case firefox)
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Firefox(options=options, executable_path="./dependencies/geckodriver")

    record = []
    records = []

    search_term = search_input.replace(' ', '+')
    url = 'https://www.amazon.in/s?k=' + search_term + '&ref=nb_sb_noss_2'
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    results = soup.find_all('div', {'data-component-type': 's-search-result'})

    for item in results:
        record = extract_amazon_record(item)
        if record:
            records.append(record)

    driver.close()
    if records:
        if option == 'default':
            df = pd.DataFrame(data=records)
            #result = df.head(10).to_html(escape=False, index=False)
            result = df.to_json(orient='records')
        elif option == 'dataframe':
            df = pd.DataFrame(data=records)
            result = df
        elif option == 'price-desc':
            df = pd.DataFrame(data=records)
            df['Product CheckOut URL'] = df['Product CheckOut URL'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=False).to_html(escape=False, index=False)
        elif option == 'price-asc':
            df = pd.DataFrame(data=records)
            df['Product CheckOut URL'] = df['Product CheckOut URL'].apply(lambda x: '<a href="{0}" target="_blank">Product Link</a>'.format(x))
            df['Product Image'] = df['Product Image'].apply(lambda x: '<img src="{0}" width="132" height="auto">'.format(x))
            result = df.head(10).sort_values('price',ascending=True).to_html(escape=False, index=False)
        else:
            result='Wrong Parameter Passed'
    return result

@app.route('/all/<search_input>/<option>')
@app.route('/all/<search_input>')
def all_web_scrapper(search_input, option="default"):
    amazon_df = amazon_web_scrapper(search_input, "dataframe")
    snapdeal_df = snapdeal_web_scrapper(search_input, "dataframe")
    #flipkart_df = flipkart_web_scrapper(search_input,"dataframe")
    myntra_df = myntra_web_scrapper(search_input, "dataframe")
    frames = [amazon_df, snapdeal_df, myntra_df]
    result = pd.concat(frames)
    result = result.sort_values('price',ascending=True).to_json(orient='records')
    return result

@app.route('/undefined/undefined')
def incorrect_search():
    response =  '[{ "source": "Not Found","product_image":"https://i1.wp.com/www.ecommerce-nation.com/wp-content/uploads/2018/10/404-error.jpg?fit=800%2C600&ssl=1", "description":"You have entered an invalid search request", "price":"NA", "product_url": "#"}]'
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)