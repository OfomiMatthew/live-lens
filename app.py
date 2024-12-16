from flask import Flask, render_template,url_for,request,make_response
import feedparser
import json 
import urllib.parse
import urllib.request
import datetime 



app = Flask(__name__)


CURRENCY_URL ="https://openexchangerates.org//api/latest.json?app_id=e6a8badb86e646ab88eee8fdcb2f4ee8"
BBC_FEED = "https://feeds.bbci.co.uk/news/rss.xml"
RSS_FEEDS = {'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
 'cnn': 'http://rss.cnn.com/rss/edition.rss',
 'fox': 'http://feeds.foxnews.com/foxnews/latest',
 'iol': 'http://www.iol.co.za/cmlink/1.640'}

DEFAULTS ={
    'publication':'bbc',
    'city':'Lagos, Nigeria',
    'currency_from':"USD",
    'currency_to':"NGN"
}


@app.route('/',methods=['GET','POST'])

def home():
    # publication = request.args.get('publication')
    # if not publication:
    #     publication = request.cookies.get('publication')
    #     if not publication:
    #         publication = DEFAULTS['publication']
    publication = get_value_with_fallback('publication')
    articles = get_news(publication)
    city = get_value_with_fallback('city')
    # if not city:
    #     city = DEFAULTS['city']
    weather = get_weather(city)

    currency_from = get_value_with_fallback('currency_from')
    # if not currency_from:
    #     currency_from = DEFAULTS['currency_from']
    currency_to = get_value_with_fallback('currency_to')
    # if not currency_to:
    #     currency_to = DEFAULTS['currency_to']
    rate,currencies = get_rate(currency_from,currency_to)
    response = make_response(render_template('news.html',
    articles=articles,
    weather=weather,
    currency_from=currency_from,currency_to=currency_to,rate=rate,currencies=sorted(currencies)))
    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    response.set_cookie("publication",publication,expires=expires)
    response.set_cookie("city",city,expires=expires)
    response.set_cookie("currency_from",currency_from,expires=expires)
    response.set_cookie("currency_to",currency_to,expires=expires)
    return response

def get_news(query):
    
    if not query or query.lower() not in RSS_FEEDS:
        publication =   DEFAULTS['publication']
    else:
        publication = query.lower()

    feed = feedparser.parse(RSS_FEEDS[publication])
    return feed['entries']


def get_weather(query):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=97b213ca8849617a5cbf5181ebe18603"
    query = urllib.parse.quote(query)
    url = api_url.format(query)
    data = urllib.request.urlopen(url).read()
    parsed = json.loads(data)
    weather = None 
    if parsed.get("weather"):
        weather = {
            "description":parsed['weather'][0]['description'],
            'temperature':parsed['main']['temp'],
            'city':parsed['name'],
            'country':parsed['sys']['country']
        }
    return weather

def get_rate(frm,to):
    all_currency = urllib.request.urlopen(CURRENCY_URL).read()
    parsed = json.loads(all_currency).get('rates')
    frm_rate = parsed.get(frm.upper())
    to_rate = parsed.get(to.upper())
    return (to_rate/frm_rate, parsed.keys())

def get_value_with_fallback(key):
    if request.args.get(key):
        return request.args.get(key)
    if request.cookies.get(key):
        return request.cookies.get(key)
    return DEFAULTS[key]



# e6a8badb86e646ab88eee8fdcb2f4ee8
if __name__ == '__main__':
    app.run(debug=True,port=7000)