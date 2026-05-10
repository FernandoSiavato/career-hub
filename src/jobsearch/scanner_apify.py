"""Apify Actors wrapper.

Lazy import de apify-client: solo se usa si hay Actors habilitados Y
APIFY_TOKEN en el entorno. Si la libreria no esta instalada, el scanner
captura ImportError y reporta el actor como skipped.
"""

from __future__ import annotations

from typing import Any

from jobsearch.config import APIFY_TOKEN
from jobsearch.scanner import Job

# Default field maps for popular Actors. Cada entry mapea
# {target -> source_field_in_dataset_item}.
DEFAULT_FIELD_MAPS: dict[str, dict[str, str]] = {
    "apify/linkedin-jobs-scraper": {
        "title": "title",
        "url": "link",
        "company": "companyName",
        "location": "location",
        "description": "description",
        "remote_type": "workType",
        "salary": "salary",
    },
    "bebity/linkedin-jobs-scraper": {
        "title": "title",
        "url": "link",
        "company": "companyName",
        "location": "location",
        "description": "description",
        "remote_type": "workType",
        "salary": "salary",
    },
    "valig/linkedin-jobs-scraper": {
        "title": "title",
        "url": "url",
        "company": "companyName",
        "location": "location",
        "description": "description",
        "remote_type": "workType",
        "salary": "salary",
    },
    "curious_coder/linkedin-jobs-scraper": {
        "title": "title",
        "url": "link",
        "company": "companyName",
        "location": "location",
        "description": "description",
        "remote_type": "workType",
        "salary": "salary",
    },
    "apify/indeed-scraper": {
        "title": "positionName",
        "url": "url",
        "company": "company",
        "location": "location",
        "description": "descriptionPlain",
        "remote_type": "jobType",
        "salary": "salary",
    },
    "misceres/indeed-scraper": {
        "title": "positionName",
        "url": "url",
        "company": "company",
        "location": "location",
        "description": "descriptionPlain",
        "remote_type": "jobType",
        "salary": "salary",
    },
    "apify/web-scraper": {
        "title": "title",
        "url": "url",
        "company": "company",
        "location": "location",
    },
    "apify/cheerio-scraper": {
        "title": "title",
        "url": "url",
        "company": "company",
        "location": "location",
    },
}


def is_enabled() -> bool:
    return bool(APIFY_TOKEN)


def run_actor(actor_id: str, run_input: dict, timeout_s: int = 300) -> list[dict]:
    """Llama actor.call() y devuelve dataset items. Bloquea hasta done o timeout.

    Lanza ImportError si apify-client no esta instalado, RuntimeError si el run
    no termina con SUCCEEDED. Excepciones son capturadas por el orquestador.
    """
    if not APIFY_TOKEN:
        raise RuntimeError("APIFY_TOKEN no esta en el entorno")

    try:
        from apify_client import ApifyClient
    except ImportError as e:
        raise ImportError(
            "Instala 'apify-client' para usar Apify Actors: pip install apify-client"
        ) from e

    client = ApifyClient(APIFY_TOKEN)
    actor = client.actor(actor_id)
    run = actor.call(run_input=run_input, timeout_secs=timeout_s)
    if not run:
        raise RuntimeError(f"Actor {actor_id}: run vacio")
    if run.get("status") != "SUCCEEDED":
        raise RuntimeError(f"Actor {actor_id}: status={run.get('status')}")

    dataset_id = run.get("defaultDatasetId")
    if not dataset_id:
        return []

    items = list(client.dataset(dataset_id).iterate_items())
    return items


def normalize_apify_items(
    items: list[dict], actor_id: str, field_map: dict | None = None, default_company: str = ""
) -> list[Job]:
    """Convierte items de un dataset Apify a Job normalizado."""
    fmap = field_map or DEFAULT_FIELD_MAPS.get(actor_id) or DEFAULT_FIELD_MAPS["apify/web-scraper"]
    actor_slug = actor_id.split("/")[-1] if "/" in actor_id else actor_id
    out: list[Job] = []
    for it in items or []:
        title = _extract(it, fmap.get("title", "title"))
        url = _extract(it, fmap.get("url", "url"))
        company = _extract(it, fmap.get("company", "company")) or default_company
        location = _extract(it, fmap.get("location", "location"))
        description = _extract(it, fmap.get("description", "")) if fmap.get("description") else ""
        remote_type = _extract(it, fmap.get("remote_type", "")) if fmap.get("remote_type") else ""
        salary_text = _extract(it, fmap.get("salary", "")) if fmap.get("salary") else ""
        if not (url and title):
            continue
        out.append(
            Job(
                url=url.strip(),
                title=title.strip(),
                company=(company or default_company or "Unknown").strip(),
                location=(location or "").strip(),
                source=f"apify:{actor_slug}",
                description=(description or "")[:20000],
                remote_type=(remote_type or "").strip(),
                salary_text=(salary_text or "").strip(),
            )
        )
    return out


def _extract(item: dict, key: str) -> str:
    """Soporta keys planas o dotted paths simples (a.b.c)."""
    if not key:
        return ""
    cur: Any = item
    for part in key.split("."):
        if isinstance(cur, dict):
            cur = cur.get(part)
        else:
            return ""
        if cur is None:
            return ""
    if isinstance(cur, (str, int, float)):
        return str(cur)
    return ""
