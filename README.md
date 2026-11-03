# The Incredible Adventures of Van Helsing - Türkçe Yama

![The Incredible Adventures of Van Helsing](https://img.shields.io/badge/Oyun-The%20Incredible%20Adventures%20of%20Van%20Helsing-red.svg)
![Sürüm](https://img.shields.io/badge/S%C3%BCr%C3%BCm-v1.0-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Steam%20(PC)-orange.svg)
![Durum](https://img.shields.io/badge/Durum-%C3%87al%C4%B1%C5%9F%C4%B1yor-brightgreen.svg)

**The Incredible Adventures of Van Helsing (Steam Sürümü)** için özel olarak geliştirilmiş, %100 uyumlu Türkçe yama paketi.

---

## 📌 Neden İnternetteki Diğer Yamalar Çalışmıyor?

Oyun için internette dolaşan eski Türkçe yamaların güncel Steam sürümünde çalışmamasının ve oyunu çökertmesinin temel teknik nedenleri:
1. **SDBM Hash & İkili Arama (Binary Search) Algoritması:** Oyun motoru (Neocore Games), dil arşivindeki (`.N2PK`) dosya tablosunu `SDBM` algoritması ile hash'ler ve çalışma zamanında dosyaları **sıralı ikili arama** ile bulur. Eski yamalar bu sıralamayı bozduğu için oyun motoru dil dosyalarını bulamaz ve çöker.
2. **Steam Dil Kilidi:** Oyun Steam üzerinden sadece `"english"` dilini sorgular. Eski yamaların oluşturduğu `Strings/Turkish` klasörü oyun tarafından hiçbir zaman okunmaz. Bu yamada doğrudan varsayılan paket mimarisi güncellenmiştir.
3. **Yazı Tipi (Font) Kısıtı:** Oyunun dahili fontları Türkçe özel karakterleri (ş, ğ, ı, ç, ö, ü) desteklemediğinden kutucuk/soru işareti hataları oluşur. Bu yamada karakterler temiz ASCII karşılıklarına (`s, g, i, c, o, u`) dönüştürülerek görsel bozulmalar %100 engellenmiştir.

---

## ⚔️ Yama Özellikleri & Kuralları

- **Görevler (Quests):** Tüm ana ve yan görev isimleri, özetleri ve görev hedefleri Türkçeleştirildi.
- **Diyaloglar:** Tüm NPC konuşmaları, Lady Katarina ile Van Helsing arasındaki eğlenceli atışmalar Türkçeleştirildi.
- **Sinematikler:** Giriş (`intro.srt`), bölüm geçişi (`chapter1_vege.srt`) ve kapanış (`outro.srt`) video altyazıları Türkçeleştirildi.
- **Özel İsimler Orijinal:** *Van Helsing, Lady Katarina, Borgova, Ink, Vlados, Beggar King, Fulmigatis* gibi karakter ve mekan adları bozulmadan korundu.
- **Eşya ve Yetenek İsimleri Orijinal:** Build rehberleri ve uluslararası oyuncu topluluğu ile uyum için eşya ve yetenek isimleri İngilizce bırakıldı.
- **Eşya ve Yetenek Açıklamaları:** Eşyaların ve yeteneklerin tüm açıklamaları, bonusları ve istatistik etkileri Türkçeleştirildi.
- **Güvenli Karakter Seti:** Tüm metinler oyun fontuyla kusursuz çalışan ASCII karakterleriyle kodlandı.

---

## 🚀 Kurulum

### Yöntem 1: Tek Tık Otomatik Kurulum (Önerilen)
1. Bu depoyu indirin (`Code` -> `Download ZIP`) ve bir klasöre çıkartın.
2. `Kurulum.bat` dosyasına çift tıklayın.
3. Betik oyun dizininizi otomatik tespit eder, orijinal dil dosyanızı yedekler (`Files.N2PK.original_backup`) ve yamayı yükler.
4. Oyunu Steam üzerinden başlatıp keyifle oynayın!

### Yöntem 2: Manuel Kurulum
1. `Files.N2PK` dosyasını oyunun kurulu olduğu dizindeki `Strings/` klasörüne kopyalayın (eski dosyanın yedeğini alın).
   - Örnek: `C:\Program Files (x86)\Steam\steamapps\common\The Incredible Adventures of Van Helsing\Strings\Files.N2PK`
2. `Videos/ENG/` klasöründeki `.srt` dosyalarını oyunun `Videos/ENG/` klasörüne kopyalayın.

---

## 🔄 Yamayı Kaldırma

Orijinal İngilizce diline dönmek için:
- `Kaldir.bat` dosyasına çift tıklayın; otomatik olarak orijinal yedeğiniz geri yüklenir.
- Veya Steam Kütüphanesinden oyuna sağ tıklayıp **Özellikler -> Yüklü Dosyalar -> Oyun dosyalarının bütünlüğünü doğrula** deyin.

---

## 🛠️ Geliştirici Araçları (`tools/`)

Geliştiriciler ve mod yapımcıları için `tools/` klasöründe:
- `n2pk_tool.py`: Neocore `.N2PK` arşivlerini açma (extract) ve SDBM hash tablosuyla yeniden paketleme (pack) aracı.
- `apply_patch.py`: Çeviri önbelleğini XML dosyalarına uygulayan ve arşivleyen betik.
- `translation_cache.json`: Tüm oyun içi metinlerin Türkçe çeviri veritabanı.

---

## 📄 Lisans

Bu proje açık kaynaklıdır ve [MIT Lisansı](LICENSE) altında sunulmaktadır.
