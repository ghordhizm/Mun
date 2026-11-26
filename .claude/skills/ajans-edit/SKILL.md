---
name: ajans-edit
description: Restoran/kafe/tatlıcı müşterileri için aylık sosyal medya üretimi — çekim planı (Word/Excel/PDF) okuma ve yazma, Instagram referans videolarını indirip analiz etme, ham çekimden Reels kurgulama (altyazı, müzik, outro), marka stiline uygun post tasarlama ve içerik planı PDF'i hazırlama. Ajansın mekanlarıyla (Huzur Pide, Deniz Lokantası, Mix Lab, Doktorun Yeri, Eski Kebap, Yiğit Öz Kasap vb.) ilgili her işte kullan.
---

# Ajans Edit

Kullanıcı bir ajansta editör. ~8-10 yemek mekanı (kebapçı, pideci, çorbacı, tatlıcı, kasap…) için her ay çekim yapılıyor: mekan başına ~10-15 Reels, ~10 post, story'ler ve 1 röportaj (5-10 soru, her soru ayrı kısa video).
Kullanıcı iPad'den çalışır: **kısa cevap ver, sadece sonucu söyle.** Uzun özet/tablo yazma.

## 1. Girdiler
- **Çekim planı** (Word/Excel/PDF): her madde = 1 içerik. Format: `N-) Fikir adı: ne çekilecek, nasıl kurgulanacak. Referans video: <instagram linki>`. Excel'de aynı bilgi satır satır (içerik no, tür, açıklama, referans link). Okumak için docx/xlsx skill'lerini veya python kullan; istenirse aynı formatta yaz.
- **Ham çekim:** SwissTransfer / SendGB / WeTransfer / Drive linki. 4K, 50fps, çoğu dikey (rotation=90). Dosya sırası = çekim sırası; kullanıcı WhatsApp ss'i ile "hangi klip hangi içerik" bilgisini verebilir.
- **Marka:** logo, renkler, font → `brands/<mekan>.json`. Yoksa logodan renk çıkar, önerip onay al, json'ı oluştur.

## 2. İş akışı
1. Planı oku → içerik listesi. Referans linkleri indir (`yt-dlp -f b`; Instagram foto postları indirilemez → kullanıcıdan ss iste).
2. Referansları **kare kare izle** (ffmpeg tile sheet) + sesi yazıya dök. Açıklamayı videonun gerçek içeriğine göre yorumla.
3. Ham çekimi indir (`scripts/st_dl.py` SwissTransfer, `scripts/sendgb_dl.js` SendGB) → `scripts/index_clips.py` ile her klibe Whisper (faster-whisper medium, tr, `HF_HUB_DISABLE_XET=1`) dökümü + kare sheet.
4. Klip ↔ içerik eşleştirme tablosu çıkar (kısa), sonra kurguya geç.
5. Reels: `scripts/make_reel.py spec.json` (spec örneği aşağıda). Her render sonrası `scripts/chk.sh` ile kareleri **kendin kontrol et**, sonra gönder.
6. Postlar: HTML+Playwright ile 1080×1350 render. Önce 1 tane yap, onay al, sonra hepsini.
7. Dosyalar 3MB'tan büyükse Drive bağlantısından geçmez → SendUserFile ile gönder.

## 3. Reels kuralları (tüm mekanlar)
- **Kurgu:** "3-2-1 oyun", "kayıt", "bir daha", yönetmen konuşmaları, fail/tekrar çekimleri KESİLİR. Klip tam ilk repliğin başladığı yerden başlar; diğer kişi konuşmaya başlamadan kesilir. Konuşmasız aksiyon 1.1-1.3x hızlanabilir, vurgu anında punch-in zoom.
- **Yatay klip asla dikeye gerilmez** (make_reel otomatik crop yapar ama tercihen dikey alternatif kullan).
- **Altyazı:** her konuşmalı videoda var. Metni Whisper'dan al ama **kelime kelime kontrol et** (rakamlar rakamla: "Masa 12", "Masa 8'in"). Altyazılar **asla üst üste binmez**; bir satır bitmeden diğeri gelmez; noktalama işaretinden böl. Stil markaya göre (`brands/*.json` → `sub`).
- **Başlık (üstte):** markanın rengi/fontu, Instagram güvenli alanı içinde (y≈250px).
- **Outro (her videoda):** arka plan DONMAZ (ham çekimin devamı akar), ~1 sn'de yavaşça bulanıklaşır, sonra logo 1.1 sn'de yavaşça belirir (+varsa slogan), ses 2.6 sn'de kısılır.
- **Müzik:**
  - Referansta viral bir ses varsa → o ses birebir kullanılır (dudak senkronu; ham çekimde ses yoksa ağız hareketine göre hizala). Ekstra müzik yok. Telif dikkate alınmaz.
  - Orijinal sesli (konuşmalı) skeç → arkaya hafif, konuya uygun (komikse komik) telifsiz müzik; konuşmada otomatik kısılır (`"duck":true`).
  - Konuşmasız ürün/mekan videosu → telifsiz müzik, kesmeler vuruşa denk (librosa beat).
  - Telifsiz kaynak: Mixkit (`assets.mixkit.co/music/<id>/<id>.mp3`). FreePD kapandı.
