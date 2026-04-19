# WarpDesk

Interfície d'escriptori per a Cloudflare WARP a Linux.

WarpDesk neix per diversió i per a la comunitat. La idea és simple: no hi havia una experiència d'escriptori realment nativa i amable a Linux per a qui només vol gestionar WARP amb dos clics, sense obrir un terminal per a una tasca quotidiana.

Made with 🖤 in Barcelona City 🇪🇸

![Captura de WarpDesk](docs/media/warpdesk-main.png)

## Per què existeix

El flux oficial de WARP a Linux funciona, però continua sent massa orientat a consola si el que busques és:

- una finestra d'escriptori adequada
- una entrada a la safata amb accions ràpides
- un resum compacte de l'estat de connexió
- canviar mode i protocol amb facilitat
- desar perfils
- no memoritzar comandes per a l'ús diari

WarpDesk manté `warp-cli` com a backend i se centra a oferir una millor experiència d'escriptori.

## Funcionalitats

- Connectar i desconnectar des d'una finestra Qt nativa
- Canviar entre MASQUE i WireGuard
- Canviar el mode de WARP
- Desar perfils
- Panell de diagnòstic
- Icona a la safata amb accions ràpides
- Integració amb menú d'aplicacions i accés directe a l'escriptori
- Interfície adaptada a l'idioma del sistema en anglès, castellà i català
- Ús de la paleta del sistema per integrar-se millor en escriptoris Linux

## Captura

La captura superior es genera des de la mateixa aplicació en mode offscreen i es pot regenerar amb:

```bash
QT_QPA_PLATFORM=offscreen PYTHONPATH=src python3 scripts/generate_screenshot.py
```

## Requisits

- Escriptori Linux
- Python 3.11+
- PySide6
- Cloudflare WARP instal·lat

Arch / CachyOS:

```bash
sudo pacman -S cloudflare-warp-bin
```

## Executar des del codi font

```bash
cd warpdesk
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
warpdesk
```

## Instal·lar com a app d'escriptori

Això crea:

- `~/.local/bin/warpdesk`
- `~/.local/share/applications/io.warpdesk.app.desktop`
- `~/Escritorio/WarpDesk.desktop`
- `~/.local/share/icons/hicolor/scalable/apps/warpdesk-shield.svg`

Executa:

```bash
cd warpdesk
./scripts/install_local.sh
```

## Notes públiques

- WarpDesk depèn de `warp-cli` i `warp-svc`
- desinstal·lar `cloudflare-warp-bin` elimina el backend que usa WarpDesk
- les accions privilegiades sobre el servei depenen de `pkexec`

## Documentació

- [Arquitectura](docs/ARCHITECTURE.md)
- [Marca i icones](docs/BRANDING.md)

## Full de ruta

El full de ruta viu com a issues a GitHub perquè el progrés sigui visible i accionable.

## Contribucions

Si vols aportar una traducció per a un altre idioma, obre un pull request i estaré encantat de revisar-lo i integrar-lo si encaixa bé amb el projecte. El mateix aplica a noves funcionalitats, millores d'UX, empaquetat o qualsevol altra contribució útil.
