# 🌐 AI Destekli Otomatik Web Sitesi Oluşturma Sistemi
### **autoWebBuilder – Yapay Zekâ ile Anında Profesyonel Web Siteleri Oluşturun**

---

## 📑 İçindekiler
- [📘 Proje Özeti](#-proje-özeti)
- [🚀 Temel Özellikler](#-temel-özellikler)
- [🏗 Sistem Mimarisi](#-sistem-mimarisi)
- [🔑 Kullanıcı Akışı](#-kullanıcı-akışı)
- [🧠 Yapay Zekâ ile Şablon Üretimi](#-yapay-zekâ-ile-şablon-üretimi)
- [🎨 Site Düzenleme Modülü](#-site-düzenleme-modülü)
- [📁 Klasör Yapısı](#-klasör-yapısı)
- [⚙️ Teknik Bileşenler](#️-teknik-bileşenler)
- [🖼 Akış Diyagramları](#-akış-diyagramları)
- [💾 Kurulum ve Çalıştırma](#-kurulum-ve-çalıştırma)
- [📝 Lisans](#-lisans)

---

## 📘 Proje Özeti

**autoWebBuilder**, kullanıcının yalnızca tema konusunu yazarak **3 farklı yapay zekâ tabanlı modern web sitesi tasarımı** üreten bir tam otomatik web sitesi oluşturma platformudur.

Sistem;  
✔ Gemini API ile HTML+CSS üretir  
✔ Kullanıcıya özel klasörlerde siteleri saklar  
✔ Önizleme ve düzenleme sağlar  
✔ Düzenlenen siteleri zip olarak indirilebilir yapar  
✔ Kullanıcı bazında profil & kayıt sistemi içerir  

Hiçbir kod bilgisine gerek olmadan profesyonel web sitesi üretmeyi sağlar.

---

##  Temel Özellikler

### ** Yapay Zekâ ile 3 Farklı Tema Üretimi**
- Her tema tamamen farklı HTML + CSS yapısına sahiptir.
- Navbar, Hero Section, Content Sections, Footer içerir.

### ** Gelişmiş Site Düzenleme Paneli**
Kullanıcı siteyi şu açılardan düzenleyebilir:
- Logo değiştirme  
- Tema renkleri  
- Arka plan renkleri  
- Yazı tipi & font ailesi  
- Kalın, italik, altı çizili metin  
- Yeni bölüm / section ekleme  
- Doğrudan HTML kodu üzerinde düzenleme  

### ** Kullanıcıya Özel Dosya Yönetimi**
- Her kullanıcı kendi UID klasörüne sahiptir.
- Orijinal ve edited siteler ayrı saklanır.

### ** Zip Olarak İndirme**
- Kullanıcı düzenlediği veya orijinal siteyi .zip olarak indirebilir.

### ** Profil & Kaydedilen Siteler**
- Kullanıcıya ait tüm siteler listelenir.
- Düzenlenmiş sürümler ayrı olarak gösterilir.

---
Flask Backend
│
├── Yapay Zekâ Modülü (Gemini API)
├── Firebase Authentication (Email/Password Login)
└── Dinamik Site Üretim Motoru
├── HTML/CSS Render
├── Görsel Üretici
├── Metadata Sistemi
└── Zip Exporter

##  Kullanıcı Akışı
[1] Kayıt / Giriş
<img width="493" height="412" alt="image" src="https://github.com/user-attachments/assets/7aa13281-5684-42ba-8d60-a8e0ef205839" /> 
<img width="484" height="402" alt="image" src="https://github.com/user-attachments/assets/b45a5f4f-0fc4-46c5-89af-6c55649b3ee6" />


↓
[2] Ana Sayfa → Konu Girilir
<img width="1214" height="316" alt="image" src="https://github.com/user-attachments/assets/95fbf76a-0ad9-40c6-a870-4235e314a1c1" />

↓
[3] Gemini API → 3 Site Üretilir
<img width="1121" height="892" alt="image" src="https://github.com/user-attachments/assets/be789332-da83-4805-8601-17d3927ccc56" />

↓
[4] Kullanıcı Önizleme / Düzenleme / İndirme
<img width="1862" height="881" alt="image" src="https://github.com/user-attachments/assets/98585eba-f437-423b-901f-9e5da96726f3" />

↓
[5] Değişiklikler edited klasörüne kaydedilir

<img width="1038" height="415" alt="image" src="https://github.com/user-attachments/assets/074b7cfb-7ee8-408f-8c46-6bcdb555c572" />

↓
[6] Profil & Kaydedilen Sitelerden yönetim yapılır

<img width="827" height="868" alt="image" src="https://github.com/user-attachments/assets/496168a5-abc3-4e88-be30-cb8699f173e5" />


---

##  Yapay Zekâ ile Şablon Üretimi

Yapay zekâdan istenen çıktı:

[
  {
    "id": 1,
    "name": "Modern Tema",
    "description": "Minimalist ve kurumsal görünüm",
    "html": "<!DOCTYPE html>...",
    "css": "body { font-family: Arial; }"
  },
  ...
]

##  Sistem Mimarisi

Sistem:

HTML & CSS dosyalarını kaydeder

Görselleri otomatik ekler

Metadata oluşturur

##Site Düzenleme Modülü
Kullanıcı düzenleme ekranında:

Biçimlendirme Araçları

Bold

Italic

Underline

Font Değiştirme

Renk Picker

Arka Plan Değiştirme

HTML Yapısal Araçlar

Yeni bölüm ekleme

Mevcut bölümü silme

Kod düzenleme modu

Logo Yükleme

Herhangi bir PNG/JPG yüklenip sayfaya uygulanabilir.

## Kaydetme Süreci
original site  →  edited copy oluşturulur
                  generated_sites/<user>/edited/<site>_edited
## Klasör Yapısı
generated_sites/
   └── <user_id>/
        ├── <site_id>/
        │     ├── index.html
        │     ├── style.css
        │     ├── images/
        │     └── metadata.json
        │
        └── edited/
              └── <site_id>_edited/
                     ├── index.html
                     ├── style.css
                     ├── images/
                     └── metadata.json
                     
## Teknik Bileşenler

| Bileşen        | Teknoloji                          |
| -------------- | ---------------------------------- |
| Backend        | Flask (Python)                     |
| Yapay Zekâ     | Google Gemini API (2.5 Flash)      |
| Authentication | Firebase Authentication            |
| Veri           | JSON + Dosya Sistemi               |
| Frontend       | HTML + CSS + JavaScript            |
| Görseller      | Unsplash source (konuya özel)      |
| Güvenlik       | .env + gitignore secret management |
| Oturum         | Flask Session                      |

## Genel Sistem Diyagramı

Kullanıcı
   ↓
Flask Backend
   ↓
Gemini API → HTML/CSS üretimi
   ↓
Site Dosyaları → generated_sites/
   ↓
Önizleme / Düzenleme / İndirme

##Düzenleme Kaydetme Süreci

[1] Kullanıcı siteyi düzenler
      ↓
[2] HTML içerik JSON olarak backend’e gönderilir
      ↓
[3] Orijinal site kopyalanır
      ↓
[4] edited/<site_id>_edited/ klasörüne yazılır
      ↓
[5] metadata.json güncellenir

##Zip İndirme Süreci
[İstek] GET /download/<site_id>
      ↓
Klasör diskten okunur
      ↓
Zip arşivi oluşturulur
      ↓
Kullanıcıya response olarak gönderilir

## Kurulum ve Çalıştırma
1.Depoyu Klonla
git clone https://github.com/kullanici/autoWebBuilder.git
cd autoWebBuilder

2.Sanal Ortam Oluştur
python -m venv .venv
.venv\Scripts\activate

3.Bağımlılıkları Kur
pip install -r requirements.txt

4..env Dosyasını Oluştur
GEMINI_API_KEY=your_api_key_here

5.Firebase Admin Key ekle
Dosya adı firebase_admin_key.json olmalı
ve proje dizininde bulunmalıdır.

6.Uygulamayı Başlat
python app.py

