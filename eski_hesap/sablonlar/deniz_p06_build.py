import numpy as np, subprocess
from PIL import Image, ImageFilter, ImageEnhance
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'; W=S+'/deniz/edit/p06'
FPS=30
SEC=[('C0835',4.0,8.4,'01978','Mercimek'),('C0857',0.2,2.85,'02153','Kelle Paça'),('C0855',1.2,3.0,'02028','Ezogelin')]
def frames(c,a,b,sp=1.0):
    p=subprocess.run(['ffmpeg','-v','error','-ss',str(a),'-t',str(b-a),'-i',f'{S}/deniz/raw/{c}.MP4','-vf',f'setpts=PTS/{sp},scale=1080:1920,crop=1080:960:0:480,fps=30,eq=contrast=1.05:saturation=1.1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    return np.frombuffer(p,np.uint8).reshape(-1,960,1080,3)
from PIL import ImageOps, ImageDraw, ImageFont
import cv2
def still(n,name):
    im=ImageOps.exif_transpose(Image.open(f'{S}/deniz/foto/DSC{n}.JPG')).convert('RGB'); a=np.asarray(im)
    hsv=cv2.cvtColor(a,cv2.COLOR_RGB2HSV); ys,xs=np.nonzero(hsv[...,1]>90); cx,cy=int(np.median(xs)),int(np.median(ys))
    w=int(min(im.width,im.height*1.125)); h=int(w/1.125); x0=max(0,min(im.width-w,cx-w//2)); y0=max(0,min(im.height-h,cy-h//2))
    t=im.crop((x0,y0,x0+w,y0+h)).resize((1080,960),Image.LANCZOS); t=ImageEnhance.Color(t).enhance(1.1)
    d=ImageDraw.Draw(t,'RGBA'); f=ImageFont.truetype('/home/user/Mun/.claude/skills/ajans-edit/fonts/DMSerifDisplay.ttf',64); tw=d.textlength(name,font=f)
    d.rounded_rectangle(((1080-tw)/2-34,850,(1080+tw)/2+34,945),22,fill=(19,41,75,235)); d.text(((1080-tw)/2,858),name,font=f,fill='white')
    return t
data=[]
for i,(c,a,b,ph,name) in enumerate(SEC):
    extra=2.8 if i==len(SEC)-1 else 0
    sp={'C0857':0.6,'C0855':0.5}.get(c,1.0)
    data.append((still(ph,name),frames(c,a,b+extra*sp,sp)))
logo=Image.open('/home/user/Mun/.claude/skills/ajans-edit/brands/logos/deniz_logo_seffaf.png').convert('RGBA').resize((560,703),Image.LANCZOS)
durs=[(b-a)/{'C0857':0.6,'C0855':0.5}.get(c,1.0) for c,a,b,_,_ in SEC]; starts=np.cumsum([0]+durs[:-1]); BODY=sum(durs); TOTAL=BODY+2.6; TR=0.35
def comp(k,t):
    st,fr=data[k]; lt=t-starts[k]; z=1+0.05*min(1,lt/4); ww,hh=int(1080/z),int(960/z)
    top=st.crop(((1080-ww)//2,(960-hh)//2,(1080-ww)//2+ww,(960-hh)//2+hh)).resize((1080,960),Image.BILINEAR)
    bot=Image.fromarray(fr[min(len(fr)-1,max(0,int(lt*FPS)))])
    im=Image.new('RGB',(1080,1920)); im.paste(top,(0,0)); im.paste(bot,(0,960)); return im
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',W+'/ref.wav',
 '-filter_complex',f'[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,apad=whole_dur={TOTAL:.2f},afade=out:st={TOTAL-2.4:.2f}:d=2.4,loudnorm=I=-14:TP=-1.5[a]','-map','0:v','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',W+'/DENIZ_Reels06_ServisHazirlik_v2.mp4'],stdin=subprocess.PIPE)
for f in range(int(TOTAL*FPS)):
    t=f/FPS; k=int(np.searchsorted(starts,t,side='right')-1); k=min(k,len(SEC)-1)
    fr=comp(k,t)
    if k>0 and t-starts[k]<TR:  # slide from right
        p=(t-starts[k])/TR; p=1-(1-p)**3; prev=comp(k-1,t); off=int(1080*p)
        c=Image.new('RGB',(1080,1920)); c.paste(prev,(-off,0)); c.paste(fr,(1080-off,0)); fr=c
    if t>BODY:
        p=min(1,(t-BODY)/1.2); fr=Image.blend(fr,Image.new('RGB',fr.size,(247,243,236)),p)
        lp=min(1,max(0,(t-BODY-0.7)/1.1))
        if lp>0:
            fr=fr.convert('RGBA'); lo=logo.copy(); lo.putalpha(lo.getchannel('A').point(lambda v:int(v*lp))); fr.alpha_composite(lo,(260,608)); fr=fr.convert('RGB')
    else:
        d=Image.new('RGB',(1080,6),(250,246,238)); fr.paste(d,(0,957))
    out.stdin.write(fr.tobytes())
out.stdin.close(); out.wait(); print('OK',TOTAL)
