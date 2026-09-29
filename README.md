# MISS2104O1 — Big Data Analytics

Course repository for **Big Data Analytics** at the Faculty of Computer Science, Alexandru Ioan Cuza University of Iași.

## Source

Protected course page:

- https://edu.info.uaic.ro/big-data-analytics/

The course page currently requires HTTP authentication. Credentials are intentionally **not** stored in this repository.

See [the course index](COURSE_INDEX.md) for the active lecture and lab links, assessment weights, and external resources. For a smaller personal download of the PDFs, run `python3 download_materials.py` and enter the course credentials at the prompts. The `materials/` directory is ignored by Git.\n\n## Mirror the course materials

The repository includes `scripts/scrape_course.py`, which recursively mirrors pages and downloadable assets under the course path while staying on the same host.

### Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

Set the credentials only in your shell environment:

```bash
export BDA_USERNAME="..."
export BDA_PASSWORD="..."
```

Windows PowerShell:

```powershell
$env:BDA_USERNAME="..."
$env:BDA_PASSWORD="..."
```

Then run:

```bash
python scripts/scrape_course.py
```

The mirror is written to `course-materials/`. The scraper records the final source URL for every downloaded item in `course-materials/manifest.json`.

## Course metadata

Public UAIC course-programme pages identify the discipline as **Big Data Analytics / Analiza bazelor mari de date** and list Prof. PhD. Mihaela Elena Breabăn as course teacher. The protected course page is the authoritative source for current teaching materials.

## Repository policy

- Do not commit passwords, cookies, authorization headers, or browser session files.
- Preserve the original filenames whenever possible.
- Keep downloaded material organized by its source URL path.
- If the source site changes, regenerate `course-materials/` rather than manually renaming mirrored files.
