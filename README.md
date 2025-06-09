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

## Ukázky kódu

### Šifrování poznámek

Zde je ukázka, jak aplikace šifruje obsah poznámek pomocí AES-256:

```python
from app.utils.crypto import AESCipher

# Inicializace šifrovacího nástroje
cipher = AESCipher()  # Použije klíč z konfigurace aplikace

# Šifrování textu poznámky
text_poznamky = "Toto je důvěrná poznámka"
ciphertext_b64, iv_b64 = cipher.encrypt(text_poznamky)

# Uložení šifrovaného textu a IV do databáze
note = Note(
    content=ciphertext_b64,
    iv=iv_b64,
    user_id=current_user.id,
    expiration=calculate_expiry_date("day"),
    is_one_time=False
)
db.session.add(note)
db.session.commit()
```

### Dešifrování poznámek

Ukázka načtení a dešifrování poznámky:

```python
from app.utils.crypto import AESCipher

# Získání poznámky z databáze
note = Note.query.get(note_id)

# Dešifrování obsahu
cipher = AESCipher()
decrypted_content = cipher.decrypt(note.content, note.iv)

# Pokud se jedná o jednorázovou poznámku, smazat ji po přečtení
if note.is_one_time:
    db.session.delete(note)
    db.session.commit()
```

### Generování sdíleného odkazu

```python
import secrets
from datetime import datetime, timedelta

def create_share_link(note_id):
    # Generování unikátního tokenu pro sdílení
    token = secrets.token_urlsafe(16)
    
    # Vytvoření záznamu o sdílení
    share = NoteShare(
        note_id=note_id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.session.add(share)
    db.session.commit()
    
    # Vrácení URL pro sdílení
    return f"/share/{token}"
```

## Zabezpečení

- Všechna hesla jsou hashována pomocí bcrypt
- Obsah poznámek je šifrován pomocí AES-256
- Implementace rate limiting pro prevenci brute-force útoků
- CSRF ochrana pro zabezpečení formulářů

## Licence

MIT License
