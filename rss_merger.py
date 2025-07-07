from flask import Flask, Response
import feedparser
from datetime import datetime
from operator import itemgetter
import re

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
        site_title = feed.feed.get('title', '')
        for e in feed.entries:
            pub = e.get('published_parsed') or e.get('updated_parsed')
            if pub:
                # descriptionと画像の抽出
                desc_html = e.get('description', '') or e.get('summary', '')
                thumbnail = ''

                # 優先：media_thumbnail, media_content, enclosures
                if 'media_thumbnail' in e:
                    thumbnail = e['media_thumbnail'][0]['url']
                elif 'media_content' in e:
                    thumbnail = e['media_content'][0]['url']
                elif 'enclosures' in e and len(e['enclosures']) > 0:
                    thumbnail = e['enclosures'][0]['href']
                else:
                    # 最後の手段：description内の<img src="..."> を抽出
                    match = re.search(r'<img[^>]+src="([^"]+)"', desc_html)
                    if match:
                        thumbnail = match.group(1)

                item = {
                    'title': f"{site_title}閂{e.get('title', '')}",
                    'link': e.get('link', ''),
                    'pubDate': datetime(*pub[:6]),
                    'description': desc_html,
                    'thumbnail': thumbnail
                }
                items.append(item)

    items.sort(key=itemgetter('pubDate'), reverse=True)
    return items[:100]  # 最大50件まで

@app.route("/")
def rss():
    items = fetch_and_sort()
    body = "\n".join(f"""<item>
<title>{i['title']}</title>
<link>{i['link']}</link>
<desc><![CDATA[{i['description']}]]></desc>
<pubDate>{i['pubDate'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
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
