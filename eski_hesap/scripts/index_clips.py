import json, os, subprocess, sys, time, glob, wave
import numpy as np
raw, out, meta = sys.argv[1:4]
os.makedirs(out, exist_ok=True)
expected = {f['path']: f['size'] for f in json.load(open(meta))['files'] if f['path'].endswith('.MP4')}
from faster_whisper import WhisperModel
model = WhisperModel('medium', device='cpu', compute_type='int8', cpu_threads=3)
done = set()
while len(done) < len(expected):
    progressed = False
    for name, size in sorted(expected.items()):
        if name in done: continue
        p = os.path.join(raw, name)
        if not (os.path.exists(p) and os.path.getsize(p) == size): continue
        base = os.path.join(out, name[:-4])
        if not os.path.exists(base + '.json'):
            pr = json.loads(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration:stream=width,height,r_frame_rate,codec_type','-of','json',p]))
            dur = float(pr['format']['duration'])
            subprocess.call(['ffmpeg','-v','error','-y','-i',p,'-vf',f'fps={12/dur},scale=200:-2,tile=6x2:padding=3','-frames:v','1',base+'_sheet.jpg'])
            subprocess.call(['ffmpeg','-v','error','-y','-i',p,'-vn','-ac','1','-ar','16000',base+'.wav'])
            segs = []
            try:
                w = wave.open(base+'.wav'); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
                if len(a) > 0:
                    s_, _ = model.transcribe(a, language='tr', vad_filter=True, word_timestamps=True)
                    segs = [{'start':round(s.start,2),'end':round(s.end,2),'text':s.text.strip(),'words':[[round(x.start,2),round(x.end,2),x.word] for x in (s.words or [])]} for s in s_]
            except Exception as e:
                print('ASR ERR', name, e, flush=True)
            json.dump({'file':name,'duration':dur,'probe':pr,'segments':segs}, open(base+'.json','w'), ensure_ascii=False)
            os.remove(base+'.wav')
            print('IDX', name, round(dur,1), len(segs), flush=True)
        done.add(name); progressed = True
    if not progressed: time.sleep(30)
print('ALLDONE', flush=True)
