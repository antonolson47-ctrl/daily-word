#!/usr/bin/env python3
"""Publish one day's verse to The Daily Word site.
Usage: python3 publish_verse.py NOTE.md IMAGE.png YYYY-MM-DD [--no-push] [--title "Short title"]
Parses the routine's study note, writes content/verses/<date>-<ref>.md, copies the image, rebuilds docs/, commits and pushes."""
import sys, os, re, shutil, subprocess, json
ROOT=os.path.dirname(os.path.abspath(__file__))
def clean(s): return re.sub(r'\*+','',s).strip()
def parse(note):
    L=open(note,encoding='utf-8').read().splitlines()
    head=clean(L[0].lstrip('# ')); m=re.match(r'Verse a Day #(\d+):\s*(.+)',head); num,ref=m.group(1),m.group(2).strip()
    d={'number':num,'ref':ref}; sec=None; S={'scene':[],'keys':[],'align':[],'tidbit':[],'sources':[]}
    for i,raw in enumerate(L[1:],1):
        l=clean(raw)
        if not l: continue
        low=l.lower()
        if low=='setting the scene': sec='scene'; continue
        if low=='key words': sec='keys'; continue
        mm=re.match(r'(Greek|Latin|KJV|ESV|Transliteration)[^:]*:\s*(.+)',l)
        if mm and sec not in ('keys',) or (mm and mm.group(1) in('Greek','Latin','KJV','ESV') and sec!='keys'):
            k={'Greek':'greek','Latin':'latin','KJV':'kjv','ESV':'esv','Transliteration':'translit'}[mm.group(1)]; d[k]=mm.group(2); sec=None
            if k=='greek' and i+1<len(L) and L[i+1].strip().startswith('*') and not L[i+1].strip().startswith('**'): d['translit']=clean(L[i+1])
            continue
        if raw.strip().startswith('*') and not raw.strip().startswith('**') and 'translit' in d and clean(raw)==d['translit']: continue
        for key,lab in (('align','Alignment'),('tidbit','Tidbit'),('sources','Sources')):
            if low.startswith(lab.lower()):
                sec=key; l=re.sub(r'^[^:]*:\s*','',l,count=1) if key!='align' else re.sub(r'^Alignment( rating)?:\s*','',l); break
        if sec: S[sec].append(l)
    al=' '.join(S['align']); d['alignment']=re.split(r'[.!]',al)[0].strip()
    return d,S,al
def to_md(d,S,al,date,image,title):
    book=re.match(r'((?:\d )?[A-Za-z ]+?) \d',d['ref']).group(1)
    fm={'date':date,'number':d['number'],'ref':d['ref'],'book':book,'title':title,'greek':d['greek'],'translit':d.get('translit',''),'latin':d['latin'],'kjv':d['kjv'],'esv':d['esv'],'alignment':d['alignment'],'image':image,'verse_count':'1'}
    out='---\n'+''.join(f'{k}: {v}\n' for k,v in fm.items())+'---\n'
    if S['scene']: out+='## Setting the scene\n\n'+'\n\n'.join(S['scene'])+'\n\n'
    out+='<!--texts-->\n## Key words\n\n'+'\n'.join('- '+re.sub(r'^(.+?\.)\s',r'**\1** ',re.sub(r'^[•\-]\s*','',k),count=1) for k in S['keys'])+'\n\n'
    out+='## Alignment\n\n'+al+'\n\n## The story\n\n'+' '.join(S['tidbit'])+'\n\n## Sources\n\n'+' '.join(S['sources'])+'\n'
    return out
def main():
    a=sys.argv[1:]; push='--no-push' not in a; a=[x for x in a if x!='--no-push']
    title=''
    if '--title' in a: i=a.index('--title'); title=a[i+1]; del a[i:i+2]
    note,img,date=a
    d,S,al=parse(note)
    slug=f"{date}-{re.sub(r'[^a-z0-9]+','-',d['ref'].lower()).strip('-')}"
    imgname=f'{date}.png'; shutil.copy(img,os.path.join(ROOT,'static/img/verses',imgname))
    open(os.path.join(ROOT,'content/verses',slug+'.md'),'w',encoding='utf-8').write(to_md(d,S,al,date,imgname,title or d['ref']))
    subprocess.run([sys.executable,os.path.join(ROOT,'build.py')],check=True)
    url=f'https://antonolson47-ctrl.github.io/daily-word/verses/{slug}/'
    if push:
        g=lambda *c: subprocess.run(['git','-C',ROOT,*c],check=True)
        g('add','-A'); g('commit','-q','-m',f'Verse {date}: {d["ref"]}'); g('push','-q','origin','main')
    print('PUBLISHED' if push else 'BUILT', url)
if __name__=='__main__': main()
