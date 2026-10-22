import re,json,urllib.request,urllib.parse,sys,time,unicodedata
sys.path.insert(0,'..')
from cy.songs import S,SIG
UA={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36','Accept-Language':'en-US'}
REP=['topic','vevo','records','netherlands bach','monteverdi','gardiner','bach collegium','bach-archiv','king\'s college','kings college','choir of','philharmonic','symphony','orchestra','smithsonian','folkways','library of congress','harmonia mundi','deutsche grammophon','warner classics','sony classical','decca','erato','naxos','hyperion','tabernacle choir','voces8','stile antico','tenebrae','the sixteen','sacred harp','fisk jubilee','columbia','legacy','rhino','universal','concord','mavis staples','staple singers','hank williams','aretha','atlantic','rca','bbc']
def norm(s): return unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
def search(q):
    s=urllib.request.urlopen(urllib.request.Request('https://www.youtube.com/results?search_query='+urllib.parse.quote_plus(q),headers=UA),timeout=20).read().decode()
    d=json.loads(re.search(r'var ytInitialData = (\{.*?\});</script>',s).group(1)); out=[]
    def walk(o):
        if isinstance(o,dict):
            if 'videoRenderer' in o:
                v=o['videoRenderer'];out.append((v['videoId'],''.join(r['text'] for r in v['title']['runs']),''.join(r['text'] for r in v.get('ownerText',{}).get('runs',[]))))
            for x in o.values(): walk(x)
        elif isinstance(o,list):
            for x in o: walk(x)
    walk(d); return out[:10]
def oembed(vid):
    try: return json.load(urllib.request.urlopen('https://www.youtube.com/oembed?format=json&url='+urllib.parse.quote('https://www.youtube.com/watch?v='+vid),timeout=15))
    except Exception: return None
def pick(song,who):
    q=f'{song} {who}'; key=[w for w in re.findall(r'[a-z]+',norm(song)) if len(w)>3][:3] or re.findall(r'[a-z]+',norm(song))[:1]
    perf=[w for w in re.findall(r'[a-z]+',norm(who)) if len(w)>3 and w not in('hymn','choir','spiritual','chant','gospel','bluegrass','gregorian','messiah','chorale')]
    try: res=search(q)
    except Exception as e: return None,q,str(e)
    for vid,t,ch in res:
        T=norm(t);C=norm(ch)
        if not all(k in T for k in key[:2]): continue
        ok=any(r in C for r in REP) or (perf and any(p in C for p in perf))
        if not ok: continue
        oe=oembed(vid)
        if oe: return vid,q,f'{t} | {ch}'
    return None,q,'no reputable match'
out={}
items=[(k,s,w) for k,v in S.items() for s,w in v]+[('SIG:'+k,s,w) for k,v in SIG.items() for s,w in v]
for k,s,w in items:
    vid,q,info=pick(s,w); out[f'{s}|{w}']={'vid':vid,'q':q,'info':info}
    print('OK ' if vid else '-- ',s,'|',w,'=>',info[:90]); time.sleep(0.4)
json.dump(out,open('yt_links.json','w'),indent=1,ensure_ascii=False)
