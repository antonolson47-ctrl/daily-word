import os, json, html, math, datetime as dt, urllib.parse
from .seasons import SEASONS
from .music import A, M, CLASSICAL, LINEAGE, APPAL
from .advent import SUNDAYS, DAILY
from .cal import FIXED, YB, easter, advent1
from .songs import S as SONGS, SIG
YT=json.load(open(os.path.join(os.path.dirname(__file__),'yt_links.json')))
STATS={'specific':set(),'search':set()}
def listen(song,who):
    k=f'{song}|{who}'; r=YT.get(k,{})
    if r.get('url'): STATS['specific'].add(k); u=r['url']
    elif r.get('vid'): STATS['specific'].add(k); u='https://www.youtube.com/watch?v='+r['vid']
    else: STATS['search'].add(k); u='https://www.youtube.com/results?search_query='+urllib.parse.quote_plus(song+' '+who)
    return f'<a class=listen href="{u}">🎧 {E(song)}</a>'
E=html.escape
SITE='https://dailywordptl.com'
ICS_URL=SITE+'/church-year.ics'
SMAP={s['slug']:s for s in SEASONS}
def usccb(d): return f'https://bible.usccb.org/bible/readings/{d[5:7]}{d[8:10]}{d[2:4]}.cfm'
def wheel():
    segs=[(s['slug'],s['name'] if s['slug']!='holy-week' else 'Holy Week',s['color'],s['weeks']) for s in SEASONS]
    tot=sum(w for *_,w in segs); a=-math.pi/2; out=[]; R,r,C=200,95,210
    for slug,name,col,w in segs:
        b=a+2*math.pi*w/tot; large=1 if b-a>math.pi else 0
        p=lambda ang,rad:(C+rad*math.cos(ang),C+rad*math.sin(ang))
        x1,y1=p(a,R);x2,y2=p(b,R);x3,y3=p(b,r);x4,y4=p(a,r)
        d=f'M{x1:.1f},{y1:.1f}A{R},{R} 0 {large} 1 {x2:.1f},{y2:.1f}L{x3:.1f},{y3:.1f}A{r},{r} 0 {large} 0 {x4:.1f},{y4:.1f}Z'
        m=(a+b)/2; lx,ly=p(m,(R+r)/2+ (0 if w>2 else 0))
        dark=' class=dk' if slug in('christmas','easter') else ''
        lbl=name.split(' /')[0].replace('Ordinary Time','Ordinary Time')
        txt=f'<text x="{lx:.0f}" y="{ly:.0f}" text-anchor=middle dominant-baseline=middle{dark}{' style="font-size:10.5px"' if w==2 else ''}>{E(lbl if w>1 else lbl.split()[0])}</text>' if w>2 else ''
        out.append(f'<a href="/church-year/{slug}/" data-s="{slug}" aria-label="{E(name)}"><title>{E(name)}</title><path d="{d}" fill="{col}"/>{txt}</a>')
        a=b
    return f'<svg class=wheel viewBox="0 0 420 420" role=img aria-label="The Church Year wheel">{"".join(out)}<circle cx=210 cy=210 r=92 fill="#fbf5e6"/><text x=210 y=196 text-anchor=middle class=dk style="font-size:15px">The Church Year</text><text x=210 y=218 text-anchor=middle class=dk style="font-size:12px;font-weight:400">Advent 2026 → 2027</text><text x=210 y=238 text-anchor=middle class=dk style="font-size:12px;font-weight:400">Lectionary Year B</text></svg>'
CYBOX='<div class=cybox data-cy><div class=k>This week in the Church Year</div><p>Loading…</p></div>'
def saintlink(slug,name,have):
    return f'<a href="/saints/{slug}/">{E(name)}</a>' if slug and slug in have else E(name)
def photo(k,cred):
    a=A[k]
    if k in cred:
        c=cred[k]; return f'<img src="/static/img/music/{k}.jpg" alt="{E(a[0])}" loading=lazy>',f'<div class=cap>Photo: {E(c["artist"])} · {E(c["lic"])} · <a href="{c["page"]}">Wikimedia Commons</a></div>'
    return '<div class=ph aria-label="No free photo available">♪</div>','<div class=cap>No freely licensed photo found yet.</div>'
