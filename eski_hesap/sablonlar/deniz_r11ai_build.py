import numpy as np, subprocess, math
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'; W='%s/deniz/edit/r11ai'%S
F='/home/user/Mun/.claude/skills/ajans-edit/fonts/'
ref=np.asarray(Image.open(S+'/deniz/ai/ref_5.8.jpg').convert('RGB')).astype(np.float32)  # 720x1280
h,w,_=ref.shape
# synthesize clean background from edge columns (right edge free of text)
right=np.median(ref[:,690:716],axis=1); left=np.median(ref[:,2:14],axis=1)
bg=np.zeros_like(ref)
for x in range(w):
    a=x/(w-1); bg[:,x]=left*(1-a)+right*a
bgsm=np.asarray(Image.fromarray(bg.astype(np.uint8)).filter(ImageFilter.GaussianBlur(6))).astype(np.float32)
SC=1080/720
BG=Image.fromarray(bgsm.astype(np.uint8)).resize((1080,1920),Image.LANCZOS)
# ingredient sprites
L=[('SIVI YAĞ','5 yemek kaşığı',135,190),('TEREYAĞI','1 yemek kaşığı',190,295),('SOĞAN','1 adet',290,385),('DOMATES SALÇASI','yarım yemek kaşığı',395,495),('HAVUÇ','1 adet',495,565),('KIRMIZI MERCİMEK','2 su bardağı',565,665),('ET SUYU','2 litre',675,745),('TUZ','1 tatlı kaşığı',745,815),('KARABİBER','yarım çay kaşığı',818,885),('KİMYON','1 çay kaşığı',878,950),('PUL BİBER','1 çay kaşığı',955,1035)]
K=0.72
spr=[]
for name,q,a,b in L:
    c=ref[a:b,264:690]; g=bgsm[a:b,264:690]
    d=np.sqrt(((c-g)**2).sum(2)); al=np.clip((d-14)/26,0,1)
    al=np.asarray(Image.fromarray((al*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2)))
    im=Image.fromarray(c.astype(np.uint8)).convert('RGBA'); im.putalpha(Image.fromarray(al))
    s=SC*K; im=im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
    im=ImageEnhance.Sharpness(im).enhance(1.4)
    spr.append((name,q,im,(a+b)/2))
# vertical layout: map ref centers 160..1000 -> 210..1210
y0r,y1r=spr[0][3],spr[-1][3]; ty=[210+(c-y0r)/(y1r-y0r)*1000 for *_,c in spr]
# bottom: Deniz bowl photo
ph=Image.open(S+'/deniz/ai/DENIZ_AI_Mercimek_yatay.jpg'); PW,PH=ph.size
cw=int(PW*0.92); x0=int(PW*0.51)-cw//2; x0=max(0,min(PW-cw,x0)); crop=ph.crop((x0,0,x0+cw,PH)).resize((1080,round(PH*1080/cw)),Image.LANCZOS)
by=1920-crop.height
m=Image.new('L',crop.size,255); gr=Image.linear_gradient('L').resize((1080,170)); m.paste(gr,(0,0))
SCENE=BG.copy(); SCENE.paste(crop,(0,by),m)
bowl_y=by+int(crop.height*0.22); bowl_x=540+int((0.51*PW-(x0+cw/2))*1080/cw)
fT=ImageFont.truetype(F+'Montserrat-700.ttf',34); fQ=ImageFont.truetype(F+'Montserrat-500.ttf',24)
# intro/outro background (vertical photo)
V=Image.open(S+'/deniz/ai/DENIZ_AI_Mercimek_dikey.jpg').resize((1080,1920),Image.LANCZOS)
logo=Image.open('/home/user/Mun/.claude/skills/ajans-edit/brands/logos/deniz_logo_rozet.png').convert('RGBA'); lw=560; logo=logo.resize((lw,int(logo.height*lw/logo.width)),Image.LANCZOS)
fS=ImageFont.truetype(F+'DMSerifDisplay.ttf',62)
FPS=30; T_INTRO=2.2; T_UP=T_INTRO+0.3; STEP=0.28; DUR=0.55; HOLD_END=T_UP+10*STEP+DUR+2.4; DSTEP=0.11; DDUR=0.42
T_BACK_END=HOLD_END+10*DSTEP+DDUR; T_OUT=T_BACK_END+0.25; TOTAL=T_OUT+3.0
eo=lambda x:1-(1-x)**3; ei=lambda x:x**3
def kb(t,t0,dur,z0,z1):
    p=min(1,max(0,(t-t0)/dur)); z=z0+(z1-z0)*p; ww,hh=int(1080/z),int(1920/z)
    return V.crop(((1080-ww)//2,(1920-hh)//2+int(80*(1-1/z)),(1080-ww)//2+ww,(1920-hh)//2+int(80*(1-1/z))+hh)).resize((1080,1920),Image.BILINEAR)
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',S+'/music/mk_1063.mp3',
 '-filter_complex',f'[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,volume=0.8,afade=in:d=0.3,afade=out:st={TOTAL-2.6:.2f}:d=2.6,loudnorm=I=-14:TP=-1.5[a]',
 '-map','0:v','-map','[a]','-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',W+'/DENIZ_Reels11_MercimekIcindekiler_v2.mp4'],stdin=subprocess.PIPE)
