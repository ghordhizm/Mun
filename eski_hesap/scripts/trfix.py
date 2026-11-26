import json,glob,sys,re
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'
def tru(s): return s.replace('i','İ').replace('ı','I').upper()
def naive(s): return s.upper().replace('İ','I')
voc={}
for f in glob.glob(S+'/deniz/idx/*.json'):
    for sg in json.load(open(f))['segments']:
        for w in re.findall(r"[\wçğıöşüÇĞİÖŞÜ']+",sg.get('text','')):
            voc.setdefault(naive(w.lower().replace('i̇','i')),set()).add(tru(w.lower()))
extra={'ŞIFALI':'ŞİFALI','BIRAZ':'BİRAZ','SENIN':'SENİN','GELDIM':'GELDİM','BIR':'BİR','MIYIZ':'MİYİZ','IÇINDE':'İÇİNDE','KEMIK':'KEMİK','ELINE':'ELİNE','BEKLIYORUM':'BEKLİYORUM'}
def fix(w):
    core=re.sub(r"[^\wÇĞİÖŞÜ']",'',w); 
    if 'I' not in core: return w
    cands=voc.get(core,set())
    rep=extra.get(core) or (sorted(cands)[0] if len(cands)==1 else None)
    return w.replace(core,rep) if rep else w
for p in sys.argv[1:]:
    d=json.load(open(p)); ch=[]
    for s in d.get('subs',[]):
        for wt in s['words']:
            n=fix(wt[0]); 
            if n!=wt[0]: ch.append(wt[0]+'>'+n); wt[0]=n
    for c in d.get('captions',[]):
        c['text']=' '.join(fix(w) for w in c['text'].split(' '))
    json.dump(d,open(p,'w'),ensure_ascii=False,indent=1); print(p.split('/')[-2],len(ch),ch[:12])
