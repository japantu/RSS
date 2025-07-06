from flask import Flask, Response
import feedparser
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)

RSS_FEEDS = [
    "http://himasoku.com/index.rdf",
    "https://hamusoku.com/index.rdf",
    "http://blog.livedoor.jp/kinisoku/index.rdf",
    "https://alfalfalfa.com/index.rdf",
    "https://itainews.com/index.rdf",
    "http://blog.livedoor.jp/news23vip/index.rdf",
    "http://yaraon-blog.com/feed",
    "http://blog.livedoor.jp/bluejay01-review/index.rdf",
    "https://www.4gamer.net/rss/index.xml",
    "https://www.gizmodo.jp/atom.xml"
]

def fetch_and_sort():
    items = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            pub = e.get('published_parsed') or e.get('updated_parsed')
            if pub:
                item = {
                    'title': e.get('title', ''),
                    'link': e.get('link', ''),
                    'pubDate': datetime(*pub[:6]),
                    'description': e.get('description', '') or e.get('summary', ''),
                    'site': e.get('source', {}).get('title') if 'source' in e else '',
                    'thumbnail': ''
                }
                # サムネイル画像の抽出
                if 'media_thumbnail' in e:
                    item['thumbnail'] = e['media_thumbnail'][0]['url']
                elif 'media_content' in e:
                    item['thumbnail'] = e['media_content'][0]['url']
                elif 'enclosures' in e and len(e['enclosures']) > 0:
                    item['thumbnail'] = e['enclosures'][0]['href']

                items.append(item)

    items.sort(key=itemgetter('pubDate'), reverse=True)
    return items[:20]

@app.route("/")
def rss():
    items = fetch_and_sort()
    body = "\n".join(f"""<item>
<title>{i['title']}</title>
<link>{i['link']}</link>
<description><![CDATA[{i['description']}]]></description>
<pubDate>{i['pubDate'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
<source>{i['site']}</source>
<media:thumbnail url="{i['thumbnail']}" />
</item>""" for i in items)
    rss = f"""<?xml version='1.0' encoding='UTF-8'?>
<rss version='2.0' xmlns:media="http://search.yahoo.com/mrss/">
<channel>
<title>Merged RSS</title>
{body}
</channel>
</rss>"""
    return Response(rss, mimetype='text/xml')
