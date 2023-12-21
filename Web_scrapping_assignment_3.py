#!/usr/bin/env python
# coding: utf-8

# ## 1. Write a python program which searches all the product under a particular product from www.amazon.in. The product to be searched will be taken as input from user. For e.g. If user input is ‘guitar’. Then search for guitars. 

# In[ ]:


get_ipython().system('pip install requests')
get_ipython().system('pip install beautifulsoup4')


# In[ ]:


import requests
from bs4 import BeautifulSoup

def search_amazon_product(product):
    base_url = "https://www.amazon.in"
    search_url = f"{base_url}/s?k={product.replace(' ', '+')}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            product_list = soup.find_all("span", attrs={"class": "a-size-medium a-color-base a-text-normal"})
            
            if product_list:
                print(f"Products related to '{product}' on Amazon India:")
                for product in product_list:
                    print(product.text)
            else:
                print(f"No products found related to '{product}'")
        else:
            print("Failed to fetch data from Amazon. Please try again later.")
    except requests.RequestException as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    user_input = input("Enter the product to search on Amazon India: ")
    search_amazon_product(user_input)


# ## 2. In the above question, now scrape the following details of each product listed in first 3 pages of your search results and save it in a data frame and csv. In case if any product has less than 3 pages in search results then scrape all the products available under that product name. Details to be scraped are: "Brand Name", "Name of the Product", "Price", "Return/Exchange", "Expected Delivery", "Availability" and “Product URL”. In case, if any of the details are missing for any of the product then replace it by “-“. 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_product_details(product):
    base_url = "https://www.amazon.in"
    search_url = f"{base_url}/s?k={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    product_data = []
    page_number = 1

    while True:
        try:
            response = requests.get(search_url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                products = soup.find_all("div", attrs={"data-component-type": "s-search-result"})

                if not products:
                    break

                for prod in products:
                    product_info = {}

                    # Extracting details
                    product_title = prod.find("span", attrs={"class": "a-size-medium a-color-base a-text-normal"})
                    if product_title:
                        product_info['Name of the Product'] = product_title.text.strip()
                    else:
                        product_info['Name of the Product'] = '-'

                    product_brand = prod.find("span", attrs={"class": "a-size-base-plus a-color-base"})
                    if product_brand:
                        product_info['Brand Name'] = product_brand.text.strip()
                    else:
                        product_info['Brand Name'] = '-'

                    product_price = prod.find("span", attrs={"class": "a-price-whole"})
                    if product_price:
                        product_info['Price'] = '₹' + product_price.text.strip()
                    else:
                        product_info['Price'] = '-'

                    product_url = prod.find("a", attrs={"class": "a-link-normal a-text-normal"})
                    if product_url:
                        product_info['Product URL'] = base_url + product_url['href']
                    else:
                        product_info['Product URL'] = '-'

                    # Fetching more details from the product page
                    if product_info['Product URL'] != '-':
                        product_page = requests.get(product_info['Product URL'], headers=headers)
                        if product_page.status_code == 200:
                            page_soup = BeautifulSoup(product_page.content, "html.parser")
                            product_details = page_soup.find_all("div", attrs={"class": "a-section a-spacing-mini"})

                            for detail in product_details:
                                label = detail.find("span", attrs={"class": "a-size-base-plus a-color-base"})
                                value = detail.find("span", attrs={"class": "a-size-base"})
                                if label and value:
                                    product_info[label.text.strip()] = value.text.strip()
                                elif label:
                                    product_info[label.text.strip()] = '-'

                    product_data.append(product_info)

                # Moving to the next page if available
                next_page = soup.find("li", {"class": "a-last"})
                if not next_page or page_number >= 3:
                    break
                page_number += 1
                search_url = base_url + next_page.find('a')['href']
            else:
                print("Failed to fetch data from Amazon. Please try again later.")
                break
        except requests.RequestException as e:
            print(f"Error: {e}")
            break

    return product_data

def create_csv(product_data):
    df = pd.DataFrame(product_data)
    df.to_csv('amazon_products.csv', index=False)
    print("Data saved to 'amazon_products.csv'")

if __name__ == "__main__":
    user_input = input("Enter the product to search on Amazon India: ")
    scraped_data = scrape_product_details(user_input)
    create_csv(scraped_data)


# ## 3. Write a python program to access the search bar and search button on images.google.com and scrape 10 images each for keywords ‘fruits’, ‘cars’ and ‘Machine Learning’, ‘Guitar’, ‘Cakes’. 

# In[ ]:


from selenium import webdriver
import time
import os
import requests
from PIL import Image
from io import BytesIO

# Function to create a directory if it doesn't exist
def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def scrape_images(keywords, num_images=10):
    # Set up Chrome webdriver (provide path to your chromedriver executable)
    driver_path = webdriver.Chrome(ChromeDriverManager().install())
    driver = webdriver.Chrome(driver_path)

    # Maximize the browser window
    driver.maximize_window()

    for keyword in keywords:
        create_directory(keyword)
        url = f"https://www.google.com/search?q={keyword}&tbm=isch"

        driver.get(url)
        time.sleep(2)  # Wait for the page to load

        # Scroll to load more images dynamically
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        # Find and store image URLs
        img_urls = set()
        images = driver.find_elements_by_css_selector("img.Q4LuWd")
        count = 0
        for image in images:
            if count >= num_images:
                break
            try:
                image.click()
                time.sleep(2)
                actual_images = driver.find_elements_by_css_selector('img.n3VNCb')
                for actual_image in actual_images:
                    if actual_image.get_attribute('src') and 'http' in actual_image.get_attribute('src'):
                        img_urls.add(actual_image.get_attribute('src'))
                        count += 1
                        break
            except Exception as e:
                print(f"Error: {e}")

        # Save images
        for i, img_url in enumerate(img_urls):
            try:
                response = requests.get(img_url)
                img = Image.open(BytesIO(response.content))
                img.save(f"{keyword}/image_{i+1}.jpg")
            except Exception as e:
                print(f"Error saving image: {e}")

    # Quit the driver
    driver.quit()

if __name__ == "__main__":
    keywords = ['fruits', 'cars', 'Machine Learning', 'Guitar', 'Cakes']
    scrape_images(keywords, num_images=10)


# ## 4.Write a python program to search for a smartphone(e.g.: Oneplus Nord, pixel 4A, etc.) on www.flipkart.com and scrape following details for all the search results displayed on 1st page. Details to be scraped: “Brand Name”, “Smartphone name”, “Colour”, “RAM”, “Storage(ROM)”, “Primary Camera”, “Secondary Camera”, “Display Size”, “Battery Capacity”, “Price”, “Product URL”. Incase if any of the details is missing then replace it by “- “. Save your results in a dataframe and CSV. 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_smartphones(product):
    base_url = "https://www.flipkart.com"
    search_url = f"{base_url}/search?q={product.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    product_data = []
    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            products = soup.find_all("div", {"class": "_1AtVbE"})

            for product in products:
                product_info = {}

                # Extracting details
                product_title = product.find("div", {"class": "_4rR01T"})
                if product_title:
                    product_info['Smartphone name'] = product_title.text.strip()
                else:
                    product_info['Smartphone name'] = '-'

                product_brand = product.find("div", {"class": "_2WkVRV"})
                if product_brand:
                    product_info['Brand Name'] = product_brand.text.split()[0]
                else:
                    product_info['Brand Name'] = '-'

                product_url = product.find("a", {"class": "_1fQZEK"})
                if product_url:
                    product_info['Product URL'] = base_url + product_url['href']
                else:
                    product_info['Product URL'] = '-'

                product_price = product.find("div", {"class": "_30jeq3 _1_WHN1"})
                if product_price:
                    product_info['Price'] = product_price.text.strip()
                else:
                    product_info['Price'] = '-'

                # Fetching more details from the product page
                if product_info['Product URL'] != '-':
                    product_page = requests.get(product_info['Product URL'], headers=headers)
                    if product_page.status_code == 200:
                        page_soup = BeautifulSoup(product_page.content, "html.parser")
                        specs = page_soup.find_all("li", {"class": "_21lJbe"})

                        for spec in specs:
                            key = spec.find("li", {"class": "_21lJbe"})
                            value = spec.find("li", {"class": "_21lJbe"})
                            if key and value:
                                product_info[key.text.strip()] = value.text.strip()
                            elif key:
                                product_info[key.text.strip()] = '-'

                product_data.append(product_info)

    except requests.RequestException as e:
        print(f"Error: {e}")

    return product_data

def create_csv(product_data):
    df = pd.DataFrame(product_data)
    df.to_csv('flipkart_smartphones.csv', index=False)
    print("Data saved to 'flipkart_smartphones.csv'")

if __name__ == "__main__":
    user_input = input("Enter the smartphone to search on Flipkart: ")
    scraped_data = scrape_smartphones(user_input)
    create_csv(scraped_data)


# ## 5. Write a program to scrap geospatial coordinates (latitude, longitude) of a city searched on google maps. 

# In[ ]:


from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def get_coordinates(city):
    driver = webdriver.Chrome(ChromeDriverManager().install())

    try:
        driver.get("https://www.google.com/maps")
        search_box = driver.find_element_by_css_selector("input.tactile-searchbox-input")
        search_box.send_keys(city)
        search_box.submit()

        # Wait for the map to load
        driver.implicitly_wait(10)

        # Get the current URL after searching for the city
        current_url = driver.current_url

        # Extract latitude and longitude from the URL
        if "/@" in current_url:
            coordinates = current_url.split("/@")[1].split(",")[0:2]
            latitude = coordinates[0]
            longitude = coordinates[1]
            print(f"Geospatial Coordinates for {city}: Latitude - {latitude}, Longitude - {longitude}")
        else:
            print("Coordinates not found.")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        driver.quit()

if __name__ == "__main__":
    city_name = input("Enter the city name: ")
    get_coordinates(city_name)


# ## 6. Write a program to scrap all the available details of best gaming laptops from digit.in. 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_gaming_laptops():
    url = 'https://www.digit.in/top-products/best-gaming-laptops-40.html'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    laptop_data = []

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            laptops = soup.find_all('div', class_='TopNumbeHeading active-class')

            for laptop in laptops:
                laptop_info = {}

                laptop_name = laptop.find('div', class_='heading')
                if laptop_name:
                    laptop_info['Laptop Name'] = laptop_name.text.strip()
                else:
                    laptop_info['Laptop Name'] = '-'

                details = laptop.find_next('div', class_='product-detail')
                if details:
                    features = details.find_all('div', class_='value')
                    specs = details.find_all('div', class_='Specs-Wrap')

                    for feature, spec in zip(features, specs):
                        laptop_info[feature.text.strip()] = spec.text.strip()

                laptop_data.append(laptop_info)

    except requests.RequestException as e:
        print(f"Error: {e}")

    return laptop_data

def create_csv(laptop_data):
    df = pd.DataFrame(laptop_data)
    df.to_csv('gaming_laptops_digit.csv', index=False)
    print("Data saved to 'gaming_laptops_digit.csv'")

if __name__ == "__main__":
    scraped_data = scrape_gaming_laptops()
    create_csv(scraped_data)


# ## 7. Write a python program to scrape the details for all billionaires from www.forbes.com. Details to be scrapped: “Rank”, “Name”, “Net worth”, “Age”, “Citizenship”, “Source”, “Industry”. 
# 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_forbes_billionaires():
    url = 'https://www.forbes.com/billionaires/'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    billionaires_data = []

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            billionaires = soup.find_all('div', class_='person')

            for billionaire in billionaires:
                billionaire_info = {}

                rank = billionaire.find('div', class_='rank')
                if rank:
                    billionaire_info['Rank'] = rank.text.strip()
                else:
                    billionaire_info['Rank'] = '-'

                name = billionaire.find('div', class_='personName')
                if name:
                    billionaire_info['Name'] = name.text.strip()
                else:
                    billionaire_info['Name'] = '-'

                net_worth = billionaire.find('div', class_='netWorth')
                if net_worth:
                    billionaire_info['Net worth'] = net_worth.text.strip()
                else:
                    billionaire_info['Net worth'] = '-'

                age = billionaire.find('div', class_='age')
                if age:
                    billionaire_info['Age'] = age.text.strip()
                else:
                    billionaire_info['Age'] = '-'

                citizenship = billionaire.find('div', class_='countryOfCitizenship')
                if citizenship:
                    billionaire_info['Citizenship'] = citizenship.text.strip()
                else:
                    billionaire_info['Citizenship'] = '-'

                source = billionaire.find('div', class_='source-column')
                if source:
                    billionaire_info['Source'] = source.text.strip()
                else:
                    billionaire_info['Source'] = '-'

                industry = billionaire.find('div', class_='category')
                if industry:
                    billionaire_info['Industry'] = industry.text.strip()
                else:
                    billionaire_info['Industry'] = '-'

                billionaires_data.append(billionaire_info)

    except requests.RequestException as e:
        print(f"Error: {e}")

    return billionaires_data

def create_csv(billionaires_data):
    df = pd.DataFrame(billionaires_data)
    df.to_csv('forbes_billionaires.csv', index=False)
    print("Data saved to 'forbes_billionaires.csv'")

if __name__ == "__main__":
    scraped_data = scrape_forbes_billionaires()
    create_csv(scraped_data)


# ## 8. Write a program to extract at least 500 Comments, Comment upvote and time when comment was posted from any YouTube Video. 

# In[ ]:


get_ipython().system('google-api-python-client')
get_ipython().system('pip install google-api-python-client')


# In[ ]:


from googleapiclient.discovery import build

# YouTube API key
api_key = serviceusage.googleapis.com

# Create a YouTube service object
youtube = build('youtube', 'v3', developerKey=api_key)

# Specify the video ID of the YouTube video
video_id = 'xTVfhGleb5Q?si=PkfNIqXrGD7w4nrd'

# Request comments for the specified video
comments = youtube.commentThreads().list(
    part='snippet',
    videoId=video_id,
    maxResults=500  # Number of comments to retrieve
).execute()

# Extract comment details
comment_data = []
for comment in comments['items']:
    snippet = comment['snippet']['topLevelComment']['snippet']
    comment_text = snippet['textDisplay']
    comment_upvotes = snippet['likeCount']
    comment_time = snippet['publishedAt']

    comment_info = {
        'Comment': comment_text,
        'Upvotes': comment_upvotes,
        'Time Posted': comment_time
    }
    comment_data.append(comment_info)

# Display or save comment data as needed
print(comment_data)


# ## 9. Write a python program to scrape a data for all available Hostels from https://www.hostelworld.com/ in “London” location. You have to scrape hostel name, distance from city centre, ratings, total reviews, overall reviews, privates from price, dorms from price, facilities and property description. 
# 

# In[ ]:


import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_hostels_in_london():
    url = 'https://www.hostelworld.com/hostels/London'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36"
    }

    hostel_data = []

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            hostels = soup.find_all('div', class_='fabresult')

            for hostel in hostels:
                hostel_info = {}

                hostel_name = hostel.find('h2', class_='title')
                if hostel_name:
                    hostel_info['Hostel Name'] = hostel_name.text.strip()
                else:
                    hostel_info['Hostel Name'] = '-'

                distance = hostel.find('span', class_='distanceFrom')
                if distance:
                    hostel_info['Distance from City Centre'] = distance.text.strip()
                else:
                    hostel_info['Distance from City Centre'] = '-'

                ratings = hostel.find('div', class_='score orange big')
                if ratings:
                    hostel_info['Ratings'] = ratings.text.strip()
                else:
                    hostel_info['Ratings'] = '-'

                total_reviews = hostel.find('div', class_='reviews')
                if total_reviews:
                    hostel_info['Total Reviews'] = total_reviews.text.strip()
                else:
                    hostel_info['Total Reviews'] = '-'

                overall_reviews = hostel.find('div', class_='keyword')
                if overall_reviews:
                    hostel_info['Overall Reviews'] = overall_reviews.text.strip()
                else:
                    hostel_info['Overall Reviews'] = '-'

                price_privates = hostel.find('span', {'data-room-type': 'Private'})
                if price_privates:
                    hostel_info['Privates from Price'] = price_privates.text.strip()
                else:
                    hostel_info['Privates from Price'] = '-'

                price_dorms = hostel.find('span', {'data-room-type': 'Dorm'})
                if price_dorms:
                    hostel_info['Dorms from Price'] = price_dorms.text.strip()
                else:
                    hostel_info['Dorms from Price'] = '-'

                facilities = hostel.find('div', class_='facilities-label')
                if facilities:
                    hostel_info['Facilities'] = facilities.text.strip()
                else:
                    hostel_info['Facilities'] = '-'

                description = hostel.find('div', class_='rating-factors propCardRating clearfix')
                if description:
                    hostel_info['Property Description'] = description.text.strip()
                else:
                    hostel_info['Property Description'] = '-'

                hostel_data.append(hostel_info)

    except requests.RequestException as e:
        print(f"Error: {e}")

    return hostel_data

def create_csv(hostel_data):
    df = pd.DataFrame(hostel_data)
    df.to_csv('hostels_in_london.csv', index=False)
    print("Data saved to 'hostels_in_london.csv'")

if __name__ == "__main__":
    scraped_data = scrape_hostels_in_london()
    create_csv(scraped_data)

