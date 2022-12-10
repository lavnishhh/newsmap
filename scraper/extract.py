from bs4 import BeautifulSoup as bs
import requests
import re
from geopy.geocoders import Nominatim
import json
import datetime as dt


geolocator = Nominatim(user_agent="extractor")

places = []
with open('./data/places.json', 'r') as js:
    places = json.load(js)

def replaceMultiple(string, replace=[], replaceWith=''):
    for item in replace:
        string = string.replace(item, replaceWith)
    return string

abbrevated_places = {'UP':"Uttar Pradesh",'MP':"Madhya Pradesh",'TN':"Tamil Nadu",'UK':'Uttarakhand',"uttar-pradesh":"Uttar Pradesh","madhya-praedsh":"Madhya Pradesh"}
def addData(data, place, link, title, image):
    data['count']+=1
    if(place not in data['data']):
        if(len(place) == 2):
            place = abbrevated_places[place]
        if('-' in place):
            place = abbrevated_places[place]
        cord = geolocator.geocode(place)
        data['data'][place] = {'cordinates' : [cord.longitude, cord.latitude],'count': 0 , 'links': [{'title':title, 'url':link, 'img':image}]}
    else:
        data['data'][place]['links'].append({'title':title, 'url':link, 'img':image})
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
            image = news.find('img')['src']
            link = 'https://zeenews.india.com/' + news.find('a')['href']
            title = news.find('a')['title']
            time = bs(requests.get(link,headers=agent).content,'html.parser').select('div.articleauthor_details > span')[-4].text[:-4]
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%b %d, %Y, %I:%M %p")):
                return data
            for place in places:
                if(re.search(place ,link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    break
            for abb_place in abbrevated_places:
                if abb_place in link[link[::-1].index('/'):].split('-'):
                    addData(data, place, link, title, image)
                    break


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
            if(not article.select_one('img')):
                continue
            image = 'https://economictimes.indiatimes.com/' + article.select_one('img')['data-original']
            link = 'https://economictimes.indiatimes.com/' + article.select_one('a')['href']
            title = article.select_one('h3>a').text
            time = article.select_one('time')['data-time'][:-4]
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%b %d, %Y, %I:%M %p")):
                return data
            for place in places:
                if(re.search(place ,link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    break
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
                    if(re.search(place ,link,re.IGNORECASE)):
                        addData(data, place, link, title, image)
                        break
    return data

def inexp():
    data = {}
    data['source_tag'] = 'inexp'
    data['name'] = 'The Indian Express'
    data['image'] = 'https://play-lh.googleusercontent.com/dSS5OclMxGTasbTH1PYsxZ9bmXZyv7xcU4elR7afSqXns-6MEo1ZYteZi-l75E3g5kY'
    data['count'] = 0
    data['data'] = {}

    for a in range(1,10):
        print('Scraping page ',a)

        document = requests.get('https://indianexpress.com/section/cities/page/' + str(a))
        articles = bs(document.content, 'html.parser').select('div.articles')

        for article in articles:
            link = article.select_one('h2.title > a')['href']
            title = article.select_one('h2.title > a').text
            image = article.select_one('a > img')['data-lazy-srcset'].split(" ")[0]
            time = article.select_one('div.date').text.lstrip().replace('  ',' ')
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%B %d, %Y %I:%M:%S %p")):
                continue
            place_link = link.split('/')[5]
            if(place_link.capitalize() in places):
                addData(data, place_link, link, title, image)
                continue
            for place in places:
                if(re.search(place ,place_link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    break
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
            link = article.find('a')['href']
            title = article.find('a')['title']
            image = article.find('img')['data-src']
            doc_cont = bs(requests.get(link).content, 'html.parser').select_one('p.article-author').text[5:]
            time = doc_cont[doc_cont.index(':')+2:doc_cont.index('(')-1]
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%d %b %Y %I:%M %p")):
                return data
            for place in places:
                if(re.search(place ,link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    break

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
                    if(re.search(place ,link,re.IGNORECASE)):
                        loc = place
                        break
                if(loc==None):
                    continue
            tim = doc.find("span",attrs={"itemprop":"dateModified"})['content']
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(tim[:-9], "%Y-%m-%dT%H:%M")):
                return data

            if(loc in places):
                addData(data, loc, link, title, image)
                data['count']+=1
                continue
            
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
            title = news.select_one('h3.hdg3 > a').text
            image = news.select_one('figure > span > a > img')['src']
            #upload time
            ti = replaceMultiple(news.find("div", class_= "dateTime").text, ["IST", "Published", "Updated", "on",","]).split(" ")[2:7]
            #ti -> [Mon, DD, YYYY, HH:MM, AM/PM]
            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(" ".join(ti), "%b %d %Y %I:%M %p")):
                return data
                #break if article was posted more than 24 hours ago
            link = 'https://www.hindustantimes.com' + news.select_one('h3.hdg3 > a')['href']
            for place in places:
                if(re.search(place ,link,re.IGNORECASE)):
                    addData(data, place, link, title, image)
                    data['count']+=1
                    break
    return data

def rw():
    data = {}
    data['source_tag'] = 'rw'
    data['name'] = 'Republic World'
    data['image'] = 'https://bharat.republicworld.com/assets/images/rdot_icon_red.svg'
    data['count'] = 0 #excludes calibration
    data['data'] = {}

    for a in range(1,10):

        print('scraping page ',a )

        document = requests.get('https://www.republicworld.com/india-news/general-news/' + str(a))
        doc = bs(document.content, 'html.parser')
        for news in doc.select('article.hover-effect'):
            link = news.select_one('a')['href']
            image = news.select_one('img')['src']
            title = news.select_one('img')['title']
            time = bs(requests.get(link).content, 'html.parser').find('time')['datetime']

            if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time[:19],"%Y-%m-%dT%H:%M:%S")):
                return data
            for place in places:
                if(re.search(place ,link[54:].replace('-',' '),re.IGNORECASE)):
                    addData(data, place,link, title, image)
                    data['count']+=1
    return data

def idto():
    data = {}
    data['source_tag'] = 'idto'
    data['name'] = 'India Today'
    data['image'] = 'https://akm-img-a-in.tosshub.com/sites/indiatodaygroup/ITG-logo-main.png'
    data['count'] = 0 #excludes calibration
    data['data'] = {}
    for a in range(0,10):
        print('scraping page '+str(a))
        doc = bs(requests.get('https://www.indiatoday.in/india?page='+str(a)).content, 'html.parser')
        news_divs = doc.select('div.catagory-listing')
        for news in news_divs:
            found = False
            link = 'https://www.indiatoday.in' + news.select_one('div.detail > h2 > a')['href']
            if('video' not in link and 'photo' not in link and 'live' not in link and 'interactive' not in link):
                article = bs(requests.get(link).content, 'html.parser')
                time = article.find('meta',attrs={'itemprop': 'datePublished'})['content'][:-6]
                image = news.select_one('img')['src']
                title = news.select_one('div.detail > h2')['title']

                if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")):
                    return data
                for place in places:
                    if(re.search(place ,link,re.IGNORECASE)):
                        addData(data, place,link,title, image)
                        found = True
                        break
                
                #if not found in url
                if(article.select_one('dl.profile-byline > dt')!=None and not found):
                    for place in places:
                        if(re.search(place ,article.select_one('dl.profile-byline > dt').text,re.IGNORECASE)):
                            addData(data, place,link,title, image)
                            break
    return data

def timnow():
    data = {}
    data['source_tag'] = 'timnow'
    data['name'] = 'Times Now'
    data['image'] = 'https://www.timesnownews.com/assets/icons/svg/times-now.svg'
    data['count'] = 0
    data['data'] = {}

    news_info = json.loads(requests.get('https://apiprod.timesnownews.com/api/getlisting?seopath=mirror-now/in-focus&pageno=1&itemcount=30').content)['response']
    for news in news_info['sections']['tnn_87847632']['children']:
        title = news['title']
        link = 'https://www.timesnownews.com/' + news['seopath'] + '-article-' + str(news['msid'])
        time = news['metainfo']['LastPublishMilliTime']['value']
        image  = 'https://static.tnn.in/photo/msid-{msid},imgsize-26308,updatedat-{upd},width-200,height-200,resizemode-75/{msid}.jpg'.format(msid = news['msid'], upd= news['updatedate'])
        #now - 1 day > start + millisec === now > start + 1 + millisec
        if(dt.datetime.now()>dt.datetime(year=1970,month=1,day=2,hour=5,minute=30,second=1)+dt.timedelta(milliseconds=int(time))):
            return data
        for place in places:
            if(re.search(place ,link,re.IGNORECASE)):
                addData(data, place, link, title, image)
                break
    return data

def cnbc():
    data = {}
    data['source_tag'] = 'cnbc'
    data['name'] = 'CNBC TV18'
    data['image'] = 'https://upload.wikimedia.org/wikipedia/commons/2/23/CNBC_TV18_logo.png'
    data['count'] = 0
    data['data'] = {}

    news_info = json.loads(requests.get('https://www.cnbctv18.com/api/v1/category/india?page=1&limit=40').content)['result']
    for news in news_info:
        title = news['headline']
        time = news['update_date']
        link = 'https://www.cnbctv18.com/' + news['posturl']
        image = list(json.loads(news['post_image_arr'])['images'].values())[0]
        if(dt.datetime.now()-dt.timedelta(days=1)>dt.datetime.strptime(str(time), "%Y%m%d%H%M%S")):
            return data
        for place in places:
            if(re.search(place ,link,re.IGNORECASE)):
                addData(data, place, link, title, image)
                break
    return data