# Club / Event Service – API Sözleşmesi (Grup 3)

Bu doküman diğer grupların (Gateway, Registration, AI) bu servisle nasıl konuşacağını tanımlar.
`campushub-integration/api-contracts/` altına da kopyalanabilir.
Canlı ve her zaman güncel sürüm: `http://<host>:8003/docs` (Swagger) ve `/openapi.json`.

- **Port:** `8003`
- **Base URL (docker network):** `http://club-event-service:8003`
- **Alan isimleri:** JSON'da camelCase (`clubId`, `startTime`, …)
- **Tarih formatı:** ISO 8601, ör. `2026-12-10T10:00:00`

## Ortak hata formatı

Tüm hatalar aynı gövdeyi döner:

```json
{ "error": "EVENT_NOT_FOUND", "message": "Event 31 does not exist." }
```

| HTTP | `error` | Ne zaman |
|---|---|---|
| 400 | `VALIDATION_ERROR` | Eksik/yanlış alan (ör. `capacity: 0`, geçersiz `startTime`) |
| 400 | `INVALID_CATEGORY` | `GET /events?category=` bilinmeyen kategori |
| 404 | `CLUB_NOT_FOUND` | Kulüp yok |
| 404 | `EVENT_NOT_FOUND` | Etkinlik yok |
| 404 | `NOT_FOUND` | Böyle bir endpoint yok |
| 409 | `CLUB_ALREADY_EXISTS` | Aynı isimde kulüp var |
| 500 | `INTERNAL_ERROR` | Beklenmeyen hata |

## Endpoint'ler

### `GET /health`
```json
{ "service": "club-event-service", "status": "UP", "version": "1.0.0" }
```

### `GET /health/dependencies`
Bağımlı servislerin durumu (entegrasyon sırasında hata ayıklamak için).
```json
[{ "name": "ai-service", "url": "http://ai-service:8005", "status": "UP", "detail": null }]
```
`status`: `UP` | `DOWN` | `DISABLED`

### `POST /clubs` → 201
```json
// istek
{ "name": "Yazılım Kulübü", "description": "Yazılım geliştirme ve teknoloji topluluğu" }
// cevap
{ "id": 7, "name": "Yazılım Kulübü", "description": "...", "createdAt": "2026-11-21T19:28:50" }
```

### `GET /clubs` → 200
```json
[{ "id": 7, "name": "Yazılım Kulübü", "description": "...", "createdAt": "..." }]
```

### `GET /clubs/{id}` → 200 / 404

### `GET /clubs/{id}/events` → 200 / 404
Kulübün etkinlikleri (`EventResponse` listesi). Örn. "Robotik Kulübü'nün etkinlikleri".

### `POST /events` → 201
```json
// istek
{
  "clubId": 7,
  "title": "Python ile Yapay Zeka Atölyesi",
  "description": "Başlangıç seviyesinde Python ve yapay zeka uygulamaları.",
  "startTime": "2026-12-10T10:00:00",
  "capacity": 100
}
// cevap (EventResponse)
{
  "id": 31,
  "clubId": 7,
  "clubName": "Yazılım Kulübü",
  "title": "Python ile Yapay Zeka Atölyesi",
  "description": "Başlangıç seviyesinde Python ve yapay zeka uygulamaları.",
  "startTime": "2026-12-10T10:00:00",
  "capacity": 100,
  "category": "TECHNOLOGY",
  "categoryConfidence": 0.94,
  "createdAt": "2026-11-21T19:28:51"
}
```
`category` AI Service tarafından belirlenir (aşağıya bakın).

### `GET /events` → 200
Query parametreleri (opsiyonel): `clubId`, `category`. `startTime`'a göre sıralı döner.

### `GET /events/{id}` → 200 / 404
**Registration Service (Grup 4)** kayıttan önce bunu çağırır:
- `200` → etkinlik var; `capacity` alanıyla kontenjan kontrol edilebilir.
- `404` + `EVENT_NOT_FOUND` → kayıt reddedilmeli.
- Bağlantı hatası / timeout / `5xx` → Registration Service kullanıcıya "Event service unavailable" benzeri bir hata dönmeli (sonsuz beklememeli).

> Not: Kayıt sayısı bu serviste tutulmaz; kalan kontenjanı Registration Service kendi verisiyle hesaplar.

## Bu servisin çağırdığı servisler

### AI Service (Grup 5) – `POST {AI_SERVICE_URL}/ai/classify`
`POST /events` sırasında başlık + açıklama birleştirilip gönderilir:
```json
// istek
{ "text": "Python ile Yapay Zeka Atölyesi. Başlangıç seviyesinde Python ve yapay zeka uygulamaları." }
// beklenen cevap
{ "category": "TECHNOLOGY", "confidence": 0.91 }
```
Kabul edilen kategoriler: `TECHNOLOGY`, `SPORT`, `ART`, `CAREER`, `SOCIAL`, `OTHER` (büyük/küçük harf fark etmez).

**AI çalışmazsa ne olur?** Etkinlik oluşturma **engellenmez**. Aşağıdaki durumların hepsinde etkinlik
`category: "OTHER"`, `categoryConfidence: null` ile kaydedilir ve `201` döner:

| Durum | Davranış |
|---|---|
| AI servisi kapalı / bağlantı reddedildi | fallback `OTHER` |
| `AI_TIMEOUT_SECONDS` (varsayılan 3 sn) içinde cevap yok | fallback `OTHER` |
| AI `4xx`/`5xx` döndü | fallback `OTHER` |
| JSON değil / bilinmeyen kategori | fallback `OTHER` |
| `confidence` 0–1 dışında | kategori korunur, `categoryConfidence: null` |
| `AI_ENABLED=false` | AI hiç çağrılmaz, `OTHER` |

Her durum servis loglarına `WARNING` olarak yazılır.