def profile(k,cred):
    a=A[k]; img,cap=photo(k,cred)
    return f'<div class="card prof" id="{k}">{img}<div><h3>{E(a[0])}</h3><span class=badge>{E(a[2])}</span> <span class=src>{E(a[1])}</span><div>{a[3]}</div><p class=lrow>Listen: {' '.join(listen(x,y) for x,y in SIG[k])}</p><p class=src>Source: <a href="{a[4][1]}">{E(a[4][0])}</a></p></div>{cap}</div>'
def musicblock(slug,md):
    rows=''
    for t,k,note,links in M[slug]:
        who=f' · <a href="/music/#{k}">{E(A[k][0])}</a>' if k else ''
        ls=' · '.join(f'<a href="{u}">{E(l)}</a>' for l,u in links)
        lis=' '.join(listen(a,b) for a,b in SONGS[t])
        rows+=f'<li><b>{md(t)[3:-4]}</b>{who}<br><span class=src>{md(note)[3:-4]}</span><br><span class=lrow>Listen: {lis}</span><br><span class=src>Also: {ls}</span></li>'
    return f'<h2>🎵 Music for the season</h2><ul>{rows}</ul><p class=src>More history and the full gospel, blues and Appalachian lineage on the <a href="/music/">Music page</a>.</p>'
