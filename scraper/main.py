print('importing libraries')
import json
import time as t
from bs4 import BeautifulSoup as bs
import requests
import re
from geopy.geocoders import Nominatim
import json
import datetime as dt
print('imported libraries')

bin_url = 'https://api.npoint.io/d45deb15252bacd419f4'

source_in = ['ndtv','ht','inexp','rw','abp','idto','news18','et','zee','timnow']

exclude = []
errors=[]
headers = {'Authorization': 'Bearer bGjA3p4KBVY4eeBaGkyRJDNN'}

json_inp = requests.get('https://api.npoint.io/d45deb15252bacd419f4').json()

def update_data(sources):
    global json_inp
    source_index = {}
    ind = 0
    for source in json_inp:
        source_index[source['source_tag']] = ind
        ind+=1
    
    for source_id in sources:
        try:
            json_inp = requests.get('https://api.npoint.io/d45deb15252bacd419f4').json()
            so_t = t.time()
            print('started '+source_id)
            if(source_id in source_index):
                json_inp[source_index[source_id]] = globals()[source_id]()
            else:
                json_inp.append(globals()[source_id]())
            print('finished',source_id,'in',t.time() - so_t ,'seconds')
            requests.post(bin_url,json=json_inp,headers=headers)
        except Exception as e:
            errors.append({source_id:str(e)})
        print(errors)
        # with open('data/data.json', 'w') as jso:
        #         json.dump(json_inp,jso,indent=3)

ti = t.time()

geolocator = Nominatim(user_agent="extractor")

places = []
with open('./data/places.json', 'r') as js:
    places = json.load(js)

def replaceMultiple(string, replace=[], replaceWith=''):
    for item in replace:
        string = string.replace(item, replaceWith)
    return string

abbrevated_places = {'UP':"Uttar Pradesh",'MP':"Madhya Pradesh",'TN':"Tamil Nadu","uttar-pradesh":"Uttar Pradesh","madhya-pradesh":"Madhya Pradesh"}

def addData(data, place, link, title, image):
    data['count']+=1
    if(place not in data['data']):
        if(len(place) == 2):
            if(place.upper() not in title):
                return
            place = abbrevated_places[place]
        elif('-' in place):
            place = abbrevated_places[place]
        cord = geolocator.geocode(place)
        data['data'][place] = {'coordinates' : [cord.latitude, cord.longitude],'count': 0 , 'links': [{'title':title, 'url':link, 'image':image}]}
    else:
        if(len(place) == 2):
            if(place.upper() not in title):
                return
            place = abbrevated_places[place]
        elif('-' in place):
            place = abbrevated_places[place]
        data['data'][place]['links'].append({'title':title, 'url':link, 'image':image})
    data['data'][place]['count'] = len(data['data'][place]['links'])

    return data

def zee():
    data = {}
    data['source_tag'] = 'zee'
    data['name'] = 'Zee news'
    data['image'] = 'https://zeenews.india.com/sites/default/files/images/icons/icon-192x192.png'
    data['count'] = 0
    data['data'] = {}
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    for a in range(0,10):
        print("Scraping page",a)
        articles = bs(requests.get('https://zeenews.india.com/common/getmorenews/%x/120183'%(a),headers=agent).content,'html.parser').select('div.row')
        for news in articles:
            try:
                image = news.find('img')['src']
                link = 'https://zeenews.india.com/' + news.find('a')['href']
                title = news.find('a')['title']
                time = bs(requests.get(link,headers=agent).content,'html.parser').select('div.articleauthor_details > span')[-4].text[:-4]
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%b %d, %Y, %I:%M %p")):
                    return data
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
            except Exception as e:
                errors.append((data['source_tag'],link,e))
                    
def et():
    data = {}
    data['source_tag'] = 'et'
    data['name'] = 'The Economic Times'
    data['image'] = 'https://img.etimg.com/photo/89824128.cms'
    data['count'] = 0
    data['data'] = {}
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    for a in range(1,10):
        print('Scraping page',a)
        document = bs(requests.get('https://economictimes.indiatimes.com/lazyloadlistnew.cms?msid=81582957&curpg='+str(a),headers = agent).content,'html.parser')
        for article in document.select('div.eachStory'):
            try:
                if(not article.select_one('img')):
                    continue
                image = 'https://economictimes.indiatimes.com/' + article.select_one('img')['data-original']
                link = 'https://economictimes.indiatimes.com/' + article.select_one('a')['href']
                title = article.select_one('h3>a').text
                time = article.select_one('time')['data-time'][:-4]
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%b %d, %Y, %I:%M %p")):
                    return data
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
            except Exception as e:
                errors.append((data['source_tag'],link,e))
                    
    return data
    
