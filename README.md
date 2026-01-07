# Audioteca (Podcast)

Sitio estático para GitHub Pages (Jekyll) que:
- Publica episodios como entradas Markdown
- Sirve MP3 desde `assets/mp3/`
- Genera un feed RSS (podcast) en `feed.xml`

## Uso rápido

1) Sube tus MP3 a `assets/mp3/` (estructura por año). Ej.: `assets/mp3/2026/2026-01-07-mi-episodio.mp3`.

2) Crea un episodio en `_posts/` (nombre: `YYYY-MM-DD-mi-episodio.md`).

	Campos importantes en el front matter:
	- `audio_url`: ruta al MP3 (ej: `/assets/mp3/episodio-001.mp3`)
	- `audio_length`: tamaño en bytes (recomendado en el enclosure)
	- `duration`: `H:MM:SS`

	Para obtener el tamaño en bytes en Linux:

	```bash
	stat -c%s assets/mp3/episodio-001.mp3
	```

	O usa el script auxiliar para generar el snippet listo para pegar (recomendado):

	```bash
	python3 tools/generate_episode_meta.py assets/mp3/2026/2026-01-07-mi-episodio.mp3
	```

	Salida de ejemplo:

	```yaml
	audio_url: "/assets/mp3/2026/2026-01-07-mi-episodio.mp3"
	audio_type: "audio/mpeg"
	audio_length: 12345678
	duration: "0:42:31"
	```

	Notas:
	- El script calcula `audio_length` siempre y `duration` si encuentra `ffprobe` (ffmpeg) o la librería `mutagen`.
	- Si no tienes `ffprobe`, instálalo (Debian/Ubuntu: `sudo apt-get install ffmpeg`). Alternativa: `pip install mutagen` en tu entorno Python.

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

- Feed original del sitio (origen para FeedBurner): `/feed.xml`
- Feed público enlazado en la web: `https://feeds.feedburner.com/daizansoriano/podcast`

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
