import cv2,numpy as np,glob,os,sys
from PIL import Image
out={}
import sys
RNG={'a/c1972.png':(1.12,1.24),'a/c1978.png':(1.12,1.24),'a/c1542.png':(1.35,1.85)}
for f in sys.argv[1:]:
    lo,hi=RNG[f]
    im=np.array(Image.open(f).convert('RGBA')); rgb=im[...,:3].copy(); A=im[...,3]
    hsv=cv2.cvtColor(rgb,cv2.COLOR_RGB2HSV)
    m=((hsv[...,1]>70)&(A>0)).astype(np.uint8)*255
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((7,7),np.uint8)); m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((25,25),np.uint8))
    cs,_=cv2.findContours(m,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)
    (cx,cy),rs=cv2.minEnclosingCircle(c); (ex,ey),(MA,ma),ang=cv2.fitEllipse(c); rs=(MA+ma)/4; cx,cy=ex,ey
    g=cv2.cvtColor(rgb,cv2.COLOR_RGB2GRAY).astype(np.float32); g=cv2.GaussianBlur(g,(5,5),0)
    gx=cv2.Sobel(g,cv2.CV_32F,1,0); gy=cv2.Sobel(g,cv2.CV_32F,0,1)
    th=np.linspace(0,2*np.pi,720,endpoint=False); best=[]
    for r in np.arange(rs*lo,min(rs*hi,445),0.5):
        xs=(cx+r*np.cos(th)).astype(int); ys=(cy+r*np.sin(th)).astype(int); ok=(xs>=0)&(xs<900)&(ys>=0)&(ys<900)
        rad=np.abs(gx[ys[ok],xs[ok]]*np.cos(th[ok])+gy[ys[ok],xs[ok]]*np.sin(th[ok]))
        best.append((np.median(rad),r))
    best.sort(reverse=True); rb=best[0][1]
    out[f]=(rs,rb,rb/rs)
    R=rb-3; Y,X=np.mgrid[:900,:900]; d=np.sqrt((X-cx)**2+(Y-cy)**2); al=np.clip((R-d)/1.5,0,1)*255
    o=np.dstack([rgb,al.astype(np.uint8)]); x0,y0=int(cx-R-2),int(cy-R-2); s=int(2*R+4)
    o=o[max(0,y0):y0+s,max(0,x0):x0+s]
    Image.fromarray(o).resize((800,800),Image.LANCZOS).save(f.replace('/c','/b'))
for k,v in out.items(): print(k,[round(x,2) for x in v])
