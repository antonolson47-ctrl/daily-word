#!/usr/bin/env python3
"""Build The Daily Word static site: content/ -> docs/ (served by GitHub Pages from main:/docs)."""
import os, re, json, shutil, html, sys, datetime
import markdown
ROOT=os.path.dirname(os.path.abspath(__file__)); C=os.path.join(ROOT,'content'); OUT=os.path.join(ROOT,'docs')
BASE='/daily-word'
def md(t): return markdown.markdown(t,extensions=['tables','md_in_html'])
def load(p):
    s=open(p,encoding='utf-8').read(); meta={}
    if s.startswith('---'):
        _,fm,s=s.split('---',2)
        for l in fm.strip().splitlines():
            if ':' in l:
                k,v=l.split(':',1); v=v.strip()
                if v.startswith('[') or v.startswith('{'): v=json.loads(v)
                meta[k.strip()]=v
    return meta,s.strip()
SUB='<div class=sub><h2 style="border:0;margin-top:0">✉ Get the Daily Word by email (free)</h2><p class=src>One New Testament verse each morning, with the scene, the Greek, Latin and English, and a story.</p><iframe src="https://dailywordptl.substack.com/embed" title="Subscribe to The Daily Word on Substack" loading=lazy frameborder=0 scrolling=no></iframe><p style="text-align:center;margin:6px 0 10px"><a class=subbtn href="https://dailywordptl.substack.com/subscribe">Subscribe on Substack →</a></p></div>'
def page(title,body,desc='',hero=None):
    return f'''<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · The Daily Word</title><meta name=description content="{html.escape(desc)}">
<link rel=preconnect href=https://fonts.googleapis.com><link href="https://fonts.googleapis.com/css2?family=Noto+Serif:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel=stylesheet>
<link rel=stylesheet href="{BASE}/static/style.css"></head><body>
<div class=bar><a href="{BASE}/"><b>✠ The Daily Word</b></a><button class=menu aria-label=Menu onclick="document.querySelector('.bar nav').classList.toggle('open')">☰</button>
<nav><a href="{BASE}/verses/">Verses</a><a href="{BASE}/pilgrimage/">Pilgrimage</a><a href="{BASE}/pilgrimage/st-michael/">St Michael</a><a href="{BASE}/saints/">Saints</a><a href="{BASE}/gallery/">Gallery</a><a href="{BASE}/about/">About</a><a class=subnav href="https://dailywordptl.substack.com/subscribe">Subscribe</a></nav></div>
<main>{body}</main><script src="{BASE}/static/rotate.js"></script><footer>The Daily Word · Scripture quotations marked ESV are from the ESV® Bible (The Holy Bible, English Standard Version®), © 2001 by Crossway, a publishing ministry of Good News Publishers. Used by permission. All rights reserved.<br>Greek: SBL Greek New Testament (SBLGNT), © 2010 Society of Biblical Literature and Logos Bible Software. KJV and Vulgate: public domain.<br>Travel facts change. Always confirm before you go.</footer></body></html>'''
def write(rel,h):
    p=os.path.join(OUT,rel.strip('/'),'index.html'); os.makedirs(os.path.dirname(p),exist_ok=True); open(p,'w',encoding='utf-8').write(h)
def art(name):
    n=name.rsplit('.',1)[0] if name else None
    return n if n and os.path.exists(os.path.join(ROOT,'static/art',n+'.jpg')) else None
def bg(n,shade='linear-gradient(#0000 40%,#000a)'):
    j=f'{BASE}/static/art/{n}.jpg'; w=f'{BASE}/static/art/{n}.webp'
    return f'background-image:{shade},url({j});background-image:{shade},image-set(url({w}) type("image/webp"),url({j}) type("image/jpeg"))'
def hero(meta,title,sub='',rotate=None):
    n=art(meta.get('hero')); st=f' style=\'{bg(n)}\'' if n else ''
    rot=''
    if rotate:
        rot=' data-rotate=\''+json.dumps([bg(x) for x in rotate])+'\''
    return f'<div class="hero tall"{st}{rot}>{html.escape(title)}<small>{html.escape(sub)}</small></div>'
def band(n,cap):
    return f'<figure class=band><picture><source srcset="{BASE}/static/art/{n}-600.webp 600w,{BASE}/static/art/{n}.webp 1280w" sizes="(max-width:760px) 100vw,760px" type=image/webp><img src="{BASE}/static/art/{n}.jpg" alt="{html.escape(cap)}" loading=lazy></picture><figcaption>{html.escape(cap)} · <a href="{BASE}/gallery/">Gallery</a></figcaption></figure>'
GALLERY=[('last-supper','The Last Supper','after Leonardo da Vinci'),('sermon-on-the-mount','The Sermon on the Mount','after Carl Bloch'),('calling-fishermen','The Calling of the Fishermen','in the manner of the Old Masters'),('pieta','Pietà','after Michelangelo\'s statue in St Peter\'s'),('st-michael-dragon','St Michael Defeating the Dragon','after Raphael and Guido Reni'),('pilgrim-camino','A Pilgrim at Sunrise near Santiago','in the classical landscape tradition'),('mont-saint-michel','Mont-Saint-Michel at Tide','after J. M. W. Turner'),('skellig-michael','Skellig Michael','in the Romantic tradition')]
def verified(meta,rel):
    if 'last_verified' not in meta: sys.exit(f'ERROR: {rel} missing last_verified')
    return f'<p class=src><b>Last verified:</b> {meta["last_verified"]}. Prices, hours and rules change: confirm with the official source before you go.</p>'

