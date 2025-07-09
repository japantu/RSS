from flask import Flask, Response, request
import feedparser
from datetime import datetime
from operator import itemgetter
import re
import html

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
            try:
                pub = e.get('published_parsed') or e.get('updated_parsed')
                if not pub:
                    continue

                desc_html = e.get('description', '') or e.get('summary', '')
                thumbnail = ''

                # 画像抽出（src または data-src に対応、' または " どちらでも可）
                match = re.search(r'<img[^>]+(?:src|data-src)=["\']([^"\']+)["\']', desc_html)
                if match:
                    thumbnail = match.group(1)

                # description に画像がなければ、強制で先頭に追加
                if thumbnail and thumbnail not in desc_html:
                    desc_html = f'<div align="center"><img src="{html.escape(thumbnail)}" /></div><br>' + desc_html

                item = {
                    'title': f"{site_title}閂{e.get('title', '')}",
                    'link': e.get('link', ''),
                    'pubDate': datetime(*pub[:6]),
                    'description': desc_html
                }
                items.append(item)
            except Exception as ex:
                print(f"Error parsing entry: {ex}")
                continue

    items.sort(key=itemgetter('pubDate'), reverse=True)
    return items[:100]

@app.route("/", methods=["GET", "HEAD"])
def rss():
    if request.method == "HEAD":
        return Response("OK", status=200, mimetype="text/plain")

    items = fetch_and_sort()
    body = ""
    for i in items:
        body += f"""<item>
<title>{html.escape(i['title'])}</title>
<link>{html.escape(i['link'])}</link>
<description><![CDATA[{i['description']}]]></description>
<pubDate>{i['pubDate'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
</item>\n"""

    rss = f"""<?xml version='1.0' encoding='UTF-8'?>
<rss version='2.0'>
<channel>
<title>Merged RSS</title>
{body}
</channel>
</rss>"""
    return Response(rss, mimetype='text/xml')
