import os,json
def explore(ROOT,C,nverses):
    nsaints=len([f for f in os.listdir(os.path.join(C,'saints')) if f.endswith('.md') and f!='index.md'])
    roads=[r for r in json.load(open(os.path.join(C,'pilgrimage','roads.json'))) if r['status']=='live']
    nroutes=sum(1 for dp,_,fs in os.walk(os.path.join(C,'pilgrimage')) for f in fs if f.endswith('.md') and f!='index.md')
    ics=open(os.path.join(ROOT,'docs','church-year.ics')).read().count('BEGIN:VEVENT') if os.path.exists(os.path.join(ROOT,'docs','church-year.ics')) else 0
    rl=' · '.join(f'<a href="/pilgrimage/{r["id"]}/">{r["name"]}</a>' for r in roads)
    def card(img,icon,grad,tag,title,blurb,count,btn,href,extra=''):
        top=(f'<picture><source srcset="/static/art/{img}-600.webp" type=image/webp><img src="/static/art/{img}.jpg" alt="" loading=lazy width=600 height=338></picture>' if img else f'<div class=fx-icon style="background:{grad}">{icon}</div>')
        return f'<article class=fx>{top}<div class=fx-b>{f"<span class=fx-tag>{tag}</span>" if tag else ""}<h3>{title}</h3><p>{blurb}</p>{extra}{f"<div class=fx-n>{count}</div>" if count else ""}<a class=fx-btn href="{href}">{btn} →</a></div></article>'
    cards=[
     card('sermon-on-the-mount','','', '', 'Verse of the Day','One New Testament verse each morning in Greek, Latin and English, with the scene, key words, a story and Dig Deeper notes.',f'{nverses} verses so far','Browse the archive','/verses/'),
     card(None,'⛪','conic-gradient(#5b3f8c 0 8%,#e9d9a6 0 12%,#3f7d4a 0 22%,#4a2f6e 0 34%,#9b1c1c 0 36%,#f3e7b4 0 50%,#c4291c 0 52%,#2f6b3a 0)','New','The Church Year','Advent to Pentecost: the history and meaning of every season, its colours, and its Sunday readings for Catholics and Lutherans.','8 seasons · Year B','Open the Church Year','/church-year/','<div class="cybox fx-cy" data-cy></div>'),
     card('st-mary','','','Advent starts Nov 29','Advent Meditations','A meditation for each of the four Sundays and every weekday from Nov 29 to Dec 24, with the day\'s readings.','27 meditations','Start Advent','/church-year/meditations/advent/'),
     card('pieta','','','','Saints','Lives, miracles, feast days and trivia, sourced and fact-checked, with legend clearly marked as legend.',f'{nsaints} saints','Meet the saints','/saints/'),
     card('pilgrim-camino','','','','Pilgrimage Roads','Stage-by-stage guides: the Camino Francés, Portugués, Norte and more, plus Rome\'s Seven Churches, St Paul, St Olav and others.',f'{len(roads)} pilgrimages · {nroutes} guide pages','Choose a road','/pilgrimage/',f'<p class=fx-list>{rl}</p>'),
     card(None,'🎵','linear-gradient(135deg,#3b2a1a,#7a4b22 55%,#b8863b)','','Music of the Church Year','Bach and Handel, spirituals, holy blues, gospel and Appalachian hymns, paired with each season and with free listening links.','23 artist profiles','Listen','/music/'),
     card('st-michael-dragon','','','','Feast Days','The year\'s feasts and holy days, with each saint linked to their page in the Saints wiki.','80+ feasts','See the feasts','/church-year/feasts/'),
     card(None,'📅','linear-gradient(135deg,#2f6b3a,#5b3f8c)','','Church Year Calendar','Add every season, Sunday reading and feast to Google, Apple or Outlook in one tap. It keeps itself up to date.',(f'{ics} events' if ics else '250+ events'),'Add to my calendar','/church-year/calendar/'),
     card(None,'✉️','linear-gradient(135deg,#b8863b,#e9d8ae)','Free','Daily Word by Email','Today\'s verse in your inbox every morning, through Substack.','','Subscribe','https://dailywordptl.substack.com/subscribe'),
    ]
    return '<section class=explore id=explore><h2>Explore the Daily Word</h2><p class=fx-intro>Much more than a daily verse: the whole Church year, a growing saints wiki, pilgrimage guides and sacred music, all sourced and free.</p><div class=fx-grid>'+''.join(cards)+'</div></section>'
