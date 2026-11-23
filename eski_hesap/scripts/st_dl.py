import json, subprocess, sys, os, time, urllib.request
meta, link, outdir = sys.argv[1:4]
files = json.load(open(meta))['files']
files.sort(key=lambda f: f['size'])
for f in files:
    dst = os.path.join(outdir, f['path'])
    if os.path.exists(dst) and os.path.getsize(dst) == f['size']:
        continue
    for attempt in range(4):
        try:
            r = urllib.request.urlopen(f"https://www.swisstransfer.com/api/1/links/{link}/files/{f['id']}", timeout=60)
            url = json.load(r)['data']['url']
            rc = subprocess.call(['curl', '-s', '-L', '--retry', '3', '-C', '-', '-o', dst, url])
            if os.path.exists(dst) and os.path.getsize(dst) == f['size']:
                print('OK', f['path'], flush=True); break
        except Exception as e:
            print('ERR', f['path'], e, flush=True)
        time.sleep(5 * (attempt + 1))
    else:
        print('FAIL', f['path'], flush=True)
print('DONE', flush=True)