def news18():
    data = {}
    data['source_tag'] = 'news18'
    data['name'] = 'News 18'
    data['image'] = 'https://www.adgully.com/img/800/201906/news-18-india-2.jpg'
    data['count'] = 0
    data['data'] = {}

    for a in range(1,5):
        print('Scraping page ',a)
        articles = bs(requests.get('https://www.news18.com/india/page-' + str(a)).content, 'html.parser').select('div.blog_list_row')
        for article in articles:
            try:
                link = article.select_one('a')['href']
                title = article.select_one('div.blog_title').text
                document = bs(requests.get(link).content, 'html.parser')
                loc = document.find('span',{"id": "location_info"})
                if document.select_one('figure > img'):
                    time = document.select('div.article_details_list > div')[-2].text[14:-4]
                    if(time==""):
                        continue
                    if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%B %d, %Y, %H:%M")):
                        return data
                    image = document.select_one('figure > img')['src']
                    for place in places:
                        if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                            addData(data, place, link, title, image)
            except Exception as e:
                errors.append((data['source_tag'],link,e))
    return data

def inexp():
    data = {}
    data['source_tag'] = 'inexp'
    data['name'] = 'The Indian Express'
    data['image'] = 'https://play-lh.googleusercontent.com/dSS5OclMxGTasbTH1PYsxZ9bmXZyv7xcU4elR7afSqXns-6MEo1ZYteZi-l75E3g5kY'
    data['count'] = 0
    data['data'] = {}

    for a in range(4,5):
        print('Scraping page ',a)

        document = requests.get('https://indianexpress.com/section/cities/page/' + str(a))
        articles = bs(document.content, 'html.parser').select('div.articles')

        for article in articles:
            try:
                link = article.select_one('h2.title > a')['href']
                title = article.select_one('h2.title > a').text
                image = article.select_one('a > img')['data-lazy-srcset'].split(" ")[0]
                time = article.select_one('div.date').text.lstrip().replace('  ',' ')
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%B %d, %Y %I:%M:%S %p")):
                    continue
                place_link = link.split('/')[5].capitalize()
                if(place_link in places):
                    addData(data, place_link, link, title, image)
                    continue
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",place_link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
            except Exception as e:
                errors.append((data['source_tag'],link,e))
                    
    return data

def abp():
    data = {}
    data['source_tag'] = 'abp'
    data['name'] = 'ABP News'
    data['image'] = 'https://static.abplive.com/frontend/images/nw-eng-og.png?impolicy=abp_cdn&imwidth=600'
    data['count'] = 0
    data['data'] = {}

    for a in range(1,10):
        print('Scraping page ',a)

        document = requests.get('https://news.abplive.com/news/india/page-' + str(a))
        articles = bs(document.content, 'html.parser').select('div.uk-width-3-4 > div > div > div.other_news')[:19]

        for article in articles:
            try:
                link = article.find('a')['href']
                title = article.find('a')['title']
                image = article.find('img')['data-src']
                doc_cont = bs(requests.get(link).content, 'html.parser').select_one('p.article-author').text[5:]
                time = doc_cont[doc_cont.index(':')+2:doc_cont.rindex('(')-1]
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%d %b %Y %I:%M %p")):
                    return data
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
            except Exception as e:
                errors.append((data['source_tag'],link,e))
                    
def ndtv():
    data = {}
    data['source_tag'] = 'ndtv'
    data['name'] = 'NDTV'
    data['image'] = 'https://cdn.ndtv.com/common/images/ogndtv.png'
    data['count'] = 0
    data['data'] = {}

    for a in range(1,15):
        print('Scraping page ',a)

        document = requests.get('https://www.ndtv.com/india/page-' + str(a))
        news_divs = bs(document.content, 'html.parser').select("div[class='news_Itm']")
        for news_item in news_divs:
            try:
                news_link = news_item.select_one('h2.newsHdng > a')
                image = news_item.select_one('div.news_Itm-img > a > img')['src']
                link = news_link['href']
                title = news_link.text
                doc = bs(requests.get(link).content,'html.parser')
                loc_item = doc.find("b", class_="place_cont")
                if doc.select_one("div.ins_instory_dv_cont > img")!= None:
                    image = doc.select_one("div.ins_instory_dv_cont > img")['src']
                loc = None
                if(loc_item!=None):
                    loc = loc_item.text[:-2]
                else:
                    for place in places:
                        if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                            loc = place
                            
                    if(loc==None):
                        continue
                tim = doc.find("span",attrs={"itemprop":"dateModified"})['content']
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(tim[:-9], "%Y-%m-%dT%H:%M")):
                    return data

                if(loc in places):
                    addData(data, loc, link, title, image)
                    data['count']+=1
                    continue
            except Exception as e:
                errors.append((data['source_tag'],link,e))
            
    return data

