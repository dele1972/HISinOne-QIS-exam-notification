# HISinOne QIS -> Benachrichtigungen über bewertete Prüfungsleistungen

Dies ist ein Fork von [MrKrisKrisu/HISinOne-QIS-exam-notification](https://github.com/MrKrisKrisu/HISinOne-QIS-exam-notification). Der Aufbau ist etwas modularer programmmiert und zusätzlich wurden die Benachrichtigungskanäle E-Mail und Discord Message (Webhook) hinzugefügt - alles in der „mal eben hinzufügen”-Manier.

## Was ist das?

Ein Python Script, das sich für dich in iCMS einloggt und schaut, ob sich Änderungen (zum Beispiel eine neue
eingetragene Note) in der Prüfungsübersicht bei dir ergeben haben. Das Script benachrichtigt dich dann direkt per
Telegram. Es ist also dafür gedacht, beispielsweise alle 10 Minuten ausgeführt zu werden.

> Tut dem Hochschulserver einen Gefallen und fragt **nicht** alle 10 Sekunden ab!

## Kompatible Hochschulen

Die QIS-Software aus dem Paket HISinOne wird bei vielen Hochschulen in Deutschland eingesetzt. Sofern keine
individuellen Programmierungen vorhanden sind, sollte dieses Script bei diesen dann auch funktionieren.

Bislang sind folgende kompatible Hochschulen bekannt:

- Hochschule Hannover
- TU Braunschweig
- Leibniz Universität Hannover
- Hochschule Bremerhaven
- Westfälische Hochschule Gelsenkirchen
- Hochschule Koblenz
- FernUniversität in Hagen
- Hochschule Karlsruhe Technik und Wirtschaft

Alternative Skripts für weitere Hochschulen:

- [Hochschule Fulda (horstl)](https://github.com/binsky08/HISinOne-QIS-exam-notification)

## Installationsanleitung

Die Konfiguration erfolgt über die Datei `userdata.json`. Dort werden die notwendigen icms Login-Daten hinterlegt und alle Ausgabekanäle konfiguriert. **Hinweis**: Aktuell ist Telegramm statisch deaktiviert. In einer späteren Version könnte man die präferierte Benachrichtigungsmethode auch dynamisch (z. B. über die `userdata.json` regeln.

### Telegram einrichten

#### Telegram Bot erstellen

Erstelle über den [BotFather](https://t.me/botfather) einen neuen Bot und schreibe dir den Token heraus. Mehr
Informationen zum erstellen von Telegram Bots: [https://core.telegram.org/bots](https://core.telegram.org/bots)

#### Telegram Chat ID herausfinden

* Erstelle eine neue Gruppe und füge deinen Bot hinzu, sowie den [TelegramRawBot](https://t.me/RawDataBot)
* Schreibe nun eine Nachricht in die Gruppe, der RawBot wird dir antworten
* Schreibe dir deine ID heraus, die unter **message -> from -> id** steht

### Discord Webhook

1. Óffne Discord per Browser
2. Óffne mit einem Rechtsklick auf deinen Server: Servereinstellungen/Integrationen
3. Erstelle einen WebHook

Im Anschluss kannst du dort auch die Webhook-URL kopieren, welche du in der `userdata.json` beim Schlüssel `whUrl` angeben musst.

**Veraltetet**: In der `userdata.json` werden zusätzlich die Schlüssel `token`, `clientID`, `cIdAllgemein` und `cIdMeintest` belegt. Dabei handelt es sich um einen Testlauf, direkt mit der Discord-API zu kommunizieren. Aktuell wird jedoch der Discord WebHook verwendet.

### Python Umgebung

Die Module [`requests`](https://pypi.org/project/requests/), [`lxml`](https://pypi.org/project/lxml/) und [`Unidecode`](https://pypi.org/project/Unidecode/) sind standardmäßig nicht installiert. Diese können mit pip nachinstalliert werden:

- per requirements

```bash
pip install -r requirements.txt
```

- oder manuell

```bash
pip install requests
pip install lxml
pip install Unidecode
```

### Script installieren

Lade das Script in deine Python Umgebung und passe in den oberen Zeilen die Werte für den Telegram Token und die
Telegram ChatID an. Außerdem musst du deine iCMS Zugangsdaten eingeben. Wenn du das Script jetzt ausführst solltest du
einmalig über **alle** eingetragenen Prüfungen benachrichtigt werden.

### Automatisches ausführen

Du kannst dein Script automatisch regelmäßig ausführen lassen (dafür ist es ja auch gedacht). Das kannst du mit einem
CronJob realisieren. Erstelle einfach folgenden CronJob:

> */15 * * * * /path/to/script.py

Dies führt dein Script automatisch alle 15 Minuten aus. Den Wert kannst du anpassen, aber denk dabei bitte an die armen,
armen Hochschulserver! Um das ganze noch mehr einzuschränken kann man die Ausführung auf die Prüfungsrelevanten Monate
begrenzen:
> */15 * * 1,2,6,7 * /path/to/script.py

## Sicherheitshinweis

Du musst dein zentrales Passwort für deinen Hochschulaccount in **Klartext** in dieses Script speichern. Achte daher
bitte darauf, dass es nur in einer gesicherten Umgebung läuft und durch geeignete Berechtigungen von dem Zugriff Dritter
geschützt ist.
