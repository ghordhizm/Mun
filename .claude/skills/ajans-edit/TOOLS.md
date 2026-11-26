# TOOLS.md — ek araçlar (ajans-edit)

Klonlar: `/home/user/work/repos/` (proje dışı). Hepsi ortamda kurulu/test edildi.

## Hyperframes (HTML → MP4) — v0.9.84, global npm
- Yol: `hyperframes` (global CLI), klon: `/home/user/work/repos/hyperframes`, skill'ler: `.claude/skills/{hyperframes,hyperframes-cli,media-use}/`
- Çağrı: `hyperframes init isim --example blank --resolution portrait --non-interactive` → `index.html`'i düzenle (GSAP timeline) → `hyperframes check` → `hyperframes render --output /abs/out.mp4`
- Chrome: `/usr/bin/google-chrome` (doctor ✓). Telemetri kapatıldı. İlk render ~50 sn (3 sn video), yazı tipleri/GSAP jsdelivr'den gelir.
- Ne için: outro kartı (logo fade-in), split-screen çorba, kağıt çekme akımı yazıları, kinetik başlık/altyazı, lower-third. Saydam/overlay çıktıyı make_reel çıktısının üstüne ffmpeg overlay ile bindir.
- Test: `/home/user/work/repos/hf_test.mp4` (1080x1920, 3 sn, Eski Kebap logo fade-in; kaynak proje `/home/user/work/repos/hf_test_proj`).
- Not: Skill içindeki `npx hyperframes` yerine global `hyperframes` kullan (plugin-cli.mjs launcher'ı ağdan npx ister).

## WhisperX (kelime zamanlı döküm, CPU) — v3.8.7rc1
- Yol: `/home/user/work/repos/whisperx-venv/bin/python` (ayrı venv; faster-whisper kurulumunu bozmaz), klon `/home/user/work/repos/whisperX`, sarmalayıcı `/home/user/work/repos/whisperx_tr.py`
- Çağrı: `OMP_NUM_THREADS=4 HF_HUB_DISABLE_XET=1 /home/user/work/repos/whisperx-venv/bin/python -I /home/user/work/repos/whisperx_tr.py klip.mp4 out.json`
- Ne için: wav2vec2 (mpoyraz tr) ile zorla hizalama → daha oturaklı kelime başlangıç/bitişleri (altyazı, kelime vurgusu). Çıktı: `{"text","words":[{word,start,end,score}]}`.
- Test C0878 (6.7 sn): ~45 sn toplam (model yükleme 17 sn + döküm 27 sn). Metin doğru: "İyiyim abi, elhamdülillah." (5.22–5.90 sn).
- Uyarılar: `OMP_NUM_THREADS=4` + `batch_size=1` ŞART (yoksa ~2 dk). Çok kısık konuşmada varsayılan VAD kaçırıyor ("Altyazı M.K" halüsinasyonu) → sarmalayıcı VAD eşiğini 0.1'e indirir ve sesi normalize eder; `score` düşükse (<0.3) zamanları faster-whisper'la karşılaştır. Silero VAD kullanılamaz (github.com torch.hub engelli). Rutin döküm için `scripts/index_clips.py` (faster-whisper) hâlâ 8 sn'de biter; WhisperX'i sadece altyazı zamanlaması kritik olunca kullan.
- punkt_tab için bir kez: `NLTK_ALLOW_PROXIED_URLOPEN=1 .../whisperx-venv/bin/python -c "import nltk;nltk.download('punkt_tab')"` (yapıldı).

## İkinci beyin (avenoxbeyin v3.15.0)
- Vault: `/home/user/work/beyin/` (durum dizini `/home/user/work/beyin-state/`), klon `/home/user/work/repos/avenoxbeyin`
- Çağrı: `cd /home/user/work/beyin && python3 beyin.py note-create --file n.json` (JSON `{"source":"knowledge/x.md","text":"# ...","metadata":{"title":"..."}}`) ; `python3 beyin.py context "sorgu" --no-sync` ; `python3 beyin.py doctor`
- Ne için: mekan başına kalıcı hafıza (marka kararları, müşteri geri bildirimi, "bu akımı kullandık"). Oturum başı hook'lar yalnızca Claude Code'u vault klasöründe açınca çalışır (`.claude/settings.local.json` vault içinde; global ayara dokunulmadı). Mun projesinden kullanmak için komutları elle çağır.
- Test: not oluşturuldu, `context` ile geri okundu.

## SFX kitleri — `/home/user/work/sfx/`
- Kategoriler: whoosh, transition_cinematik, pop, ding_zil, sizzle_pisirme, bicak_kesme, ates, kamera_shutter, riser, impact_hit, klik_yazi, yeme_gevrek, sparkle, kutlama_para, tone_diger (toplam ~274 dosya). Kaynak + lisans: `/home/user/work/sfx/LISANS.md` (Mixkit ücretsiz lisans + CC0 GitHub paketleri).
- Çağrı: `ffmpeg -i reel.mp4 -i /home/user/work/sfx/whoosh/mixkit_1489_air_woosh.mp3 -filter_complex "[1:a]adelay=2300|2300,volume=0.7[s];[0:a][s]amix=inputs=2:normalize=0" ...` (adelay ms cinsinden kesme anı)
- Ne için: kesme/başlık geçişinde whoosh, metin belirişinde pop, ürün kesitinde sizzle/bıçak, outro logo için ding/riser, fotoğraf geçişinde shutter. Mixkit dosyaları tek başına yeniden dağıtılmamalı (videoya gömmek serbest).

## Alınan/atlanan skill'ler
- Alındı: `hyperframes`, `hyperframes-cli`, `media-use` (heygen-com/hyperframes `skills/`).
- Alınmadı: avenoxskills (YouTube uzun-form, mlx-whisper/mac, Avenox markasına özel), avenox-video-kurgu-notlari (genel metodoloji, ajansa özel iş yok), herk-edit-kit (Nate'in konuşan-kafa/ElevenLabs/Kie hattı, repo içi docs'a bağımlı; SFX-senkron fikri için `short-form-edit` referans okunabilir: `/home/user/work/repos/herk-edit-kit/.claude/skills/short-form-edit/`).