def build():
    if os.path.exists(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT); shutil.copytree(os.path.join(ROOT,'static'),os.path.join(OUT,'static'))
    open(os.path.join(OUT,'.nojekyll'),'w').close()
    # ---- verses
    vs=[]
    for f in sorted(os.listdir(os.path.join(C,'verses'))):
        if f.endswith('.md'):
            m,b=load(os.path.join(C,'verses',f)); m['slug']=f[:-3]; m['body']=b; vs.append(m)
    vs.sort(key=lambda m:m['date'])
    esv=sum(int(m.get('verse_count',1)) for m in vs)
    for i,m in enumerate(vs):
        rows=f'''<div class=card><div class=row><div class=k>Greek · SBLGNT</div><div class=gr>{html.escape(m['greek'])}</div><div class=it>{html.escape(m.get('translit',''))}</div></div>
<div class=row><div class=k>Latin · Vulgate</div>{html.escape(m['latin'])}</div><div class=row><div class=k>KJV</div>{html.escape(m['kjv'])}</div><div class=row><div class=k>ESV</div>{html.escape(m['esv'])}</div></div>'''
        nav=[]
        if i>0: nav.append(f'<a href="{BASE}/verses/{vs[i-1]["slug"]}/">← {vs[i-1]["ref"]}</a>')
        nav.append(f'<a href="{BASE}/verses/">Archive</a>')
        if i<len(vs)-1: nav.append(f'<a href="{BASE}/verses/{vs[i+1]["slug"]}/">{vs[i+1]["ref"]} →</a>')
        d=datetime.date.fromisoformat(m['date'])
        body=(hero(m,m['ref'],m.get('title','')) if m.get('hero') else '')+f'''<div class=k>Verse a Day #{m['number']} · {d:%B} {d.day}, {d.year}</div><h1>{m['ref']}</h1><span class=badge>Alignment: {html.escape(m.get('alignment','—'))}</span>
<img class=v style="margin-top:12px" src="{BASE}/static/img/verses/{m['image']}" alt="{m['ref']} in Greek, Latin and English">
{md(m['body'].split('<!--texts-->')[0])}{band('calling-fishermen','The Calling of the Fishermen')}<h2>Four witnesses</h2>{rows}{md(m['body'].split('<!--texts-->')[1]) if '<!--texts-->' in m['body'] else ''}{band('pieta','Pietà, after Michelangelo')}<p class=src>{' &nbsp;·&nbsp; '.join(nav)}</p>'''+SUB
        write(f'verses/{m["slug"]}',page(m['ref'],body,m.get('title','')))
    def vcard(m): return f'<a class=card href="{BASE}/verses/{m["slug"]}/" data-s="{html.escape((m["ref"]+" "+m.get("title","")+" "+m["book"]).lower())}">{m["date"][5:].replace("-","/")} · <b>{m["ref"]}</b> — {html.escape(m.get("title",""))} <span class=badge style=float:right>{html.escape(m.get("alignment","").split(".")[0].split(",")[0][:18])}</span></a>'
    books=sorted({m['book'] for m in vs})
    arch=f'''{hero({'hero':'sermon-on-the-mount'},'Verse Archive','One New Testament verse a day, in Greek, Latin and English')}<input id=q placeholder="Search verses (e.g. kingdom, John)" oninput="for(const c of document.querySelectorAll('.cards .card'))c.style.display=c.dataset.s.includes(this.value.toLowerCase())?'':'none'">
<p class=src>Books: {' · '.join(books)}</p><div class=cards>{''.join(vcard(m) for m in reversed(vs))}</div>'''
    write('verses',page('Verse Archive',arch))
    # ---- wiki pages
    roads=json.load(open(os.path.join(C,'pilgrimage','roads.json')))
    for sec,url,top in [('pilgrimage/camino','pilgrimage/camino',('Pilgrimage','pilgrimage')),('pilgrimage/st-michael','pilgrimage/st-michael',('Pilgrimage','pilgrimage')),('saints','saints',('Home',''))]:
        d=os.path.join(C,sec); items=[]
        for f in sorted(os.listdir(d)):
            if not f.endswith('.md'): continue
            m,b=load(os.path.join(d,f)); slug=f[:-3]; m['slug']=slug; items.append((m,b))
        idx=[x for x in items if x[0]['slug']=='index'][0]; subs=sorted([x for x in items if x[0]['slug']!='index'],key=lambda x:int(x[0].get('order',99)))
        secname=idx[0]['title']
        for m,b in subs:
            crumb=f'<div class=crumb><a href="{BASE}/{top[1]}/">{top[0]}</a> › <a href="{BASE}/{url}/">{secname}</a></div>'.replace('//"','/"')
            facts=''
            if m.get('facts'): facts='<div class="facts'+(' long' if max(len(v) for v in m['facts'].values())>22 else '')+'">'+''.join(f'<div>{html.escape(k)}<b>{html.escape(v)}</b></div>' for k,v in m['facts'].items())+'</div>'
            write(f'{url}/{m["slug"]}',page(m['title'],crumb+hero(m,m['title'],m.get('subtitle',''))+facts+md(b)+verified(m,m['slug']),m.get('subtitle','')))
        groups={}
        for m,b in subs: groups.setdefault(m.get('group','Pages'),[]).append(m)
        lists=''.join(f'<h2>{g}</h2><div class=cards>'+''.join(f'<a class=card href="{BASE}/{url}/{m["slug"]}/"><b>{html.escape(m["title"])}</b><br><span class=src>{html.escape(m.get("subtitle",""))}</span></a>' for m in ms)+'</div>' for g,ms in groups.items())
        m,b=idx; parts=b.split('<!--list-->')
        write(url,page(m['title'],f'<div class=crumb><a href="{BASE}/{top[1]}/">{top[0]}</a></div>'.replace('//"','/"')+hero(m,m['title'],m.get('subtitle',''))+md(parts[0])+lists+(md(parts[1]) if len(parts)>1 else '')+verified(m,sec),m.get('subtitle','')))
    m,b=load(os.path.join(C,'pilgrimage','index.md'))
    cards=''.join(f'<a class="card{"" if r["status"]=="live" else " soon"}" href="{BASE}/pilgrimage/{r["id"]}/"><b>{r["name"]}</b><br><span class=src>{r["summary"]}</span></a>' if r['status']=='live' else f'<div class="card soon"><b>{r["name"]}</b> <span class=badge>Coming soon</span><br><span class=src>{r["summary"]}</span></div>' for r in roads)
    write('pilgrimage',page('Pilgrimage Roads',hero(m,m['title'],m.get('subtitle',''))+md(b)+'<div class=cards>'+cards+'</div>'))
    g=''.join(f'<figure class=gal><picture><source srcset="{BASE}/static/art/{n}.webp" type=image/webp><img src="{BASE}/static/art/{n}.jpg" alt="{t}" loading=lazy></picture><figcaption><b>{t}</b><br><span class=src>{by}</span></figcaption></figure>' for n,t,by in GALLERY if art(n))
    write('gallery',page('Gallery','<h1>Gallery</h1><p>Original paintings made for The Daily Word. They are new adaptations inspired by the Old Masters (da Vinci, Michelangelo, Raphael, Guido Reni, Carl Bloch and Turner), not copies of their works.</p>'+g))
    # ---- about
    m,b=load(os.path.join(C,'about.md')); b=b.replace('{{ESV_COUNT}}',str(esv))
    write('about',page('About',f'<h1>{m["title"]}</h1>'+md(b)+SUB))
    # ---- home
    t=vs[-1]; scene=re.search(r'## Setting the scene\s+(.+?)(\n\n|$)',t['body'],re.S)
    ex=(scene.group(1)[:260].rsplit(' ',1)[0]+'…') if scene else t.get('title','')
    hm,hb=load(os.path.join(C,'home.md'))
    d=datetime.date.fromisoformat(t['date'])
    home=hero(hm,hm['title'],hm.get('subtitle',''),rotate=['last-supper','sermon-on-the-mount','calling-fishermen'])+f'''<div class=k>{d:%A, %B} {d.day} · Day {t['number']}</div><h1>{html.escape(t.get('title',''))}</h1><div class=it>{t['ref']}</div>
<div class=card><a href="{BASE}/verses/{t['slug']}/"><img class=v src="{BASE}/static/img/verses/{t['image']}" alt="{t['ref']}"></a><p style="margin:.6em 0 0">{html.escape(ex)} <a href="{BASE}/verses/{t['slug']}/">Read today's verse →</a></p></div>
'''+SUB+f'''<h2>Recent verses</h2><div class=cards>{''.join(vcard(m) for m in list(reversed(vs))[1:4])}</div><p><a href="{BASE}/verses/">All verses →</a></p>
<h2>Explore</h2><div class=doors><a class=door href="{BASE}/pilgrimage/">🥾 Pilgrimage Roads<small>Camino de Santiago & more</small></a><a class=door href="{BASE}/pilgrimage/st-michael/">⚔ St Michael's Line<small>Seven sanctuaries, Ireland to Carmel</small></a><a class=door href="{BASE}/saints/" style="grid-column:1/-1">✨ Saints<small>Lives, miracles, feast days & trivia</small></a></div>'''+md(hb)
    write('',page('Home',home,'A New Testament verse each day in Greek, Latin and English, plus pilgrimage guides.'))
    open(os.path.join(OUT,'404.html'),'w').write(page('Not found','<h1>Page not found</h1><p><a href="/daily-word/">Home</a></p>'))
    print(f'built {len(vs)} verses; ESV verses quoted: {esv}/500')
    if esv>=450: print('WARNING: approaching Crossway 500-verse limit; plan the switch to NRSV/BSB/WEB')
if __name__=='__main__': build()
