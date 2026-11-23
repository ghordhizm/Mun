import json,sys,subprocess,os,hashlib
HERE=os.path.dirname(os.path.abspath(__file__))
spec=json.load(open(sys.argv[1])); W=os.path.dirname(os.path.abspath(sys.argv[1]))
brand=json.load(open(spec['brand'])) if spec.get('brand') else {}
B=lambda k,d: spec.get(k, brand.get(k, d))
RAW=spec['raw']; FONTS=B('fonts_dir',os.environ.get('AJANS_FONTS','fonts'))
LOGO=B('logo',''); SLOGAN=B('slogan','')
OSTYLE=B('outro_style','blur'); OBG=B('outro_bg','#F7F3EC')
if OSTYLE=='white' and B('outro_logo',''): LOGO=B('outro_logo','')
TB=B('title_bg','#E01E26'); TF=B('title_fg','#FFFFFF'); TFONT=B('title_font','Montserrat-Black.ttf')
SUB=B('sub',{}); SFONT=SUB.get('font','Montserrat Black'); SSIZE=SUB.get('size',50); SOUT=SUB.get('outline',2.2); SSHAD=SUB.get('shadow',0.8)
SCOL=SUB.get('color','&H00FFFFFF'); KAR=SUB.get('karaoke',True); POP=SUB.get('pop',True); SMV=SUB.get('margin_v',560)
SLFONT=B('slogan_font','BreeSerif.ttf')
def render_png(html,out):
    open(out+'.html','w').write(html)
    subprocess.check_call(['node','-e',f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:1080,height:1920}}}});await p.goto('file://{out}.html');await p.waitForTimeout(400);await p.screenshot({{path:'{out}',omitBackground:true}});await b.close();}})()"""])
title=spec.get('title',[])
PLAIN='' if B('title_style','box')!='plain' else '.b{background:none;box-shadow:none;color:#fff;font-size:%dpx;letter-spacing:2px;padding:0;-webkit-text-stroke:%spx #000;paint-order:stroke fill;text-shadow:0 3px 10px rgba(0,0,0,.35)}'%(B('title_size',78),B('title_stroke',5))
if B('title_style','box')=='plain': TFONT=B('title_font_plain','DMSerifDisplay.ttf')
th=''.join(f'<div class="b">{t}</div>' for t in title)
render_png(f'''<html><head><style>@font-face{{font-family:MB;src:url('file://{FONTS}/{TFONT}')}}
body{{margin:0;background:transparent;width:1080px;height:1920px;overflow:hidden}}.t{{position:absolute;left:0;right:0;top:{spec.get('title_top',250)}px;display:flex;flex-direction:column;align-items:center;gap:14px}}
.b{{font-family:MB;font-size:48px;letter-spacing:1px;padding:14px 30px 12px;border-radius:14px;box-shadow:0 8px 24px rgba(0,0,0,.35);background:{TB};color:{TF}}}{PLAIN}</style></head><body><div class="t">{th}</div></body></html>''',W+'/title.png')
render_png(f'''<html><head><style>@font-face{{font-family:Bree;src:url('file://{FONTS}/{SLFONT}')}}
body{{margin:0;background:transparent;width:1080px;height:1920px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:40px}}
img{{width:{560 if OSTYLE=='white' else 620}px;{'' if OSTYLE=='white' else 'filter:drop-shadow(0 18px 40px rgba(0,0,0,.45))'}}}.s{{font-family:Bree;font-size:54px;color:#fff;text-shadow:0 4px 18px rgba(0,0,0,.6)}}</style></head>
<body>{f'<img src="file://{LOGO}">' if LOGO else ''}{f'<div class="s">{SLOGAN}</div>' if SLOGAN else ''}</body></html>''',W+'/outro.png')
segs=spec['segments']; o=spec['outro']
# timeline
t=0; tl=[]
for s in segs:
    d=(s['out']-s['in'])/s.get('speed',1); tl.append((s,t,d)); t+=d
body=t; OD=o.get('dur',2.6); total=body+OD
def map_t(clip,ts):
    for s,off,d in tl:
        if s['clip']==clip and s['in']-0.05<=ts<=s['out']+0.05: return off+(max(ts,s['in'])-s['in'])/s.get('speed',1)
    return None
# subtitles
def at(x):
    h=int(x//3600);m=int(x%3600//60);sec=x%60;return f"{h}:{m:02d}:{sec:05.2f}"
Y='&H004FB0F5&'; ev=[]
for L in spec.get('subs',[]):
    ws=[(w,map_t(L['clip'],tt)) for w,tt in L['words']]
    ws=[(w,x) for w,x in ws if x is not None]
    if not ws: continue
    end=map_t(L['clip'],L['end']) or ws[-1][1]+0.6
    # split into chunks of max ~3 words / 18 chars
    chunks=[];cur=[]
    for w in ws:
        if cur and (len(cur)>=4 or len(' '.join(x for x,_ in cur+[w]))>20 or cur[-1][0][-1] in '?!.'): chunks.append(cur);cur=[]
        cur.append(w)
    chunks.append(cur)
    for ci,ch in enumerate(chunks):
        cend=chunks[ci+1][0][1] if ci+1<len(chunks) else end
        for i,(w,x) in enumerate(ch):
            a=x if i else max(x-0.08,0); b=ch[i+1][1] if i+1<len(ch) else cend
            if b<=a: b=a+0.15
            if not KAR and i>0: continue
            if not KAR: b=cend
            txt=' '.join((f'{{\\c{Y}}}{q}{{\\c&HFFFFFF&}}' if (j==i and KAR) else q) for j,(q,_) in enumerate(ch))
            pop='{\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}' if (i==0 and POP) else ''
            ev.append([a,b,pop+txt])
ev.sort(key=lambda e:e[0]); out=[]; prev=0
caps=[]
CAPSZ=SUB.get('cap_size',64)
for c in spec.get('captions',[]):
    a=map_t(c['clip'],c['in']); b=map_t(c['clip'],c['out'])
    if a is not None and b is not None: caps.append(f"Dialogue: 1,{at(a)},{at(b)},Cap,,0,0,0,,{{\\fad(150,150)}}{c['text']}")
for a,b,tx in ev:
    a=max(a,prev); 
    if b<=a+0.05: b=a+0.12
    out.append(f"Dialogue: 0,{at(a)},{at(b)},Sub,,0,0,0,,{tx}"); prev=b
ev=out+caps
open(W+'/subs.ass','w').write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{SFONT},{SSIZE},{SCOL},{SCOL},&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,{SOUT},{SSHAD},2,70,70,{SMV},1
Style: Cap,{SFONT},{CAPSZ},&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,0,0,0,0,100,100,1,0,1,{SOUT+0.6},{SSHAD},8,70,70,{SUB.get('cap_margin_v',500)},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""+'\n'.join(ev)+'\n')
# inputs: one seeked input per segment (low memory)
def _dur(c):
    return float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f"{RAW}/{c}.MP4"]).decode().strip())
osp=o.get('speed',1.0); _avail=_dur(o['clip'])-o['in']-0.05
if _avail<OD*osp: osp=max(0.35,_avail/OD)
allsegs=segs+[{'clip':o['clip'],'in':o['in'],'out':o['in']+OD*osp,'speed':osp,'outro':True,'rot':o.get('rot',0)}]
# stage 1: render each segment to a light 1080p intermediate (memory-safe)
os.makedirs(W+'/_seg',exist_ok=True)
grade=spec.get('grade','eq=contrast=1.06:saturation=1.12')
for k,s in enumerate(allsegs):
    sp=s.get('speed',1)
    rot=subprocess.run(['ffprobe','-v','error','-select_streams','v','-show_entries','stream_side_data=rotation','-of','csv=p=0',f"{RAW}/{s['clip']}.MP4"],capture_output=True,text=True).stdout.strip().strip(',')
    hx=s.get('hx',0.5)
    fit=f"crop=ih*9/16:ih:(iw-ih*9/16)*{hx}/0.5/2:0,scale=1080:1920:flags=lanczos" if rot not in ('90','-90') else "scale=1080:1920:flags=lanczos"
    if s.get('rot'): fit=("transpose=1" if s['rot']==1 else "transpose=2")+",scale=1080:1920:flags=lanczos"
    v=f"setpts=(PTS-STARTPTS)/{sp},{fit},setsar=1,fps=30,{grade}"
    if s.get('bw'): v+=",hue=s=0"
    z=s.get('zoom')
    if z:
        f,cx,cy=z; w=int(1080/f)//2*2; h=int(1920/f)//2*2
        v+=f",crop={w}:{h}:{max(0,min(1080-w,int(cx*1080-w/2)))}:{max(0,min(1920-h,int(cy*1920-h/2)))},scale=1080:1920:flags=lanczos,setsar=1"
    a="asetpts=PTS-STARTPTS,"+("afftdn=nf=-28," if B("denoise",True) else "")+("dynaudnorm=f=300:g=21:p=0.85:m=12," if B("speech_boost",False) else "")+"aresample=48000"
    if sp!=1 and not s.get('outro'): a+=f",atempo={sp}"
    if s.get("outro"): a+=f",apad=whole_dur={OD:.3f}"
    if s.get("vol") is not None: a+=f",volume={s['vol']}"
    if s.get('mute'): a+=",volume=0"
    if s.get('outro') and o.get('mute_audio',True): a+=",afade=out:st=0:d=0.5"
    subprocess.check_call(['ffmpeg','-v','error','-y','-ss',str(s['in']),'-t',str(s['out']-s['in']),'-i',f"{RAW}/{s['clip']}.MP4",'-vf',v,'-af',a,'-ac','2','-c:v','libx264','-crf','16','-preset','veryfast','-c:a','pcm_s16le','-threads','4',f"{W}/_seg/{k:02d}.mkv"])
inp=[]
for k,s in enumerate(allsegs): inp+=['-i',f"{W}/_seg/{k:02d}.mkv"]
ni=len(allsegs); inp+=['-loop','1','-t',str(total+1),'-i',W+'/title.png','-loop','1','-t',str(total+1),'-i',W+'/outro.png']
music=spec.get('music')
if music: inp+=['-i',music['file']]
ovs=[]
for ov in spec.get('overlays',[]):
    a=map_t(ov['clip'],ov['in']); b=map_t(ov['clip'],ov['out'])
    if a is None or b is None: continue
    ovs.append((len(inp)//2 if False else None,ov,a,b)); inp+=['-loop','1','-t',str(total+1),'-i',ov['img']]
fc=[]
for k,s in enumerate(allsegs):
    fc.append(f"[{k}:v]setpts=PTS-STARTPTS[v{k}]"); fc.append(f"[{k}:a]asetpts=PTS-STARTPTS[a{k}]")
n=len(allsegs)
fc.append(''.join(f'[v{k}][a{k}]' for k in range(n))+f'concat=n={n}:v=1:a=1[cv][ca]')
fc.append('[cv]tpad=stop_mode=clone:stop_duration=3,split[base][blr]')
if OSTYLE=='white':
    fc.append(f"[blr]drawbox=x=0:y=0:w=iw:h=ih:color={OBG}:t=fill,format=rgba,fade=in:st={body+0.05:.3f}:d=1.2:alpha=1[blur]")
else:
    fc.append(f"[blr]boxblur=20:2,eq=brightness=-0.12,format=rgba,fade=in:st={body+0.05:.3f}:d=1.0:alpha=1[blur]")
if OSTYLE=='white': fc.append(f"[base][blur]overlay=0:0,drawbox=x=0:y=0:w=iw:h=ih:color={OBG}:t=fill:enable='gte(t,{body+1.25:.3f})'[b2]")
else: fc.append('[base][blur]overlay=0:0[b2]')
te=body-0.1
if spec.get('title_end') is not None:
    te=spec['title_end'] if isinstance(spec['title_end'],(int,float)) else tl[1][1]-0.3
fc.append(f"[{ni}:v]format=rgba,fade=out:st={te:.3f}:d={spec.get("title_fade",0.35)}:alpha=1[ttl]")
fc.append('[b2][ttl]overlay=0:0:eof_action=pass[b3]')
fc.append(f"[{ni+1}:v]format=rgba,fade=in:st={body+0.7:.3f}:d=1.1:alpha=1[lg]")
cur='b3'
base_idx=ni+2+(1 if music else 0)
for j,(_,ov,a,b) in enumerate(ovs):
    sz=ov.get('size',300); y=ov.get('y',1060)
    if ov.get('full'):
        fd='' if ov.get('nofade') else f",fade=in:st={a:.2f}:d=0.4:alpha=1,fade=out:st={b-0.3:.2f}:d=0.3:alpha=1"
        fc.append(f"[{base_idx+j}:v]format=rgba{fd}[ov{j}]")
        fc.append(f"[{cur}][ov{j}]overlay=0:0:enable='between(t,{a:.2f},{b:.2f})'[o{j}]"); cur=f'o{j}'; continue
    fd2='' if ov.get('nofade') else f",fade=in:st={a:.2f}:d=0.25:alpha=1,fade=out:st={b-0.25:.2f}:d=0.25:alpha=1"
    fc.append(f"[{base_idx+j}:v]scale={sz}:{sz},format=rgba{fd2}[ov{j}]")
    fc.append(f"[{cur}][ov{j}]overlay=(W-w)/2:{y}:enable='between(t,{a:.2f},{b:.2f})'[o{j}]"); cur=f'o{j}'
fc.append(f"[{cur}][lg]overlay=0:0,subtitles={W}/subs.ass:fontsdir={FONTS},trim=0:{total:.3f},setpts=PTS-STARTPTS[vf]")
if music:
    mi=ni+2; vol=music.get('vol',0.12)
    fc.append(f"[{mi}:a]atrim={music.get('start',0)}:{music.get('start',0)+total},asetpts=PTS-STARTPTS,volume={vol},afade=out:st={total-2.6:.2f}:d=2.6[mu]")
    if music.get('duck'):
        fc.append(f"[ca]atrim=0:{total:.3f},asplit[cd][sc];[mu][sc]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400[md];[cd][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[af]")
    else:
        fc.append(f"[ca]atrim=0:{total:.3f}[cd];[cd][mu]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[af]")
else:
    fc.append(f"[ca]atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[af]")
open(W+'/fc.txt','w').write(';\n'.join(fc))
cmd=['ffmpeg','-v','error','-y']+inp+['-filter_complex_script',W+'/fc.txt','-map','[vf]','-map','[af]','-c:v','libx264','-preset','medium','-crf','19','-threads','4','-pix_fmt','yuv420p','-movflags','+faststart','-c:a','aac','-b:a','192k','-ar','48000',spec['out']]
subprocess.check_call(cmd)
print('OK',spec['out'],round(total,2),'s')
