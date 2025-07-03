from flask import Flask, Response
import feedparser
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)

RSS_FEEDS = [
    "http://himasoku.com/index.rdf",
    "https://hamusoku.com/index.rdf",
    "https://news4vip.livedoor.biz/index.rdf",
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
                items.append({
                    'title': e.title,
                    'link': e.link,
                    'pubDate': datetime(*pub[:6])
                })
    items.sort(key=itemgetter('pubDate'), reverse=True)
    return items[:20]

@app.route("/")
def rss():
    items = fetch_and_sort()
    body = "\n".join(f"""<item>
<title>{i['title']}</title>
<link>{i['link']}</link>
<pubDate>{i['pubDate'].strftime('%a, %d %b %Y %H:%M:%S +0000')}</pubDate>
</item>""" for i in items)
    rss = f"<?xml version='1.0' encoding='UTF-8'?><rss version='2.0'><channel><title>Merged RSS</title>{body}</channel></rss>"
    return Response(rss, mimetype='application/rss+xml')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
