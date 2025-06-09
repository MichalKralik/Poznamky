# Poznámky - Šifrovaná webová aplikace pro správu poznámek

Poznámky je bezpečná webová aplikace pro ukládání a sdílení šifrovaných textových poznámek s funkcí automatické expirace a jednorázového zobrazení.

## Funkce

- **Šifrování poznámek**: Všechny poznámky jsou šifrovány pomocí AES-256 před uložením do databáze
- **Automatická expirace**: Nastavte dobu platnosti poznámek (hodina, den, týden)
- **Jednorázové poznámky**: Poznámky, které se automaticky smažou po prvním přečtení
- **Sdílení přes odkazy**: Bezpečné sdílení jednorázových poznámek pomocí unikátních odkazů
- **REST API**: Kompletní API pro programový přístup k funkcím aplikace
- **JWT autentizace**: Zabezpečené API pomocí JWT tokenů

## Technologie

- **Backend**: Flask, SQLAlchemy
- **Databáze**: SQLite/PostgreSQL
- **Šifrování**: AES-256 (pycryptodome)
- **Autentizace**: Flask-Login, Flask-JWT-Extended
- **Background tasky**: Celery s Redis
- **Frontend**: Bootstrap, Jinja2 templates

## Instalace

1. Klonujte repozitář:
   ```
   git clone https://github.com/vaše-uživatelské-jméno/poznámky.git
   cd poznámky
   ```

2. Vytvořte a aktivujte virtuální prostředí:
   ```
   python -m venv venv
   source venv/bin/activate  # Pro Linux/Mac
   venv\Scripts\activate     # Pro Windows
   ```

3. Nainstalujte závislosti:
   ```
   pip install -r requirements.txt
   ```

4. Inicializujte databázi:
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. Spusťte Redis (potřebný pro Celery):
   - Pro Windows: Stáhněte a nainstalujte [Redis pro Windows](https://github.com/tporadowski/redis/releases)
   - Pro Linux/Mac: `sudo apt install redis-server` nebo `brew install redis`

## Spuštění aplikace

1. Spusťte Redis server:
   ```
   redis-server
   ```

2. Spusťte Celery worker v novém terminálu:
   ```
   celery -A celery_worker.celery worker --pool=solo --loglevel=info
   ```

3. Spusťte Flask aplikaci v dalším terminálu:
   ```
   flask run
   ```

4. Otevřete aplikaci v prohlížeči: http://127.0.0.1:5000/

## API dokumentace

### Autentizace

```
POST /api/login
```
Tělo požadavku:
```json
{
  "email": "uzivatel@example.com",
  "password": "heslo123"
}
```
Odpověď:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### Získání všech poznámek

```
GET /api/notes
Header: Authorization: Bearer {access_token}
```

### Vytvoření nové poznámky

```
POST /api/notes
Header: Authorization: Bearer {access_token}
```
Tělo požadavku:
```json
{
  "content": "Obsah poznámky",
  "expiration": "day", // "hour", "day", "week", "never"
  "is_one_time": false // true pro jednorázovou poznámku
}
```

## Zabezpečení

- Všechna hesla jsou hashována pomocí bcrypt
- Obsah poznámek je šifrován pomocí AES-256
- Implementace rate limiting pro prevenci brute-force útoků
- CSRF ochrana pro zabezpečení formulářů

## Licence

MIT License
