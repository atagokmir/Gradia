# Gradia — Grup Değerlendirme Sistemi

Django tabanlı peer evaluation (grup değerlendirme) uygulaması.

## Özellikler

- Öğrenciler aktif anketler üzerinden grup arkadaşlarını değerlendirir
- Admin paneli: grup, öğrenci, anket yönetimi
- Excel ile toplu öğrenci içe aktarma
- Excel sonuç dışa aktarma (özet + detay)
- TailwindCSS ile modern arayüz
- Docker + Nginx + PostgreSQL production kurulumu

## Kurulum

### 1. Ortam Dosyası

```bash
cp .env.example .env
# SECRET_KEY değerini değiştirin!
```

### 2. SSL Sertifikası (Self-signed)

```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=localhost"
```

### 3. Docker ile Başlat

```bash
docker-compose up --build -d
```

### 4. Veritabanı Migrasyonları

```bash
docker-compose exec web python manage.py migrate
```

### 5. Superuser Oluştur

```bash
docker-compose exec web python manage.py createsuperuser
```

### 6. Erişim

| URL | Açıklama |
|-----|----------|
| `https://localhost` | Öğrenci girişi |
| `https://localhost/admin-panel/dashboard/` | Admin paneli |
| `https://localhost/gizli-x9k2m/` | Django admin |

## Local Geliştirme (Docker'sız)

```bash
pip install -r requirements.txt
# .env dosyasını yerel veritabanına göre düzenle (SQLite desteklenir)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Excel İçe Aktarma Formatı

| Kolon | Açıklama |
|-------|----------|
| `ad_soyad` | Ad ve soyad (boşlukla ayrılmış) |
| `kullanici_adi` | Giriş kullanıcı adı |
| `ogrenci_no` | Öğrenci numarası (şifre olarak kullanılır) |
| `grup` | Grup adı (yoksa otomatik oluşturulur) |

## Kullanım Akışı

1. Admin panelinden grupları oluşturun
2. Öğrencileri ekleyin (tek tek veya Excel ile)
3. Öğrencileri gruplara atayın
4. Anket oluşturun ve aktif edin
5. Öğrenciler `https://localhost` üzerinden giriş yaparak değerlendirme yapar
6. Sonuçlar → anket seçin → Excel olarak indirin

## Teknolojiler

- Python 3.12 / Django 5.0
- PostgreSQL 16
- Gunicorn + Nginx
- TailwindCSS (CDN)
- openpyxl (Excel)
- Docker Compose
