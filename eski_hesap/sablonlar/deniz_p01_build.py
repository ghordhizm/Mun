import subprocess
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter, ImageEnhance
S='/tmp/claude-0/-home-user-Mun/521f8cfe-2f47-55ee-947c-c97f3b0a55cf/scratchpad'; W=S+'/deniz/edit/p01'; F='/home/user/Mun/.claude/skills/ajans-edit/fonts/'
D=[('02240','Makarna'),('02242','Pilav Üstü Kuru Fasulye'),('02243','Bulgur Pilavı'),('02245','Taze Fasulye')]
def load(n):
    im=ImageOps.exif_transpose(Image.open(f'{S}/deniz/foto/DSC{n}.JPG')).convert('RGB'); w,h=im.size
    tw=int(h*9/16); im=im.crop(((w-tw)//2,0,(w-tw)//2+tw,h)).resize((1080,1920),Image.LANCZOS)
    return ImageEnhance.Color(im).enhance(1.1)
P=[load(n) for n,_ in D]
fN=ImageFont.truetype(F+'DMSerifDisplay.ttf',84); fT=ImageFont.truetype(F+'Montserrat-Black.ttf',58)
logo=Image.open('/home/user/Mun/.claude/skills/ajans-edit/brands/logos/deniz_logo_seffaf.png').convert('RGBA').resize((560,703),Image.LANCZOS)
bt=[0,0.46,0.93,1.39,1.88,2.32,2.72,3.09]; order=[0,1,2,3,1,2,3]
sched=[(bt[k],bt[k+1],order[k]) for k in range(7)]
BODY=3.09; TOTAL=3.09; FPS=30
def label(im,txt):
    d=ImageDraw.Draw(im,'RGBA')
    tw=d.textlength('FAVORİNİ SEÇ',font=fT); d.rounded_rectangle(((1080-tw)/2-30,230,(1080+tw)/2+30,330),18,fill=(19,41,75,235)); d.text(((1080-tw)/2,244),'FAVORİNİ SEÇ',font=fT,fill='white')
    w=d.textlength(txt,font=fN); y=1690
    d.text(((1080-w)/2+3,y+4),txt,font=fN,fill=(0,0,0,140)); d.text(((1080-w)/2,y),txt,font=fN,fill=(255,255,255,255))
out=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r',str(FPS),'-i','-','-i',W+'/ref.wav',
 '-filter_complex',f'[1:a]atrim=0:{TOTAL:.2f},asetpts=PTS-STARTPTS,apad=whole_dur={TOTAL:.2f},loudnorm=I=-14:TP=-1.5[a]','-map','0:v','-map','[a]',
 '-c:v','libx264','-crf','18','-preset','medium','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-movflags','+faststart',W+'/DENIZ_Reels01_FavoriniSec_v2.mp4'],stdin=subprocess.PIPE)
for f in range(int(TOTAL*FPS)):
    t=f/FPS
    i=[s for s in sched if s[0]<=t<s[1]]; i=i[0][2] if i else sched[-1][2]
    z=1.0; im=P[i]; ww,hh=int(1080/z),int(1920/z); fr=im.crop(((1080-ww)//2,(1920-hh)//2,(1080-ww)//2+ww,(1920-hh)//2+hh)).resize((1080,1920),Image.BILINEAR)
    if t<BODY: label(fr,D[i][1])
    else:
        p=min(1,(t-BODY)/1.2); fr=Image.blend(fr,Image.new('RGB',fr.size,(247,243,236)),p)
        lp=min(1,max(0,(t-BODY-0.7)/1.1))
        if lp>0:
            fr=fr.convert('RGBA'); lo=logo.copy(); lo.putalpha(lo.getchannel('A').point(lambda v:int(v*lp))); fr.alpha_composite(lo,(260,608)); fr=fr.convert('RGB')
    out.stdin.write(fr.tobytes())
out.stdin.close(); out.wait(); print('OK',TOTAL)
