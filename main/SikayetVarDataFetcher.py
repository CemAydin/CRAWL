#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from queue import Queue

import requests
import codecs
import csv

import sys
import openpyxl
import  pandas as pd
from pandas import ExcelWriter
from google.cloud import datastore
from google.auth import compute_engine
SLEEP_TIME = 1
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1004cem+",
  database="sikayet"
)



mycursor = mydb.cursor()
mycursor.execute("SET AUTOCOMMIT=1")

if sys.version_info[0] >= 3:
    unicode = str


from htmlmin.minify import html_minify


from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup



def simple_get(url):
    """
    GET isteği yaparak url almaya çalışır.
    Yanıt HTML veya XML ise, içeriğini döndürür.
    Aksi halde None döner.
    """
    try:
        # with closing(requests.get(url, stream=True, proxies=proxies)) as resp:
        with closing(requests.get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('{0} için yapılan istekte hata döndü: {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    # Yanıt HTML ise True, aksi takdirde False döndürür.

    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    # Hataları kaydeder.

    print(e)


import mysql.connector

domain = 'https://www.sikayetvar.com'
global credentials
global client
print("Setup Database Connection")
credentials = compute_engine.Credentials()
# service account
client = datastore.Client.from_service_account_json('sa1.json')
scraped_data = []

def toList(s):
    listToStr = ', '.join([str(elem) for elem in s])
    return listToStr

def extract_data(page):
    sikayet_url = domain + page
    sikayet_source = simple_get(sikayet_url)
    sikayet_soup = BeautifulSoup(html_minify(sikayet_source), 'html.parser')
    artdic = {}
    tempdic = {}

    title = sikayet_soup.find('title')
    if title != None:
        title = title.text.strip('\n')
        title = title.replace(' - Şikayetvar', '')
    description = sikayet_soup.find('div', {'class': 'card-text'})
    if description != None:
        description = description.text.strip('\n')
    date = sikayet_soup.find('span', {'class': 'info-icn time-tooltip'})
    if date != None:
        date = date['title']
    views = sikayet_soup.find('span', {'class': 'js-view-count'})
    if views != None:
        find = views.find('span', {'class': 'count'})
        views = find.text
    try:
        hashtags = sikayet_soup.find_all('div', {'class': 'detailComp-tags clearfix'})
        tags = []
        for a in hashtags[0].find_all('a', href=True):
            tags.append(a['title'])
    except Exception as a:
        print(a)
    tempdic["brand"]=brand
    tempdic["sikayet_url"] = sikayet_url
    tempdic["title"] = title
    tempdic["description"] = description
    tempdic["views"] = views
    tempdic["tags"] = toList(tags)
    tempdic["date"] = date


    val = (brand, sikayet_url, title, description, views, toList(tags), date)
    pages_result.append(val)
    #insertdb(val)
    #return val
    artdic[sikayet_url] = tempdic
    #writeToDB(artdic)
    return artdic


def insertdb(val):
    sql = """INSERT INTO `sikayet`.`sikayet_text`
(
`brand`,
`URL`,
`Title`,
`Description`,
`Views_count`,
`Tags`,
`zaman`) VALUES (%s,%s, %s,%s,%s,%s,%s)"""
    print("insert ediyorum")
    mycursor.execute(sql, val)
    print("insert ettim")


def get_page_num(brand_soup):
    pagination = brand_soup.find('nav', {'class': 'pagination-wrap'})
    """
    Markaya ait sayfa sayısının tespiti:
    İlk sayfanın değeri 0'dır.
    Eğer pagination değeri varsa +1 eklenir.
    """
    if pagination != None:

        num_of_pages = pagination.find_all('a')
        page_numbs = []

        for page_no in num_of_pages:
            page_numbs.append(page_no.text)

        last_page_no = int(page_numbs[-2]) + 1

    else:
        last_page_no = 2
    return  last_page_no


def get_item_url(page_num, brand_url):
    time.sleep(SLEEP_TIME)
    page_numbered_url = brand_url + '?page=' + str(page_num)

    log = '\n ' + str(page_numbered_url) + ' için ' + str(page_num) + '. sayfa okunuyor...\n'
    page_source = simple_get(page_numbered_url)
    page_soup = BeautifulSoup(html_minify(page_source), 'html.parser')
    item_pages = []
    """
        Her sayfa ziyaret edilir
        Sayfalar diziye alınır
        """
    find_all_card_url = page_soup.find_all('p', {'class': 'card-text'})
    for complaint in find_all_card_url:
        """ contents_ = complaint.contents
         href_ = contents_[1]
         item_pages.append(href_)"""
        for a in complaint.find_all('a', href=True):
            item_pages.append(a['href'])
    return item_pages
def get_all_items_url(brand):
    brand_url = domain + '/' + brand

    brand_source = simple_get(brand_url)
    brand_soup = BeautifulSoup(html_minify(brand_source), 'html.parser')

    last_page_no = get_page_num(brand_soup)
    items_url = []
    for x in range(1, last_page_no):
        item_pages = get_item_url(x,brand_url)
        items_url=items_url+item_pages
    return items_url

headers = [ "sikayet_url", "title", "description", "views", "tags","date"]

def printFileXlsx(file_name, columns, result):
    df = pd.DataFrame(result, columns=columns)
    df.to_excel(file_name+ ".xlsx", index=False, encoding='utf-8')


from multiprocessing import Pool

brand = "garanti-bbva"

pages_result=[]
def printqueue(queue, data):
    queue.put(data)
    return queue

def writeToDB( resultArticleDetailsList):
    # Extract single elements
    articleList = []

    for resultArticleDetails in resultArticleDetailsList:
        for value in resultArticleDetails.values():
            str_articlenumber = value["sikayet_url"]
            str_URL = value['sikayet_url']
            str_title = value['title']
            str_views = value['views']
            str_pubdate = value['date']
            str_text = value['description']
            str_brand = value['brand']
            try:
                int_views = value['views']
            except:
                int_views = 0
            Tag_list = value['tags']
            # Create new Article Entity
            Article = datastore.Entity(client.key('Article_ID', str_articlenumber), exclude_from_indexes=['Text'])
            Article.update({
                "URL": str_URL,
                "Title": str_title,
                "Views": str_views,
                "PublishingDate": str_pubdate,
                "Text": str_text,
                "Claps": int_views,
                "Tags": Tag_list,

                "Brand": str_brand
            })
            articleList.append(Article)

    client.put_multi(articleList)
    return (True)

import time

if __name__ == '__main__':
    result=[]


    start = time.time()
    print("hello")
    print(start)


    brand_url = domain + '/' + brand

    brand_source = simple_get(brand_url)
    brand_soup = BeautifulSoup(html_minify(brand_source), 'html.parser')

    last_page_no = get_page_num(brand_soup)
    items_url = []
    for x in range(1, last_page_no):
        print(x)
        item_pages = get_item_url(x,brand_url)
        with Pool(1) as p:
            writeToDB(p.map(extract_data, item_pages))
    end = time.time()
    print(end - start)
"""  alllinks=get_all_items_url(brand)
    for i in alllinks:
        extract_data(i)
"""