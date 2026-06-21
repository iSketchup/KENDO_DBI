# API-Dokumentation 



# Inhaltsverzeichnis

- [Projektlaufzeit](#projektlaufzeit-daniels-historie)

- [User-API](#user-api-dokumentation)
  - [GET /user/{username}](#get-userusername)
  - [POST /user/login](#post-userlogin)
  - [POST /user/](#post-user)
  - [PUT /user/](#put-user)
  - [DELETE /user/](#delete-user)

- [Admin-API](#admin-api-dokumentation)
  - [GET /admin/](#get-admin)
  - [GET /admin/{username}](#get-adminusername)
  - [POST /admin/login](#post-adminlogin)
  - [POST /admin/](#post-admin)
  - [PUT /admin/](#put-admin)
  - [DELETE /admin/](#delete-admin)

# Projektlaufzeit (Daniels-Historie)

| Datum | Name | Aufgabe |
| :--- | :--- | :--- |
| Jun 17 2026 | Daniel WALSER | Fehlermeldung ist jetzt im user und Admin für die Suche nach dem Namen vorhanden. |
| Jun 17 2026 | Daniel WALSER | Bug fix. Im Login wird jetzt genauer geprüft, ob das Passwort vorhanden ist. |
| Jun 17 2026 | Daniel WALSER | Bug fix. |
| Jun 17 2026 | Daniel WALSER | Server ip anpassung. |
| Jun 17 2026 | Daniel WALSER | Anpassung vom Admin.py. Hashing ist auf der Server Seite möglich. |
| Jun 17 2026 | Daniel WALSER | Bug Fix. Versuch das SSL sicher zu machen. Im Backend ist es möglich ein hashpasswort zu erzeugen. |
| Jun 16 2026 | Daniel WALSER | Bug fix. |
| Jun 16 2026 | Daniel WALSER | Bug fix. |
| Jun 16 2026 | Daniel WALSER | is_admin attribut hinzugefügt. Prüfung dass nur ein Admin existieren darf. |
| Jun 16 2026 | Daniel WALSER | is_admin attribut wurde dem userResponse auch hinzugefügt. |
| Jun 16 2026 | Daniel WALSER | ADmin wurde somit auch erstellt. |
| Jun 15 2026 | Daniel WALSER | Requirements angepasst |
| Jun 15 2026 | Daniel WALSER | API-KEY wurde noch fertig implementiert. |
| Jun 11 2026 | Daniel WALSER | Update: Man kann eigentlich auch nur den Usernamen ohne Passwort abändern, anstatt nur das Passwort (Schreibfehler vom vorherigen Commit) |
| Jun 11 2026 | Daniel WALSER | Jetzt kann für User auch nur das Passwort öndern |
| Jun 8 2026 | Daniel WALSER | Update: Da es Probleme gab, gibt es eine Datei die das SSL erzeugt. |
| Jun 8 2026 | Daniel WALSER | SSL-Zertifikat wird jetzt erstellt, wenn man keines zum starten hat. |
| Jun 8 2026 | Daniel WALSER | Neue Route um die User nur nach dem Namen finden kann. |
| Jun 7 2026 | Daniel WALSER | Anpassung von ChangeUser und DeleteUser an das C# Programm. Jetzt sucht das Programm nach den Usernamen anstelle nach der ID des Users. |
| Jun 5 2026 | Daniel WALSER | Ohne Zertifikat kann man den Server auch starten. |
| Jun 5 2026 | Daniel WALSER | Hier ist noch das ERM u. RM |
| Jun 5 2026 | Daniel WALSER | Hier wurde HTTPS eingebunden (besonders wichtig für das Login). |
| Jun 3 2026 | Daniel WALSER | ERM-RM angepasst |
| Jun 1 2026 | Daniel WALSER | Requirements sind auf aktuellen Stand |
| Mai 29 2026 | Daniel WALSER | 3. Teil Login |
| Mai 28 2026 | Daniel WALSER | Versuch 2.teil: Login ermöglchen. |
| Mai 27 2026 | Daniel WALSER | Versuch: Das Login ermöglichen. |
| Mai 27 2026 | Daniel WALSER | Hier wurden mal die Hashing Methoden erstellt. |
| Mai 25 2026 | Daniel WALSER | User: Eine Alias wurde eingefügt, damit der Server einen neuen User erstellen kann. |
| Mai 24 2026 | Daniel WALSER | Merge remote-tracking branch 'origin/main' |
| Mai 24 2026 | Daniel WALSER | PUT: Username abändern sodass zwei den gleichen haben ist nicht möglich. |
| Mai 24 2026 | Daniel WALSER | POST: User mit gleichen Namen sind nicht mehr möglich. |
| Mai 24 2026 | Daniel WALSER | Merge remote-tracking branch 'origin/main' |
| Mai 24 2026 | Daniel WALSER | Post: gleiche Usernamen sind nicht mehr erlaubt. |
| Mai 24 2026 | Daniel WALSER | Put Methode hinzugefügt und das Delete wurde gefixt. |
| Mai 24 2026 | Daniel WALSER | Put Methode hinzugefügt und das Delete wurde gefixt. |
| Mai 23 2026 | Daniel WALSER | Maximale Länge von Strings angepasst. Routen angepasst. |
| Mai 21 2026 | Daniel WALSER | Hier ist die FastAPI für unser Projekt. Der User wurde somit auch erstellt. |



# User-Endpunkte

> **Basis-URL:** `http://<server>/user`  
> **Authentifizierung:** Alle Endpunkte erfordern einen gültigen API-Key im Header.

---

## Wichtige Regeln vorab

Der `UserName` darf keine Leerzeichen enthalten und muss 1–31 Zeichen lang sein. Passwörter können entweder als Klartext oder bereits als bcrypt-Hash (`$2a$`, `$2b$`, `$2y$`, exakt 60 Zeichen) geschickt werden – das Backend erkennt das selbst und hasht Klartextpasswörter automatisch. Alle Requests und Responses sind JSON.

---

## Endpunkte

### 1. `GET /user/{username}` – Benutzer abrufen

Gibt die Daten eines bestimmten Benutzers zurück.

**URL-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung            |
|------------|--------|---------|-------------------------|
| `username` | string | ✅      | Der Name des Benutzers  |

**Beispiel-Anfrage:**
```
GET /user/MaxMustermann
```

**Beispiel-Antwort (200 OK):**
```json
{
  "UserName": "MaxMustermann",
  "passwd": "$2b$12$...",
  "UserId": 1,
  "is_admin": false
}
```

**Fehlercodes:**

| Code | Bedeutung                       |
|------|---------------------------------|
| 404  | Benutzer wurde nicht gefunden   |

---

### 2. `POST /user/login` – Einloggen

Prüft Benutzername und Passwort. Bei Erfolg werden die Benutzerdaten zurückgegeben.

**Request-Body:**
```json
{
  "UserName": "MaxMustermann",
  "passwd": "meinPasswort123"
}
```

| Feld       | Typ    | Pflicht | Beschreibung                        |
|------------|--------|---------|-------------------------------------|
| `UserName` | string | ✅      | Der Benutzername                    |
| `passwd`   | string | ✅      | Das Passwort (Klartext oder Hash)   |

**Hinweis:** Wird das Passwort im Klartext übergeben und ist in der Datenbank noch kein Hash gespeichert, wird das Passwort beim erfolgreichen Login automatisch gehasht und gespeichert.

**Beispiel-Antwort (200 OK):**
```json
{
  "UserName": "MaxMustermann",
  "passwd": "$2b$12$...",
  "UserId": 1,
  "is_admin": false
}
```

**Fehlercodes:**

| Code | Bedeutung                          |
|------|------------------------------------|
| 404  | Benutzer nicht gefunden            |
| 401  | Passwort falsch / Login ungültig   |

---

### 3. `POST /user/` – Neuen Benutzer erstellen

Legt einen neuen Benutzer an.

**Request-Body:**
```json
{
  "UserName": "NeuerUser",
  "passwd": "sicheresPasswort"
}
```

| Feld       | Typ    | Pflicht | Regeln                                         |
|------------|--------|---------|------------------------------------------------|
| `UserName` | string | ✅      | 1–31 Zeichen, keine Leerzeichen                |
| `passwd`   | string | ✅      | Klartext oder bcrypt-Hash (60 Zeichen)         |

**Beispiel-Antwort (200 OK):**
```json
{
  "UserName": "NeuerUser",
  "passwd": "$2b$12$...",
  "UserId": 5,
  "is_admin": false
}
```

**Fehlercodes:**

| Code | Bedeutung                                         |
|------|---------------------------------------------------|
| 409  | Ein Benutzer mit diesem Namen existiert bereits   |

---

### 4. `PUT /user/` – Benutzer bearbeiten

Aktualisiert den Benutzernamen und/oder das Passwort eines bestehenden Benutzers.

**Query-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung                              |
|------------|--------|---------|-------------------------------------------|
| `username` | string | ✅      | Der aktuelle Name des zu ändernden Users  |

**Request-Body:**
```json
{
  "UserName": "NeuerName",
  "passwd": "neuesPasswort"
}
```

**Hinweis:** Beide Felder müssen angegeben werden. Es wird nur geändert, was einen neuen Wert hat.

**Beispiel-Anfrage:**
```
PUT /user/?username=AlterName
```

**Beispiel-Antwort (200 OK):**
```json
{
  "UserName": "NeuerName",
  "passwd": "neuesPasswort",
  "UserId": 5,
  "is_admin": false
}
```

**Fehlercodes:**

| Code | Bedeutung                                            |
|------|------------------------------------------------------|
| 404  | Benutzer mit dem alten Namen nicht gefunden          |
| 409  | Der neue Benutzername ist bereits vergeben           |

---

### 5. `DELETE /user/` – Benutzer löschen

Löscht einen Benutzer anhand seines Namens.

**Query-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung                   |
|------------|--------|---------|--------------------------------|
| `username` | string | ✅      | Name des zu löschenden Users   |

**Beispiel-Anfrage:**
```
DELETE /user/?username=MaxMustermann
```

**Antwort:** `204 No Content` (kein Body)

**Fehlercodes:**

| Code | Bedeutung                      |
|------|--------------------------------|
| 404  | Benutzer wurde nicht gefunden  |

---

## Übersicht aller Endpunkte

| Methode  | Pfad              | Beschreibung               |
|----------|-------------------|----------------------------|
| GET      | `/user/{username}`| Benutzer abrufen           |
| POST     | `/user/login`     | Einloggen                  |
| POST     | `/user/`          | Neuen Benutzer erstellen   |
| PUT      | `/user/`          | Benutzer bearbeiten        |
| DELETE   | `/user/`          | Benutzer löschen           |



---

# Admin-API Dokumentation

**Basis-URL:** `http://<server>/admin`
**Authentifizierung:** Jeder Request braucht einen gültigen API-Key im Header.

---

## Wichtige Regeln vorab

Der `AdminName` (im JSON als `UserName` übergeben) darf keine Leerzeichen enthalten und muss 1–31 Zeichen lang sein. Passwörter können als Klartext oder als bcrypt-Hash (`$2a$`, `$2b$`, `$2y$`, exakt 60 Zeichen) geschickt werden – das Backend hasht Klartext automatisch. Alle Requests und Responses sind JSON.

Es kann **nur einen Administrator** im System geben. Ein zweiter Admin-Account lässt sich nicht anlegen, solange bereits einer existiert.

---

## GET /admin/

Gibt eine Liste aller Benutzer im System zurück.

Kein Request-Body, keine Parameter nötig.

**Response 200:**
```json
[
  {
    "UserName": "adminUser",
    "passwd": "$2b$12$...",
    "UserId": 1,
    "is_admin": true
  },
  {
    "UserName": "hansmüller",
    "passwd": "$2b$12$...",
    "UserId": 2,
    "is_admin": false
  }
]
```

---

## GET /admin/{username}

Liefert die Daten zu einem bestimmten Benutzer.

**URL-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung                 |
|------------|--------|---------|------------------------------|
| `username` | string | ja      | Name des gesuchten Benutzers |

**Beispiel:**
**Response 200:**
```json
{
  "UserName": "hansmüller",
  "passwd": "$2b$12$...",
  "UserId": 2,
  "is_admin": false
}
```

**Fehler:**

| Code | Grund                                   |
|------|-----------------------------------------|
| 404  | Kein Benutzer mit diesem Namen gefunden |

---

## POST /admin/login

Prüft Login-Daten des Admins. Das Passwort muss als bcrypt-Hash in der Datenbank stehen – Klartext-Vergleich wie beim User-Login findet hier nicht statt.

**Request-Body:**
```json
{
  "AdminName": "adminUser",
  "passwd": "adminPasswort"
}
```

| Feld        | Typ    | Pflicht | Hinweis                        |
|-------------|--------|---------|--------------------------------|
| `AdminName` | string | ja      | Name des Admin-Accounts        |
| `passwd`    | string | ja      | Klartext (wird gegen Hash geprüft) |

**Response 200:**
```json
{
  "UserName": "adminUser",
  "passwd": "$2b$12$...",
  "UserId": 1,
  "is_admin": true
}
```

**Fehler:**

| Code | Grund                   |
|------|-------------------------|
| 404  | Benutzer nicht gefunden |
| 401  | Passwort falsch         |

---

## POST /admin/

Legt den Administrator-Account an. Das geht nur einmal – sobald ein Admin existiert, wird jeder weitere Versuch abgelehnt.

**Request-Body:**
```json
{
  "UserName": "adminUser",
  "passwd": "sicheresPasswort"
}
```

| Feld       | Typ    | Pflicht | Regeln                                 |
|------------|--------|---------|----------------------------------------|
| `UserName` | string | ja      | 1–31 Zeichen, keine Leerzeichen        |
| `passwd`   | string | ja      | Klartext oder bcrypt-Hash (60 Zeichen) |

Der neu angelegte Account bekommt automatisch `is_admin: true`.

**Response 200:**
```json
{
  "UserName": "adminUser",
  "passwd": "$2b$12$...",
  "UserId": 1,
  "is_admin": true
}
```

**Fehler:**

| Code | Grund                                              |
|------|----------------------------------------------------|
| 409  | Ein Benutzer mit diesem Namen existiert schon      |
| 400  | Es existiert bereits ein Administrator im System   |

---

## PUT /admin/

Ändert den Namen und/oder das Passwort eines Benutzers. Der zu ändernde Benutzer wird per Query-Parameter übergeben, die neuen Daten im Body.

**Query-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung                 |
|------------|--------|---------|------------------------------|
| `username` | string | ja      | Aktueller Name des Benutzers |

**Request-Body:**
```json
{
  "UserName": "neuerAdminName",
  "passwd": "neuesPasswort"
}
```

Beide Felder müssen mitgeschickt werden. Soll nur das Passwort geändert werden, einfach den alten Namen nochmal im Body angeben.

**Beispiel:**
**Response 200:**
```json
{
  "UserName": "neuerAdminName",
  "passwd": "neuesPasswort",
  "UserId": 1,
  "is_admin": true
}
```

**Fehler:**

| Code | Grund                            |
|------|----------------------------------|
| 404  | Benutzer nicht gefunden          |
| 409  | Der neue Name ist schon vergeben |

---

## DELETE /admin/

Löscht einen Benutzer.

**Query-Parameter:**

| Parameter  | Typ    | Pflicht | Beschreibung                     |
|------------|--------|---------|----------------------------------|
| `username` | string | ja      | Name des zu löschenden Benutzers |

**Beispiel:**
**Response:** `204 No Content` (kein Body)

**Fehler:**

| Code | Grund                   |
|------|-------------------------|
| 404  | Benutzer nicht gefunden |

---

## Kurzübersicht

| Methode | Pfad                | Was passiert            |
|---------|---------------------|-------------------------|
| GET     | `/admin/`           | Alle Benutzer abrufen   |
| GET     | `/admin/{username}` | Einzelnen User abrufen  |
| POST    | `/admin/login`      | Admin-Login             |
| POST    | `/admin/`           | Admin-Account erstellen |
| PUT     | `/admin/`           | Benutzer bearbeiten     |
| DELETE  | `/admin/`           | Benutzer löschen        |