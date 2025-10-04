# Technische Einsatzleitung
Digitale Unterstützung in der Technische Einsatzleitung (TEL).

## Einrichtung

Diese digitale Unterstüzung kann auf jedem Rechner ausgeführt werden. Dazu dieses Repository clonen in dem folgender Befehl im Terminal ausgeführt wird:
```bash
    git clone https://github.com/sw-lnk/TEL.git
```
Im Anschluss die Datei ```.env.example``` in ```.env``` umbenennen und mit eigenen Werten ausfüllen.

Administrator anlegen:
```bash
    python3 setup.py
```

Anwendung starten:
```bash
    python3 app.py
```

Weitere Infos zum Deployment siehe [NiceGUI](https://nicegui.io/documentation/section_configuration_deployment).


## ToDo's
- [X] User Interface
- [X] Nutzer-Management
- [ ] Einsatztagebuch
    - [ ] Gesamteinsatz
    - [ ] Einsatzabschnitte
- [ ] Vierfachnachrichtenvordruck
- [ ] Kräfteübersicht
- [ ] Einsatzübersicht

## Referenz
* [NiceGUI](https://nicegui.io/)
* [FastAPI](https://fastapi.tiangolo.com/)
* [Pydantic](https://pydantic.dev/)
* [SQLmodel](https://sqlmodel.tiangolo.com/)