- **Ses:** gürültü temizleme, -14 LUFS.
- Kullanıcı dudak senkronunu kendisi yapmak isterse: başlıklı/altyazısız/outrosuz video + ses MP3 + ham klip (1080p) gönder.

## 4. Post kuralları (tüm mekanlar)
- 1080×1350 (4:5). **Logo her postta orta altta, aynı boyut ve konum.**
- Her mekanın **kendi tasarım dili** var (`brands/*.json` → `post`). Referans posta bakıp ondan esinlen, ama mekanın renk/fontunda, tutarlı bir template ile.
- Gerçek çekim fotoğrafı kullan; **aynı fotoğrafı farklı postlarda tekrar kullanma**. Fotoğraf yoksa video karesi çek (iştah açıcı an: peynir uzaması, ısırma, dolu masa).
- Ürünler iştah açıcı: renk/kontrast/doygunluk + keskinleştirme; yuvarlak ürünler grabCut + fitEllipse ile **tam daireye** çevrilir, hepsi aynı boyut.
- **Kase/tabak ürünler kasenin dış kenarından kesilir**: alt tabak, masa, örtü ASLA görünmez (radyal kenar tespiti: çorba elipsi → kase kenarı). Yandan çekilmiş kase kullanma.
- Post konsepti net olmalı (ör. ChatGPT postu: "daha iyi hale getir" → iki pide).
- Yapay zeka görsel (GPT Image/Higgsfield) sadece kredi varsa; yoksa kendin düzenle ve söyle.

## 5. İçerik planı PDF'i (yeni mekan)
- Kapak (mekan fotoğrafı) → "Bu ay neye odaklanıyoruz?" (4 madde, sade, övgüsüz) → 15 Reels → 10 post → 5 röportaj sorusu (+"cevapta vurgulanacak").
- Metin müşteri okuyacak: profesyonel ama yapay/övgü kokmayan dil. Menüdeki gerçek ürünleri kullan.
- Reels dağılımı (kullanıcı tercihi): ürünlerin baştan sona hazırlanışı (≥3-6), mekan tanıtımı (2: dıştan içeri, ocak/tezgahtan salona), kalanı akım. Daha önce kullanılan akım referanslarını tekrar etme. Referans sadece akımlarda; diğerleri yazıyla.
- Instagram linkleri **orijinal paylaşım linkiyle** (`?igsh=` / `?xxxx=` parametreli) tıklanabilir olmalı.

## 6. Spec örneği (make_reel.py)
```json
{"out":"/abs/OUT.mp4","raw":"/abs/raw","brand":".claude/skills/ajans-edit/brands/huzur_pide.json",
 "fonts_dir":".claude/skills/ajans-edit/fonts",
 "title":["SATIR 1","SATIR 2"],
 "segments":[{"clip":"C0705","in":4.85,"out":7.0},{"clip":"C0766","in":20.2,"out":23.7,"zoom":[1.3,0.5,0.42]},
             {"clip":"C0722","in":28.3,"out":37.7,"mute":true,"speed":1.0,"bw":false}],
 "subs":[{"clip":"C0705","end":7.0,"words":[["USTA,",4.9],["MASA",5.66],["12",5.78],["ACİL!",6.42]]}],
 "outro":{"clip":"C0766","in":23.7,"dur":2.6,"mute_audio":true},
 "music":{"file":"/abs/music.mp3","start":0,"vol":0.35,"duck":true}}
```
Bellek: segment başına ayrı seek'li input kullanılır (4K'da tek input'u çok kez trim'lemek OOM yapar).

## 7. Ortam notları
- Ağ izinleri ortamda kalıcı: instagram, cdninstagram (ord5-1/2/3), swisstransfer (+ storage host'ları her transferde değişebilir → yeni host gerekirse update_environment), sendgb + api.sendgb.com, huggingface + us.aws.cdn.hf.co, mixkit, wikimedia.
- Drive bağlantısı dosya başına ~3MB; büyük dosyalar SendUserFile ile.
- Kullanıcının medya ekibi Drive'ına dokunma; sadece "AJANS EDİT (Claude)" klasörü.
