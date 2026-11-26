# Birebir tarifler (kullanıcının çok beğendiği iki video) – yeni Claude AYNEN uygulasın

## A) CUMA / CUMARTESİ / PAZAR (kâğıt çekilince altından yazı çıkar)
Dosya: `sablonlar/deniz_p08_build.py` (çalışan kod; sadece klip adları/yolları değiştir).
Mantık:
1. 3 klip (her biri: masada kâğıt üstünde ürün, kâğıt çekiliyor). Her klipten **1080×640 yatay bant** kesilir (`scale=1080:1920,crop=1080:640:0:Y0`, Y0 ürün+kâğıt banda girecek şekilde, Deniz'de 470). 3 bant alt alta = 1080×1920. Bantlar arasında 6px krem çizgi.
2. **Sıralı çekiliş:** bant 1 → 2 → 3 sırayla çekilsin diye her klibin başına "ilk kareyi bekletme" (pad) eklenir: `bands=[(klip, pad_sn, 'CUMA'), …]` (Deniz: 0.8 / 0.0 / 1.9). Sahne statik olduğu için bekletme fark edilmez.
3. **YAZI KÂĞIDIN ALTINDAN ÇIKAR (asıl numara):** her kare için maske = "bu piksel klibin SON karesine (boş masa) benziyor mu" → `dd=|kare-son_kare|` ortalaması, `mask=clip((40-dd)/20,0,1)`, açma (9×9) + hafif blur. Yazı sadece maske=1 yerlerde çizilir → kâğıt/kase geçerken yazının üstünü örter, çekildikçe yazı ortaya çıkar. (Renk/HSV maskesi KULLANMA: çorba da turuncu, yazı kasenin üstüne biner – denendi, bozuk.)
4. Yazı: DM Serif Display 150px, krem beyaz (255,248,236), hafif gölge; bant ortasının biraz altına.
5. Hepsi açıldıktan sonra ~1.5 sn bekle → outro (krem kart yavaşça + logo). Müzik: telifsiz, sakin (Deniz'de mk_540 handpan). Toplam ~12 sn.
Kontrol: çekiliş anında bir kare al – yazı kâğıdın/kasenin ÜSTÜNE binmemeli, sadece boş masada görünmeli.

## B) SOFRAYA/ZEMİNE SIRAYLA DİZİLİŞ (isimler yazılı, ürünler tek tek konur)
Dosya: `sablonlar/deniz_p03_sofraya_dizilis_spec.json` + `deniz_p03_names.png` (make_reel.py ile render).
Mantık:
1. Tek uzun klip: tepeden, beyaz/düz zemine ürünler TEK TEK konuyor (Deniz C0818, 23 sn). Yatay 4K ise `"rot":1` (90° döndür, germe yok).
2. Hız `speed 1.7` (6 tabak ~13 sn'ye iner). Başı tam ilk tabak konarken başlasın (`in 0.0`), son tabak konunca body biter; outro aynı klibin devamında (make_reel otomatik yavaşlatır, donmaz).
3. **İsim katmanı:** klibin SON karesini al (`ffmpeg -sseof -0.5 … -vf transpose=1,scale=1080:1920 lastr.png`), `cv2.HoughCircles` (minR 140, maxR 230) ile tabak merkezlerini bul, her tabağın ALTINA (y = cy + r + 18) ismini yaz (DM Serif 50px, lacivert/marka rengi) → şeffaf 1080×1920 PNG. Spec'te `overlays:[{img:names.png, clip, in, out, full:true, nofade:true}]` → isimler baştan beri zeminde yazılı, tabaklar üstüne gelir.
4. Başlık yok; müzik referans sesi (varsa) yoksa telifsiz. İsimler tahminse kullanıcıya "teyit et" de.
Eski Kebap'ta: "Mezeler yerine" (haydari, ezme, havuç tarator, çoban salata, soğan, içli köfte) ve "sofra kuruldu" bunun aynısı.

## C) NE ARZU EDERSİNİZ (mekan + ortada hızlı değişen ürünler)
`sablonlar/deniz_p07_ne_arzu_spec.json`: mekan geniş plan klip; üstte "Ne arzu" (DM Serif 110), altta "edersiniz?" (Playfair italik) tam ekran PNG; ortada kasenin kenarından kesik ürün png'leri `size 470, y 400`, **ilk kareden itibaren** her biri **0.25 sn** (`nofade:true`, arada boşluk yok), video boyunca döner.
