from flask import Flask, Response, request
import feedparser
from datetime import datetime
from operator import itemgetter
import html

app = Flask(__name__)

RSS_FEEDS = [
    "http://himasoku.com/index.rdf",
    "https://hamusoku.com/index.rdf",
    "http://blog.livedoor.jp/kinisoku/index.rdf",
    "https://www.lifehacker.jp/feed/index.xml",
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

                title = f"{site_title}閂{e.get('title', '')}"
                link = e.get('link', '')
                summary = e.get('summary', '') or e.get('description', '')
                content_encoded = ''

                # content:encoded の抽出（feedparserでは content[0].value に入ってることが多い）
                if 'content' in e and isinstance(e['content'], list) and 'value' in e['content'][0]:
                    content_encoded = e['content'][0]['value']

                item = {
                    'title': title,
                    'link': link,
                    'pubDate': datetime(*pub[:6]),
                    'description': summary,
                    'content': content_encoded
                }
                items.append(item)

            except Exception as ex:
                print(f"Error parsing entry from {url}: {ex}")
                continue

    items.sort(key=lambda x: x['pubDate'], reverse=True)
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
<pubDate>{i['pubDate'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>"""

        if i['content']:
            body += f"\n<content:encoded><![CDATA[{i['content']}]]></content:encoded>"

        body += "\n</item>\n"

    rss = f"""<?xml version='1.0' encoding='UTF-8'?>
<rss version='2.0' xmlns:content="http://purl.org/rss/1.0/modules/content/">
<channel>
<title>Merged RSS</title>
{body}
</channel>
</rss>"""
    return Response(rss, mimetype='text/xml')