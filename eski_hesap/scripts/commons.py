import json,sys,urllib.request,urllib.parse
q,n=sys.argv[1],int(sys.argv[2])
u='https://commons.wikimedia.org/w/api.php?'+urllib.parse.urlencode({'action':'query','format':'json','generator':'search','gsrnamespace':6,'gsrsearch':q+' filetype:bitmap','gsrlimit':n,'prop':'imageinfo','iiprop':'url|size|extmetadata','iiurlwidth':900})
r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'content-planner/1.0'})))
for p in sorted(r.get('query',{}).get('pages',{}).values(),key=lambda x:x['index']):
    ii=p['imageinfo'][0]; lic=ii.get('extmetadata',{}).get('LicenseShortName',{}).get('value','')
    print(p['title'][:60],'|',ii['width'],'x',ii['height'],'|',lic,'|',ii['thumburl'])