def ht():
    data = {}
    data['source_tag'] = 'ht'
    data['name'] = 'Hindustan Times'
    data['image'] = 'https://www.hindustantimes.com/res/images/logo.png'
    data['count']=0
    data['data'] = {}
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

    for a in range(1,10):
        print("scraping page " , a)
        document = requests.get('https://www.hindustantimes.com/cities/page-' + str(a),headers=agent)
        news_divs = bs(document.content, 'html.parser').select("div[data-vars-storytype='story']")
        for news in news_divs:
            try:    
                title = news.select_one('h3.hdg3 > a').text
                time = replaceMultiple(news.find("div", class_= "dateTime").text, ["IST", "Published", "Updated", "on",","]).split(" ")[2:7]
                #ti -> [Mon, DD, YYYY, HH:MM, AM/PM]
                if(dt.datetime.now()-dt.timedelta(hours=18,minutes=30)>dt.datetime.strptime(" ".join(time), "%b %d %Y %I:%M %p")):
                    return data
                    #break if article was posted more than 24 hours ago
                link = 'https://www.hindustantimes.com' + news.select_one('h3.hdg3 > a')['href']
                image = bs(requests.get(link,headers=agent).content, 'html.parser').select_one('div.storyParagraphFigure').find("img")['src']
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
                        data['count']+=1
            except Exception as e:
                errors.append((data['source_tag'],link,e))
                    
    return data

def rw():
    data = {}
    data['source_tag'] = 'rw'
    data['name'] = 'Republic World'
    data['image'] = 'https://bharat.republicworld.com/assets/images/rdot_icon_red.svg'
    data['count'] = 0 #excludes calibration
    data['data'] = {}

    for a in range(1,2):

        print('scraping page ',a )

        document = requests.get('https://www.republicworld.com/india-news/general-news/' + str(a))
        doc = bs(document.content, 'html.parser')
        for news in doc.select('article.hover-effect'):
            try:
                link = news.select_one('a')['href']
                image = news.select_one('img')['src']
                title = news.select_one('img')['title']
                time = bs(requests.get(link).content, 'html.parser').find('time')['datetime']

                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time[:19],"%Y-%m-%dT%H:%M:%S")):
                    return data
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place,link, title, image)
                        data['count']+=1
            except Exception as e:
                errors.append((data['source_tag'],link,e))
    return data

def idto():
    data = {}
    data['source_tag'] = 'idto'
    data['name'] = 'India Today'
    data['image'] = 'https://akm-img-a-in.tosshub.com/sites/indiatodaygroup/ITG-logo-main.png'
    data['count'] = 0 #excludes calibration
    data['data'] = {}
    domain = 'https://www.indiatoday.in'
    for a in range(0,10):
        page_data = json.loads(requests.get(f'https://www.indiatoday.in/api/ajax/loadmorecontent?page={a}&pagepath=/india').content)
        for article in page_data['data']['content']:
            try:
                title = article['title_short']
                image = article['big_story_image']
                link = domain + article['canonical_url']
                time = article['datetime_published']
                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time[:19],"%Y-%m-%d %H:%M:%S")):
                    return data
                for place in places:
                    if(re.search("[\/-]"+place+"[\/-]",link,re.IGNORECASE)):
                        addData(data, place,link, title, image)
                        data['count']+=1
            except Exception as e:
                errors.append((data['source_tag'],link,e))   
    return data

def zee():
    data = {}
    data['source_tag'] = 'zee'
    data['name'] = 'Zee news'
    data['image'] = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSUUloj_N7pWOlr1uZEjf4w-IC0L8aREBqTzA&usqp=CAU'
    data['count'] = 0
    data['data'] = {}
    agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
    for a in range(0,10):
        print("Scraping page",a)
        articles = bs(requests.get('https://zeenews.india.com/common/getmorenews/%x/120183'%(a),headers=agent).content,'html.parser').select('div.row')
        for news in articles:
            image = news.find('img')['src']
            link = 'https://zeenews.india.com/' + news.find('a')['href']
            title = news.find('a').text
            time = bs(requests.get(link,headers=agent).content,'html.parser').select('div.articleauthor_details > span')[-4].text[:-4]
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%b %d, %Y, %I:%M %p")):
                return data
            for place in places:
                if(re.search(place ,link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    break

def run(event, conext):
    ti = t.time()
    update_data(source_in)
    print(t.time() - ti, ' time taken')

while True:
    run(1,1)
    print(f"sleeping for {(900 - (t.time() - ti))//60} minutes")
    t.sleep(900 - (t.time() - ti))