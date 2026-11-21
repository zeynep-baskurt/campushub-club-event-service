# CampusHub - Club & Event Service (Grup 3)

CampusHub platformu icin kulup ve etkinlik yonetimini saglayan mikroservis.
Yeni etkinlikler olusturulurken AI Service (Grup 5) ile otomatik kategorize edilir.

- **Dil / framework:** Python 3.11+, FastAPI, SQLAlchemy, httpx
- **Port:** 8003
- **API sozlesmesi:** [docs/api-contract.md](docs/api-contract.md)

## Calistirma

### Docker

```bash
docker compose up --build -d
```

### Lokal

```bash
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env          # Linux/macOS: cp .env.example .env
uvicorn app.main:app --reload --port 8003
```

AI servisi lokalde calismiyorsa `.env` icinde `AI_ENABLED=false` yapilabilir; etkinlikler `OTHER` kategorisiyle olusur.

- Health Check: http://localhost:8003/health
- Bagimli servisler: http://localhost:8003/health/dependencies
- API Docs (Swagger): http://localhost:8003/docs

## Testler

```bash
pytest -q
```

Testler gercek AI servisine ihtiyac duymaz; AI sahte bir client ile taklit edilir
(calisiyor / kapali / timeout / bozuk cevap senaryolari).

## Environment variable'lar

| Degisken | Varsayilan | Aciklama |
|---|---|---|
| `APP_PORT` | `8003` | Servis portu |
| `DATABASE_URL` | `sqlite:///./campushub_events.db` | Veritabani baglantisi |
| `AI_SERVICE_URL` | `http://ai-service:8005` | AI Inference Service adresi |
| `AI_TIMEOUT_SECONDS` | `3` | AI cagrisi icin zaman asimi |
| `AI_ENABLED` | `true` | `false` ise AI hic cagrilmaz |
| `CORS_ORIGINS` | `*` | Izin verilen origin'ler (virgulle) |

## Endpoint'ler

| Method | Path | Aciklama |
|---|---|---|
| GET | `/health` | Servis durumu |
| GET | `/health/dependencies` | AI servisinin durumu |
| POST | `/clubs` | Kulup olustur |
| GET | `/clubs` | Kulupleri listele |
| GET | `/clubs/{id}` | Kulup detayi |
| GET | `/clubs/{id}/events` | Kulubun etkinlikleri |
| POST | `/events` | Etkinlik olustur (AI ile kategorize edilir) |
| GET | `/events` | Etkinlikleri listele (`clubId`, `category` filtreleri) |
| GET | `/events/{id}` | Etkinlik detayi (Registration Service kullanir) |

Hatalar ortak formattadir: `{"error": "EVENT_NOT_FOUND", "message": "Event 31 does not exist."}`

## Mimari

```
app/
  main.py            -> uygulamayi kurar (config, AI client, CORS, hata handler'lari, router'lar)
  config.py          -> environment variable'lar
  errors.py          -> ortak hata formati
  clients/ai_client.py -> AI Service ile iletisim (timeout + fallback)
  routers/           -> HTTP katmani
  services/          -> is mantigi
  repositories/      -> veritabani erisimi
  models/ schemas/   -> ORM modelleri ve API semalari
tests/               -> API ve AI entegrasyon testleri
```
