import numpy as np, subprocess, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'; W=S+'/deniz/edit/p08'
F='/home/user/Mun/.claude/skills/ajans-edit/fonts/'
FPS=30; BH=640; Y0=470
bands=[('C0836',0.8,'CUMA'),('C0838',0.0,'CUMARTESİ'),('C0839',1.9,'PAZAR')]
TOTAL=11.8; BODY=9.2
def read(c,pad):
    p=subprocess.run(['ffmpeg','-v','error','-i',f'{S}/deniz/raw/{c}.MP4','-vf',f'scale=1080:1920,crop=1080:{BH}:0:{Y0},fps={FPS},eq=contrast=1.05:saturation=1.1','-f','rawvideo','-pix_fmt','rgb24','-'],capture_output=True).stdout
    a=np.frombuffer(p,np.uint8).reshape(-1,BH,1080,3)
    n=int(TOTAL*FPS); pre=int(pad*FPS)
    idx=[0]*pre+list(range(len(a))); idx=idx+[len(a)-1]*(n-len(idx)); return a,idx[:n]
data=[read(c,p) for c,p,_ in bands]
font=ImageFont.truetype(F+'DMSerifDisplay.ttf',150)
txt=[]
for _,_,t in bands:
    im=Image.new('L',(1080,BH),0); d=ImageDraw.Draw(im); w=d.textlength(t,font=font); d.text(((1080-w)/2,BH/2-40),t,font=font,fill=255)
    txt.append(np.asarray(im).astype(np.float32)/255)
logo=Image.open('/home/user/Mun/.claude/skills/ajans-edit/brands/logos/deniz_logo_seffaf.png').convert('RGBA'); logo=logo.resize((560,703),Image.LANCZOS)
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',S+'/music/mk_540.mp3',
 '-filter_complex',f'[1:a]atrim=0:{TOTAL},asetpts=PTS-STARTPTS,volume=0.9,afade=in:d=0.4,afade=out:st={TOTAL-2.6}:d=2.6,loudnorm=I=-14:TP=-1.5[a]','-map','0:v','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',W+'/DENIZ_Reels08_CumaCumartesiPazar_v1.mp4'],stdin=subprocess.PIPE)
seen=[np.zeros((BH,1080),np.float32) for _ in bands]
for f in range(int(TOTAL*FPS)):
    t=f/FPS; fr=np.zeros((1920,1080,3),np.float32)
    # backdrop: blurred upper/lower from band 1/3
    for k,(a,idx) in enumerate(data):
        img=a[idx[f]].astype(np.float32)
        last=a[-1].astype(np.float32)
        dd=np.abs(img-last).mean(2)
        wood=np.clip((40-dd)/20,0,1)
        wood=cv2.GaussianBlur(cv2.morphologyEx(wood,cv2.MORPH_OPEN,np.ones((9,9),np.uint8)),(0,0),2)
        seen[k]=wood
        m=txt[k]*np.clip(seen[k],0,1)
        col=np.array([255,248,236],np.float32)
        sh=cv2.GaussianBlur(m,(0,0),6)[...,None]*0.45
        img=img*(1-sh)
        img=img*(1-m[...,None])+col*m[...,None]
        fr[k*BH:(k+1)*BH]=img
    # thin separators
    for k in (1,2): fr[k*BH-3:k*BH+3]=np.array([250,246,238])
    if t>BODY:
        p=min(1,(t-BODY)/1.2); fr=fr*(1-p)+np.array([247,243,236],np.float32)*p
        lp=min(1,max(0,(t-BODY-0.7)/1.1))
        if lp>0:
            im=Image.fromarray(np.clip(fr,0,255).astype(np.uint8)).convert('RGBA'); lo=logo.copy(); lo.putalpha(lo.getchannel('A').point(lambda v:int(v*lp)))
            im.alpha_composite(lo,(260,608)); fr=np.asarray(im.convert('RGB')).astype(np.float32)
    out.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
out.stdin.close(); out.wait(); print('OK')