n=int(TOTAL*FPS)
for f in range(n):
    t=f/FPS
    if t<T_INTRO:
        fr=kb(t,0,T_INTRO,1.0,1.08)
    elif t<T_OUT:
        fr=SCENE.copy(); d=ImageDraw.Draw(fr)
        for i,(name,q,im,_) in enumerate(spr):
            tu=T_UP+i*STEP; td=HOLD_END+(10-i)*DSTEP
            if t<tu: continue
            if t<td:
                pr=eo(min(1,(t-tu)/DUR)); y=bowl_y+(ty[i]-bowl_y)*pr; s=0.35+0.65*pr; a=min(1,(t-tu)/0.2)
            else:
                pr=ei(min(1,(t-td)/DDUR)); y=ty[i]+(bowl_y-ty[i])*pr; s=1-0.65*pr; a=1-max(0,(pr-0.6)/0.4)
                if pr>=1: continue
            sp=im.resize((max(1,int(im.width*s)),max(1,int(im.height*s))),Image.BILINEAR)
            if a<1: sp.putalpha(sp.getchannel('A').point(lambda v:int(v*a)))
            cx0=bowl_x+110; cx=bowl_x+(cx0-bowl_x)*(pr if t<td else 1-pr); fr.paste(sp,(int(cx-sp.width/2),int(y-sp.height/2)),sp)
            # label
            la=min(1,max(0,(t-(tu+DUR*0.6))/0.25))*(1-min(1,max(0,(t-HOLD_END)/0.25)))
            if la>0:
                col=(255,255,255,int(255*la)); ov=Image.new('RGBA',(400,90),(0,0,0,0)); od=ImageDraw.Draw(ov)
                od.text((0,0),name,font=fT,fill=col); od.text((0,40),q,font=fQ,fill=(255,245,230,int(230*la)))
                fr.paste(ov,(48,int(ty[i]-30)),ov)
    else:
        base=kb(t,T_OUT,TOTAL-T_OUT,1.0,1.05)
        bp=min(1,(t-T_OUT)/1.0); bl=base.filter(ImageFilter.GaussianBlur(18)); bl=ImageEnhance.Brightness(bl).enhance(0.86)
        fr=Image.blend(base,bl,bp)
        lp=min(1,max(0,(t-T_OUT-0.7)/1.1))
        if lp>0:
            lo=logo.copy(); lo.putalpha(lo.getchannel('A').point(lambda v:int(v*lp)))
            fr=fr.convert('RGBA'); fr.alpha_composite(lo,((1080-lw)//2,700))
            ov=Image.new('RGBA',(1080,120),(0,0,0,0)); od=ImageDraw.Draw(ov); tw=od.textlength('Afiyet olsun.',font=fS)
            od.text(((1080-tw)/2,10),'Afiyet olsun.',font=fS,fill=(255,255,255,int(255*lp))); fr.alpha_composite(ov,(0,700+logo.height+40)); fr=fr.convert('RGB')
    if t>=T_INTRO and t<T_INTRO+0.12: fr=Image.blend(fr,Image.new('RGB',fr.size,'white'),0.5*(1-(t-T_INTRO)/0.12))
    p.stdin.write(fr.convert('RGB').tobytes())
p.stdin.close(); p.wait(); print('OK',TOTAL)