def build(B,vs):
    md,page,write,hero=B.md,B.page,B.write,B.hero
    have={f[:-3] for f in os.listdir(os.path.join(B.C,'saints'))}
    cred=json.load(open(os.path.join(B.ROOT,'cy','music_credits.json')))
    # ---------- hub
    cards=''.join(f'<a class=card href="/church-year/{s["slug"]}/"><span class=dot style="background:{s["color"]}"></span><b>{s["icon"]} {E(s["name"])}</b><br><span class=src>{E(s["dates"])}</span></a>' for s in SEASONS)
    hub=hero({'hero':'sermon-on-the-mount'},'The Church Year','Seasons, Sundays, feasts, meditations and music')+CYBOX+wheel()+'<p class=src style="text-align:center">'+' · '.join(f'<a href="/church-year/{s["slug"]}/"><span class=dot style="background:{s["color"]};width:10px;height:10px"></span>{E(s["name"].split(" /")[0])}</a>' for s in SEASONS)+'</p><p class=src style="text-align:center">Tap a season. The ring is drawn to scale by weeks; the current season is outlined.</p>'+md('''Christians have marked time by the life of Christ since the first centuries: a weekly Sunday for the Resurrection, a yearly Pascha, and, by the fifth century, a cycle of preparation, feast and ordinary time. The Catechism calls it the year in which "the whole mystery of Christ" unfolds (§1171). Catholics, Lutherans, Anglicans and many other churches share the same shape and, through the lectionary, many of the same Sunday readings.

**Lectionary years:** readings run on a three-year cycle: **A** (Matthew), **B** (Mark), **C** (Luke), with John in all three. The year that begins on **29 November 2026 is Year B**, the year of Mark, for both the Catholic Lectionary and the Revised Common Lectionary.''')+f'<h2>The seasons</h2><div class=cards>{cards}</div>'+f'''<h2>Go deeper</h2><div class=doors><a class=door href="/church-year/meditations/advent/">🕯️ Advent meditations<small>Four Sundays and every day, 29 Nov – 24 Dec 2026</small></a><a class=door href="/church-year/sundays/">📖 Sunday readings<small>Year B, 2026–27, every season</small></a><a class=door href="/church-year/feasts/">✨ Feast days<small>Linked to the Saints wiki</small></a><a class=door href="/church-year/calendar/">📅 Add to your calendar<small>Google, Apple, Outlook, TimeTree</small></a><a class=door href="/music/">🎵 Music of the year<small>Bach to Blind Willie Johnson</small></a><a class=door href="/church-year/through-the-year/">📜 Daily Word through the year<small>Verses by season</small></a></div>'''+md('''## Sources
- [Catechism of the Catholic Church §§1163–1173, "When is the liturgy celebrated?"](https://www.vatican.va/archive/ENG0015/__P39.HTM)
- [USCCB: Liturgical Year and Calendar](https://www.usccb.org/prayer-worship/liturgical-year) · [daily readings](https://bible.usccb.org/)
- [LCMS: The Church Year](https://www.lcms.org/worship/church-year) · [ELCA: Worship](https://www.elca.org/worship)
- [Vanderbilt Divinity Library: Revised Common Lectionary](https://lectionary.library.vanderbilt.edu/)
- [Catholic Encyclopedia (1913): Liturgical Colours](https://www.newadvent.org/cathen/04134a.htm)

<p class=src>Written for The Daily Word: summaries are in our own words, with sources linked. Catholic and Lutheran practice is described as each church describes it.</p>''')
    write('church-year',page('The Church Year',hub,'Advent, Christmas, Epiphany, Lent, Holy Week, Easter, Pentecost and Ordinary Time: history, meaning, readings, feasts and music.'))
    # ---------- season pages
    for i,s in enumerate(SEASONS):
        sund=[y for y in YB if y[2]==s['slug']]
        tbl=''
        if sund: tbl='<h2>Sundays and holy days, 2026–27 (Year B)</h2><div class=tbl><table><tr><th>Date</th><th>Day</th><th>Readings (RCL)</th></tr>'+''.join(f'<tr><td>{dt.date.fromisoformat(d):%a %d %b %Y}</td><td>{E(n)}</td><td>{E(r)}{"<br><span class=src>Catholic: "+E(c)+"</span>" if c else ""}</td></tr>' for d,n,_,r,c in sund)+'</table></div>'
        meds=f'<p><a class=subbtn href="/church-year/meditations/{s["slug"]}/">Meditations for {E(s["name"].split(" /")[0])} →</a></p>'
        prev=SEASONS[i-1]; nxt=SEASONS[(i+1)%len(SEASONS)]
        body=(f'<div class=crumb><a href="/church-year/">Church Year</a></div>'+hero({'hero':'last-supper' if s['slug'] in('lent','holy-week') else 'sermon-on-the-mount'},s['icon']+' '+s['name'],s['dates'])+CYBOX
            +f'<div class="facts long"><div>Liturgical colour<b><span class=dot style="background:{s["color"]}"></span>{E(s["colname"])}</b></div><div>When<b>{E(s["dates"])}</b></div></div>'
            +md('## History\n\n'+s['history']+'\n\n## Why it is observed\n\n'+s['why']+'\n\n## Colours and symbols\n\n'+s['symbols']+'\n\n## Catholic practice\n\n'+s['catholic']+'\n\n## Lutheran practice\n\n'+s['lutheran'])
            +tbl+meds+musicblock(s['slug'],md)+'<h2>Sources</h2><ul>'+''.join(f'<li><a href="{u}">{E(t)}</a></li>' for t,u in s['sources'])+'</ul>'
            +f'<p class=src><a href="/church-year/{prev["slug"]}/">← {E(prev["name"])}</a> · <a href="/church-year/">Church Year</a> · <a href="/church-year/{nxt["slug"]}/">{E(nxt["name"])} →</a></p>')
        write(f'church-year/{s["slug"]}',page(s['name']+' · Church Year',body,f'{s["name"]}: history, meaning, colours, Catholic and Lutheran practice, readings and music.'))
    # ---------- Advent meditations
    dmap={d[0]:d for d in DAILY}
    allds=sorted(set([x[0] for x in SUNDAYS]+[x[0] for x in DAILY]))
    sec=''
    toc=[]
    for d in allds:
        day=dt.date.fromisoformat(d); sn=[x for x in SUNDAYS if x[0]==d]
        if sn:
            _,t,theme,rd,txt=sn[0]
            toc.append(f'<a href="#d{d}"><b>{day:%a %d %b}</b> · {E(t)}</a>')
            sec+=f'<div class="med" id="d{d}" style="border-color:#b8863b"><div class=k>{day:%A, %d %B %Y} · Candle of {theme}</div><h2 style="border:0;margin-top:4px">{E(t)}</h2><p class=src><b>Readings:</b> {E(rd)} · <a href="{usccb(d)}">USCCB</a> · <a href="https://lectionary.library.vanderbilt.edu/">RCL</a></p>{md(txt)}</div>'
            if d=='2026-12-20': continue
        if d in dmap:
            _,t,rd,txt,sl=dmap[d]
            if sn: continue
            toc.append(f'<a href="#d{d}">{day:%a %d %b} · {E(t)}</a>')
            sx=f' · Saint: <a href="/saints/{sl}/">{E(sl.replace("-"," ").title())}</a>' if sl and sl in have else ''
            sec+=f'<div class=med id="d{d}"><div class=k>{day:%A, %d %B %Y}</div><h3 style="margin:4px 0">{E(t)}</h3><p class=src><b>Readings:</b> {E(rd)} · <a href="{usccb(d)}">Full text at USCCB</a>{sx}</p>{md(txt)}</div>'
    adv=(f'<div class=crumb><a href="/church-year/">Church Year</a> › <a href="/church-year/advent/">Advent</a></div>'+hero({'hero':'pilgrim-camino'},'Advent Meditations 2026','Year B · 29 November – 24 December')
        +md('''A meditation for each Sunday of Advent and a short one for every weekday, following the readings of the Catholic weekday lectionary (Lutherans using the RCL daily readings will find the same Sunday texts). Light the wreath candle on Sunday, read the passage, then the meditation. Scripture quotations are from the King James Version (public domain); full readings are linked to the USCCB.''')
        +'<details class=card><summary><b>Jump to a day</b></summary><p style="columns:2;font-size:14px">'+'<br>'.join(toc)+'</p></details>'+sec
        +md('''<p class=src>Meditations written for The Daily Word. Readings: Lectionary for Mass (USCCB) and Revised Common Lectionary (Consultation on Common Texts, via Vanderbilt Divinity Library); the O Antiphons and ERO CRAS from the Roman Breviary tradition.</p>''')+musicblock('advent',md))
    write('church-year/meditations/advent',page('Advent Meditations 2026',adv,'Daily and Sunday Advent meditations for 2026, Year B, with readings.'))
    # scaffolds
    for s in SEASONS:
        if s['slug']=='advent': continue
        sund=[y for y in YB if y[2]==s['slug']]
        rows=''.join(f'<div class=med id="d{d}" style="border-color:{s["color"]}"><div class=k>{dt.date.fromisoformat(d):%A, %d %B %Y}</div><h3 style="margin:4px 0">{E(n)}</h3><p class=src><b>Readings (RCL):</b> {E(r)}{" · <b>Catholic:</b> "+E(c) if c else ""} · <a href="{usccb(d)}">USCCB</a></p><p class=src><i>Meditation coming before this day.</i></p></div>' for d,n,_,r,c in sund) or '<p class=src>Ordinary Time Sundays follow the readings on the <a href="/church-year/sundays/">Sunday readings page</a>; meditations will be added through the year.</p>'
        pace={'lent':'Pacing: one meditation per Sunday plus Ash Wednesday, and daily readings through Lent (planned).','holy-week':'Pacing: daily, Palm Sunday through the Easter Vigil.','easter':'Pacing: Easter Day, each Sunday of Easter and Ascension.','christmas':'Pacing: Christmas Eve, Christmas Day and the Sundays of Christmas, plus the feasts of the Twelve Days.'}.get(s['slug'],'Pacing: one meditation per Sunday and major feast.')
        write(f'church-year/meditations/{s["slug"]}',page(f'{s["name"]} Meditations',f'<div class=crumb><a href="/church-year/">Church Year</a> › <a href="/church-year/{s["slug"]}/">{E(s["name"])}</a></div><h1>{s["icon"]} {E(s["name"])} meditations</h1><p>{pace}</p>'+rows))
    idx=''.join(f'<a class=card href="/church-year/meditations/{s["slug"]}/"><span class=dot style="background:{s["color"]}"></span><b>{E(s["name"])}</b> <span class=badge>{"Ready" if s["slug"]=="advent" else "Readings listed"}</span></a>' for s in SEASONS)
    write('church-year/meditations',page('Meditations',f'<div class=crumb><a href="/church-year/">Church Year</a></div><h1>Meditations through the year</h1><div class=cards>{idx}</div>'))
    # Sunday readings page
    rows=''.join(f'<tr><td>{dt.date.fromisoformat(d):%d %b %Y}</td><td><a href="/church-year/meditations/{sl}/#d{d}">{E(n)}</a></td><td>{E(r)}{"<br><span class=src>Catholic: "+E(c)+"</span>" if c else ""}</td></tr>' for d,n,sl,r,c in YB)
    write('church-year/sundays',page('Sunday Readings 2026–27',f'<div class=crumb><a href="/church-year/">Church Year</a></div><h1>Sunday readings, 2026–27 (Year B)</h1><p>Revised Common Lectionary (used by the ELCA and many Protestant churches), with Catholic differences noted. Ordinary Time Sundays from June to November follow Mark; see the <a href="https://lectionary.library.vanderbilt.edu/">Vanderbilt RCL</a> or <a href="https://bible.usccb.org/">USCCB</a> for each week. The LCMS three-year lectionary is close but not identical.</p><div class=tbl><table><tr><th>Date</th><th>Day</th><th>Readings</th></tr>{rows}</table></div>'))
    # ---------- feasts
    frows='';missing=[]
    for m,d,n,sl,miss,kind in FIXED:
        day=dt.date(2027 if m<11 else 2026,m,d) if not (m==11 and d<29) else dt.date(2027,m,d)
        link=saintlink(sl,n,have)
        if miss: missing.append((miss,n,f'{d} {dt.date(2000,m,1):%B}'))
        frows+=f'<tr><td>{d} {dt.date(2000,m,1):%b}</td><td>{link}{" <span class=badge>saint page planned</span>" if miss else ""}</td><td class=src>{kind}</td></tr>'
    mov=''.join(f'<li><b>{dt.date.fromisoformat(d):%a %d %b %Y}</b> · <a href="/church-year/{sl}/">{E(n)}</a></li>' for d,n,sl,_,_ in YB if any(w in n for w in('Ash','Palm','Maundy','Good Friday','Easter Sunday','Ascension','Pentecost','Trinity','Christ the King','Baptism','Transfiguration','Epiphany of','Christmas Day','Corpus')))
    write('church-year/feasts',page('Feast Days',f'<div class=crumb><a href="/church-year/">Church Year</a></div><h1>Feast days</h1><h2>Movable feasts, 2026–27</h2><ul>{mov}</ul><p class=src>Easter 2027 is 28 March, so the Annunciation (25 March, Maundy Thursday) moves to Monday 5 April.</p><h2>Fixed feasts and saints</h2><p>Linked names open the saint\'s page on our <a href="/saints/">Saints wiki</a>. Feasts follow the General Roman Calendar, with Lutheran commemorations noted.</p><div class=tbl><table><tr><th>Date</th><th>Feast</th><th>Rank</th></tr>{frows}</table></div>'))
    # ---------- ICS
    ev=[]
    def add(d,summary,desc,url):
        ev.append((d,summary,desc,url))
    for d,n,sl,r,c in YB: add(dt.date.fromisoformat(d),n,f'Readings: {r}'+(f' | Catholic: {c}' if c else ''),f'{SITE}/church-year/meditations/{sl}/#d{d}')
    for d,t,rd,txt,sl in DAILY:
        if d not in [x[0] for x in YB]: add(dt.date.fromisoformat(d),'Advent: '+t,'Readings: '+rd,f'{SITE}/church-year/meditations/advent/#d{d}')
    for y in (2026,2027,2028):
        for m,d,n,sl,miss,kind in FIXED:
            day=dt.date(y,m,d)
            if dt.date(2026,11,1)<=day<=dt.date(2028,12,31): add(day,n,'Feast day ('+kind+')',f'{SITE}/saints/{sl}/' if sl and sl in have else f'{SITE}/church-year/feasts/')
    # seasons start markers across 2026-2028
    for y in (2026,2027):
        a1=advent1(y);E2=easter(y+1)
        for d,n,sl in [(a1,'Advent begins','advent'),(dt.date(y,12,25),'Christmas season begins','christmas'),(dt.date(y+1,1,6),'Epiphany','epiphany'),(E2-dt.timedelta(46),'Lent begins: Ash Wednesday','lent'),(E2-dt.timedelta(7),'Holy Week begins: Palm Sunday','holy-week'),(E2,'Easter Day','easter'),(E2+dt.timedelta(49),'Day of Pentecost','pentecost'),(E2+dt.timedelta(50),'Season after Pentecost / Ordinary Time','ordinary-time')]:
            add(d,'⛪ '+n,'Season: '+SMAP[sl]['name']+'. Colour: '+SMAP[sl]['colname'],f'{SITE}/church-year/{sl}/')
    esc=lambda s:s.replace('\\','\\\\').replace(';','\\;').replace(',','\\,').replace('\n','\\n')
    def fold(l):
        b=l.encode(); out=[]
        while len(b)>73:
            cut=73
            while (b[cut]&0xC0)==0x80: cut-=1
            out.append(b[:cut].decode()); b=b[cut:]
        out.append(b.decode()); return '\r\n '.join(out)
    L=['BEGIN:VCALENDAR','VERSION:2.0','PRODID:-//The Daily Word//Church Year//EN','CALSCALE:GREGORIAN','METHOD:PUBLISH','X-WR-CALNAME:Church Year · The Daily Word','X-WR-CALDESC:Seasons\\, Sunday readings\\, feast days and meditations from dailywordptl.com','X-WR-TIMEZONE:America/Chicago','REFRESH-INTERVAL;VALUE=DURATION:P1D','X-PUBLISHED-TTL:P1D']
    seen=set()
    for d,s,desc,u in sorted(ev,key=lambda x:x[0]):
        uid=f'{d:%Y%m%d}-{abs(hash(s))%10**8}@dailywordptl.com'
        import hashlib; uid=f'{d:%Y%m%d}-'+hashlib.md5(s.encode()).hexdigest()[:10]+'@dailywordptl.com'
        if uid in seen: continue
        seen.add(uid)
        L+= ['BEGIN:VEVENT',f'UID:{uid}','DTSTAMP:20261022T150000Z',f'DTSTART;VALUE=DATE:{d:%Y%m%d}',f'DTEND;VALUE=DATE:{d+dt.timedelta(1):%Y%m%d}',fold('SUMMARY:'+esc(s)),fold('DESCRIPTION:'+esc(desc+'\n'+u)),fold('URL:'+u),'TRANSP:TRANSPARENT','END:VEVENT']
    L.append('END:VCALENDAR')
    open(os.path.join(B.OUT,'church-year.ics'),'w',encoding='utf-8',newline='').write('\r\n'.join(L)+'\r\n')
    wc='webcal://dailywordptl.com/church-year.ics'
    g='https://calendar.google.com/calendar/r?cid='+urllib.parse.quote(wc,safe='')
    o='https://outlook.live.com/calendar/0/addfromweb?url='+urllib.parse.quote(ICS_URL,safe='')+'&name='+urllib.parse.quote('Church Year · The Daily Word')
    o365='https://outlook.office.com/calendar/0/addfromweb?url='+urllib.parse.quote(ICS_URL,safe='')+'&name='+urllib.parse.quote('Church Year · The Daily Word')
    calp=(f'<div class=crumb><a href="/church-year/">Church Year</a></div><h1>📅 The Church Year in your calendar</h1><p>One free subscription brings in every season change, each Sunday with its readings, the Advent daily readings and the major feast days, each linked back to its meditation or saint page. It updates itself as we add meditations. ({len(seen)} events, Advent 2026 to the end of 2028.)</p>'
        f'<div class=btns id=calbtns><a href="{g}">Add to Google Calendar</a><a href="{wc}">Add to Apple Calendar</a><a href="{o}">Add to Outlook.com</a><a href="{o365}">Outlook (work/school)</a><a href="/church-year.ics" download>Download .ics</a></div>'
        f'<p><b>Feed URL</b> (paste into any calendar app\'s "subscribe by URL"):<br><input id=q readonly value="{ICS_URL}" onclick="this.select()"></p>'
        +md('''## TimeTree
TimeTree does not subscribe to calendar feed URLs directly, but it can show calendars from your phone. The easy way:

1. Subscribe with **Add to Google Calendar** (Android) or **Add to Apple Calendar** (iPhone) above.
2. In TimeTree, open **Settings › Calendar sync** (or "Show phone calendars") and switch on *Church Year · The Daily Word*.

The events then appear in your TimeTree view alongside the family calendar.

## Tips
- On iPhone, "Add to Apple Calendar" opens a subscribe prompt; tap **Subscribe**.
- Google refreshes subscribed calendars every few hours; Apple lets you choose the refresh interval.
- To remove it, unsubscribe in your calendar app. Nothing is sent to us.'''))
    write('church-year/calendar',page('Church Year Calendar',calp,'Subscribe to the Church Year in Google, Apple or Outlook calendar.'))
    # ---------- music page
    def lin(keys): return ''.join(profile(k,cred) for k in keys)
    pair=''.join(f'<h3><span class=dot style="background:{s["color"]}"></span><a href="/church-year/{s["slug"]}/">{E(s["name"])}</a></h3>'+musicblock(s['slug'],md).split('</h2>',1)[1].rsplit('<p class=src>',1)[0] for s in SEASONS)
    mus=(hero({'hero':'calling-fishermen'},'Music of the Church Year','Bach and Handel, spirituals, holy blues, gospel and mountain hymns')
        +md('''Every season of the Church year has its music, and Christian music in America has come down several streams that keep meeting. Handel and Bach wrote for the liturgy of their own churches. African Americans made the **spirituals** from the Bible stories they heard, hiding hope of freedom inside the Exodus and the Cross. From the spirituals and the work songs came both the **blues** and **gospel**: the same flattened "blue" notes, the same call and response, the same moan, one sung on Saturday night and one on Sunday morning. Many blues singers were preachers' sons or preachers themselves, and the father of gospel, Thomas A. Dorsey, had been a blues pianist. Meanwhile, in the Appalachian hills, **shape-note** singing and mountain hymns became **country gospel** and **bluegrass**, and these streams crossed again and again, as when a Black guitarist named Lesley Riddle taught the Carter Family his songs. All of it, from Leipzig to Clarksdale to Clinch Mountain, sings the same Scriptures.''')
        +'<p class=src>Jump to: <a href="#season">By season</a> · <a href="#classical">Classical</a> · <a href="#lineage">Spirituals → blues → gospel</a> · <a href="#appalachia">Appalachian &amp; country gospel</a> · <a href="#roots">Why gospel and blues share roots</a></p>'
        +f'<h2 id=season>Listening by season</h2>{pair}'
        +'<h2 id=classical>The classical masters</h2>'+lin(CLASSICAL)
        +'<h2 id=lineage>From the spirituals to gospel</h2><div class=lin>'+md('''**1. Spirituals (18th–19th centuries).** Sung in slavery and carried to the world by the Fisk Jubilee Singers from 1871. Songs like *Go Down, Moses* and *Steal Away* were prayers and, sometimes, coded escape plans.''')+lin(['fisk','anderson'])
        +md('''**2. Holy blues (1920s–30s).** Street evangelists with guitars took the blues form and filled it with Scripture. Record companies sold them on the same "race records" as secular blues.''')+lin(['bwj','davis','house'])
        +md('''**3. The birth of gospel (1930s).** Thomas A. Dorsey brought blues piano and feeling into the Black church in Chicago and organised the first gospel choirs and conventions. Sister Rosetta Tharpe took it onto the radio and into the nightclubs; Mahalia Jackson made it the voice of a nation.''')+lin(['dorsey','tharpe','mahalia'])
        +md('''**4. The quartets (1930s–50s).** Four or five men in sharp suits, unaccompanied or with one guitar, singing "hard gospel" on Sunday afternoon programs across the South.''')+lin(['dixie','soulstirrers'])
        +md('''**5. Gospel into soul (1950s–70s).** Church-raised singers carried gospel into soul music and the civil-rights movement, and some came back to make the greatest gospel records of all.''')+lin(['aretha','staples'])+'</div>'
        +'<h2 id=appalachia>Appalachian, bluegrass and early country gospel</h2><div class=lin>'+md('''In the mountains of Virginia, Kentucky, Tennessee and North Carolina, Scots-Irish ballads met Baptist and Methodist hymnody. Shape-note tunebooks taught whole congregations to sing in rough four-part harmony; Primitive Baptists "lined out" psalms, a leader singing each line for the church to echo, a practice also kept in Black churches. When the radio and record business arrived in the 1920s, these songs became country and later bluegrass, and every major act kept a gospel set.

**Where the streams crossed:** A. P. Carter collected songs with **Lesley Riddle**, a Black guitarist who remembered the tunes and taught Maybelle his picking. Bill Monroe learned the blues from **Arnold Shultz**, a Black fiddler in Kentucky. Hank Williams credited **Rufus "Tee-Tot" Payne**. The "high lonesome" sound and the blues moan answer each other.''')+lin(APPAL)+'</div>'
        +'<h2 id=roots>Why gospel and blues share the same roots</h2>'+md('''- **Same source.** Both grew from the spirituals, field hollers and ring shouts of enslaved Africans in the American South, with their call and response, bent "blue" notes and rhythmic drive.
- **Same musicians.** Thomas A. Dorsey played blues as "Georgia Tom" before writing *Precious Lord*. Son House preached before he sang blues; Rev. Gary Davis sang blues before he preached. Sister Rosetta Tharpe played the same guitar in church and in clubs.
- **Same subject, different answer.** The blues names suffering honestly, with no resolution; gospel names the same suffering and answers it with the Cross and the Resurrection. Dorsey said gospel was "good news" sung with the feeling of the blues.
- **Same Scriptures.** The Psalms of lament (Psalm 22, 88, 130) sit in the Bible alongside the Psalms of praise. Lent and Holy Week give the Church its "blues"; Easter its gospel.

Mahalia Jackson put it plainly: "Blues are the songs of despair, but gospel songs are the songs of hope." Both are honest prayer.''')
        +md('''## Sources and listening
- Library of Congress, [National Jukebox](https://www.loc.gov/collections/national-jukebox/) and [audio collections](https://www.loc.gov/audio/)
- [Internet Archive, 78rpm and LP collections](https://archive.org/details/georgeblood)
- Smithsonian Folkways, [Sacred Harp and African American gospel recordings](https://folkways.si.edu/)
- Biographical facts from the Library of Congress, Rock & Roll and Country Music Halls of Fame, and the Catholic Encyclopedia (1913) for church history.

<p class=src>Listening links go to the Internet Archive, the Library of Congress and Spotify/YouTube searches. Photos are public domain or freely licensed, credited under each one.</p>'''))
    write('music',page('Music of the Church Year',mus,'Classical, spirituals, holy blues, gospel and Appalachian gospel for every season of the Church year.'))
    # ---------- through the year archive
    def season_of(d):
        y=d.year; a1=advent1(y)
        if d<a1: y-=1; a1=advent1(y)
        E2=easter(y+1)
        for lim,s in [(dt.date(y,12,25),'advent'),(dt.date(y+1,1,6),'christmas'),(E2-dt.timedelta(46),'epiphany'),(E2-dt.timedelta(7),'lent'),(E2,'holy-week'),(E2+dt.timedelta(49),'easter'),(E2+dt.timedelta(56),'pentecost')]:
            if d<lim: return s
        return 'ordinary-time'
    grp={}
    for m in vs: grp.setdefault(season_of(dt.date.fromisoformat(m['date'])),[]).append(m)
    arch=''.join(f'<h2><span class=dot style="background:{s["color"]}"></span>{E(s["name"])}</h2>'+(('<div class=cards>'+''.join(f'<a class=card href="/verses/{m["slug"]}/">{m["date"]} · <b>{E(m["ref"])}</b> — {E(m.get("title",""))}</a>' for m in reversed(grp[s['slug']]))+'</div>') if s['slug'] in grp else '<p class=src>Verses will appear here when this season comes round.</p>') for s in SEASONS)
    write('church-year/through-the-year',page('Daily Word through the Year',f'<div class=crumb><a href="/church-year/">Church Year</a></div><h1>📜 The Daily Word through the year</h1><p>Every daily verse, sorted by the season of the Church year in which it was published. The Daily Word began on 12 October 2026, in the season after Pentecost; Advent begins on 29 November.</p>'+arch))
    return missing
