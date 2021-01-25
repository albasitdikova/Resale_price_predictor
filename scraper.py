#!/usr/bin/env python
# coding: utf-8

# In[1]:


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys


# In[2]:


def money_to_int(moneystring):

    '''
    A helper function to return string about bag price to integer format
    
    Parameters
    ----------
    string : A string of text.
    
    Returns
    -------
    A integer number if the string contains information and None otherwise.
    '''
    
    if moneystring == 0:
        return None
    moneystring = moneystring.replace('$', '').replace(',', '').replace('USD', '').replace('Est.', '').replace('Retail', '')
    return int(moneystring)


# In[3]:


def size_to_float(sizestring):
    
    '''
    A helper function get string about width, height, depth of bag, 
    multiplicate it to get a volume of the bag and return it to float format
    
    Parameters
    ----------
    string : A string of text.
    
    Returns
    -------
    A float number if the string contains information and None otherwise.
    '''

    if sizestring == 0:
        return None
    volume = 1
    sizestring = sizestring.replace('W', '').replace('H', '').replace('x', '')
    size_list = sizestring.split('"')
    if len(size_list) < 3:
        return None
    for i,el in enumerate(size_list):
        if i < 3:
            el = float(el.strip())
            volume = volume * el
            
    return volume


# In[4]:


def get_details_value(soup, field_name):
    
    '''Grab a value from REBAG HTML
    
    Takes a string attribute of a bag on the page and returns the string in
    the next sibling object (the value for that attribute) or None if nothing is found.
    
    Parameters
    ----------
    string : A string of text.
    
    Returns
    -------
    string: A string of text.
    '''
    
    obj = soup.find(text=field_name)
    
    if not obj: 
        return None
    
    # this works for most of the values
    next_element = obj.findNext()
    
    if next_element:
        return next_element.text 
    else:
        return None


# In[5]:


def get_bags_dict(link, driver):
    '''
    From REBAG link stub, request bag html, parse with BeautifulSoup, and
    collect 
        - title 
        - brand
        - price 
        - condition
        - retail price
        - volume
        - exterior color
        - exterior material
        - interior color
        - interior materal
        - accesories
        - nimber of accessories
    Return information as a dictionary.
    '''
    
    base_url = 'https://shop.rebag.com'
    
    #Create full url to scrape
    url = base_url + link
    
    #Request HTML and parse
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    headers = ['Title', 'Brand', 'Price', 'Condition', 'Retail_Price', 'Volume', 'Exterior_Color',
               'Exterior_Material', 'Interior_Color', 'Interior_Material', 'Accessories', 'Ac_Count']
      
    #title
    title_string = soup.find('title').text
    title = title_string.split('-')[0].strip()
    title = title.rsplit(' ', 1)[0]
    print(title)
    
    #brand
    if soup.find(class_='pdp__designer'):
        brand = soup.find(class_='pdp__designer').text
    else:
        brand = None
        
    #price
    if soup.find(itemprop='price'):
        raw_price = soup.find(itemprop='price').text 
        price = money_to_int(raw_price)
    else:
        price=None
    
    #condition
    if soup.find(class_='pdp__condition-item--selected'):
        condition = soup.find(class_='pdp__condition-item--selected').text
    else:
        condition=None
    
    #retail price
    if soup.find(class_='pdp__retail-price'):
        raw_retail_price = soup.find(class_='pdp__retail-price').text
        retail_price = money_to_int(raw_retail_price)
    else:
        retail_price=None
        
    #exterior color
    ex_color = get_details_value(soup,'Exterior Color')
    
    #exterior material
    ex_material = get_details_value(soup,'Exterior Material')
    
    #interior color
    int_color = get_details_value(soup,'Interior Color')
    
    #interior material
    int_material = get_details_value(soup,'Interior Material')
    
    # Volume    
    raw_volume = get_details_value(soup, 'SIZE AND FIT')
    if (raw_volume):
        volume = size_to_float(raw_volume)
    else:
        volume = None
        
    #Accessories
    accessories=[]
    for el_class in soup.find_all(class_="pdp__group-title"):
        if el_class.text == 'Accessories':
            for element in el_class.findNext().find_all('div'):
                accessories.append(element.text)
    if len(accessories)==0:
        accessories = None
    
    #number of accesories
    if accessories == None:
        accessories_count = None
    elif len(accessories) == 1 and accessories[0]=='No accessories':
        accessories_count = 0
    else:
        accessories_count = len(accessories)
        
    #add all features to dict
    bags_dict = dict(zip(headers, [title,
                                brand,
                                price,
                                condition,
                                retail_price,
                                volume,
                                ex_color,
                                ex_material,
                                int_color, 
                                int_material,
                                accessories,
                                accessories_count]))

    return bags_dict

