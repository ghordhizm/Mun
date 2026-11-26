import numpy as np, subprocess, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'; W=S+'/deniz/edit/p12'
F='/home/user/Mun/.claude/skills/ajans-edit/fonts/'
FPS=30; TOTAL=10.0; BODY=7.4; BH=640
items=[('b1978','Mercimek',(222,166,48)),('b2113','Domates',(178,62,42)),('b1542','Ayak Paça',(196,170,120))]
fT=ImageFont.truetype(F+'DMSerifDisplay.ttf',78)
bowls=[Image.open(f'{S}/deniz/post/a/{b}.png').convert('RGBA').resize((430,430),Image.LANCZOS) for b,_,_ in items]
sh=[]
for b in bowls:
    s=Image.new('RGBA',(520,520),(0,0,0,0)); s.paste((0,0,0,90),(45,60),b.getchannel('A')); sh.append(s.filter(ImageFilter.GaussianBlur(18)))
logo=Image.open('/home/user/Mun/.claude/skills/ajans-edit/brands/logos/deniz_logo_seffaf.png').convert('RGBA').resize((560,703),Image.LANCZOS)
eo=lambda x:1-(1-max(0,min(1,x)))**3
def band(k,t):
    b,name,col=items[k]
    im=Image.new('RGBA',(1080,BH),(246,240,229,255)); d=ImageDraw.Draw(im)
    d.rectangle((0,250,1080,390),fill=col+(255,))
    # name
    na=eo((t-0.9-0.35*k)/0.5)
    if na>0:
        tl=Image.new('RGBA',(1080,BH),(0,0,0,0)); td=ImageDraw.Draw(tl); w=td.textlength(name,font=fT)
        td.text(((1080-w)/2,40),name,font=fT,fill=(19,41,75,int(255*na))); im.alpha_composite(tl)
    # slide
    p=eo((t-0.15*k)/0.8); dirn=1 if k!=1 else -1
    x=540+dirn*(1-p)*900
    z=1.0
    zs=2.2+0.9*k
    if t>zs: z=1+0.07*eo((t-zs)/0.6)
    bw=int(430*z); bb=bowls[k].resize((bw,bw),Image.BILINEAR); ss=sh[k].resize((int(520*z),int(520*z)),Image.BILINEAR)
    cy=380
    im.alpha_composite(ss,(int(x-ss.width/2+10),int(cy-ss.height/2+18)))
    im.alpha_composite(bb,(int(x-bw/2),int(cy-bw/2)))
    return im
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',W+'/ref.wav',
 '-filter_complex',f'[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,apad=whole_dur={TOTAL},afade=out:st={TOTAL-2.4}:d=2.4,loudnorm=I=-14:TP=-1.5[a]','-map','0:v','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',W+'/DENIZ_Reels12_UcCorba_v2.mp4'],stdin=subprocess.PIPE)
for f in range(int(TOTAL*FPS)):
    t=f/FPS; fr=Image.new('RGBA',(1080,1920))
    for k in range(3): fr.alpha_composite(band(k,t),(0,k*BH))
    fr=fr.convert('RGB')
    if t>BODY:
        p=min(1,(t-BODY)/1.2); fr=Image.blend(fr,Image.new('RGB',fr.size,(247,243,236)),p)
        lp=min(1,max(0,(t-BODY-0.7)/1.1))
        if lp>0:
            fr=fr.convert('RGBA'); lo=logo.copy(); lo.putalpha(lo.getchannel('A').point(lambda v:int(v*lp))); fr.alpha_composite(lo,(260,608)); fr=fr.convert('RGB')
    out.stdin.write(fr.tobytes())
out.stdin.close(); out.wait(); print('OK')
