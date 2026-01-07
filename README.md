# Audioteca (Podcast)

Sitio estático para GitHub Pages (Jekyll) que:
- Publica episodios como entradas Markdown
- Sirve MP3 desde `assets/mp3/`
- Genera un feed RSS (podcast) en `feed.xml`

## Uso rápido

1) Sube tus MP3 a `assets/mp3/`

2) Crea un episodio en `_posts/` (nombre: `YYYY-MM-DD-mi-episodio.md`).

	Campos importantes en el front matter:
	- `audio_url`: ruta al MP3 (ej: `/assets/mp3/episodio-001.mp3`)
	- `audio_length`: tamaño en bytes (recomendado en el enclosure)
	- `duration`: `HH:MM:SS`

	Para obtener el tamaño en bytes en Linux:

	```bash
	stat -c%s assets/mp3/episodio-001.mp3
	```

3) Configura `url` y `baseurl` en `_config.yml`.

## Ejecutar localmente

Requiere Ruby + Bundler.

En Linux, para que `bundle install` pueda compilar dependencias nativas, suele hacer falta instalar headers:
- Debian/Ubuntu: `sudo apt-get install ruby-dev build-essential`
- Fedora: `sudo dnf install ruby-devel gcc make`

Si instalas Bundler en modo usuario, añade a tu PATH:

```bash
export PATH="$PATH:$HOME/.local/share/gem/ruby/3.3.0/bin"
```

```bash
bundle install
bundle exec jekyll serve
```

Luego abre `http://localhost:4000`.

## Feed

- Feed del podcast: `/feed.xml`

## Importar episodios desde un feed existente

Hay un importador para traer episodios desde un RSS (como el de daizansoriano.com) y convertirlos a `_posts/*.md`.

Solo crear los Markdown (sin descargar MP3):

```bash
/home/sasogu/web/Audioteca/.venv/bin/python tools/import_podcast_feed.py --dry-run
```

Crear Markdown y descargar los MP3 a `assets/mp3/` (ejemplo con 5 episodios):

```bash
/home/sasogu/web/Audioteca/.venv/bin/python tools/import_podcast_feed.py --download --limit 5
```
