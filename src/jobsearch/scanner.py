"""Portal scanner: descubre ofertas nuevas desde Greenhouse/Ashby/Lever + Apify.

Lee portals.yml, llama APIs publicas, filtra por titulo segun perfil,
deduplica contra scanned_jobs, y devuelve un ScanReport.
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from jobsearch.database import get_seen_urls, insert_scanned_jobs

TIMEOUT_S = 10
USER_AGENT = "jobsearch-scanner/1.0 (+https://github.com/local)"


# ---------------------------------------------------------------------------
# Data shapes
# ---------------------------------------------------------------------------


@dataclass
class Job:
    url: str
    title: str
    company: str
    location: str = ""
    source: str = ""
    profile_tag: str = ""
    description: str = ""
    remote_type: str = ""
    salary_text: str = ""

    def as_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "source": self.source,
            "profile_tag": self.profile_tag,
            "description": self.description,
            "remote_type": self.remote_type,
            "salary_text": self.salary_text,
        }


@dataclass
class CompanyResult:
    name: str
    source: str
    fetched: int = 0
    filtered: int = 0
    error: str | None = None


@dataclass
class ScanReport:
    companies: list[CompanyResult] = field(default_factory=list)
    actors: list[CompanyResult] = field(default_factory=list)
    found_total: int = 0
    after_title_filter: int = 0
    after_dedup: int = 0
    inserted: int = 0
    samples: list[Job] = field(default_factory=list)
    dry_run: bool = False


# ---------------------------------------------------------------------------
# API detection
# ---------------------------------------------------------------------------

ASHBY_RE = re.compile(r"jobs\.ashbyhq\.com/([^/?#]+)")
LEVER_RE = re.compile(r"jobs\.lever\.co/([^/?#]+)")
GH_BOARDS_RE = re.compile(r"job-boards(?:\.eu)?\.greenhouse\.io/([^/?#]+)")
GH_LEGACY_RE = re.compile(r"boards\.greenhouse\.io/([^/?#]+)")
WORKDAY_RE = re.compile(
    r"https?://([^.]+)\.([^.]+)\.myworkdayjobs\.com/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#]+)"
)


def detect_api(company: dict) -> dict | None:
    """Returns {'type': 'greenhouse'|'ashby'|'lever', 'url': str} or None."""
    api = company.get("api") or ""
    if "greenhouse" in api:
        # Add content=true to get description if not already there
        if "content=true" not in api:
            sep = "&" if "?" in api else "?"
            api = f"{api}{sep}content=true"
        return {"type": "greenhouse", "url": api}
    if "ashbyhq" in api:
        return {"type": "ashby", "url": api}
    if "lever" in api:
        return {"type": "lever", "url": api}

    careers = company.get("careers_url") or ""

    m = ASHBY_RE.search(careers)
    if m:
        return {
            "type": "ashby",
            "url": f"https://api.ashbyhq.com/posting-api/job-board/{m.group(1)}?includeCompensation=true",
        }

    m = LEVER_RE.search(careers)
    if m:
        return {"type": "lever", "url": f"https://api.lever.co/v0/postings/{m.group(1)}?mode=json"}

    m = GH_BOARDS_RE.search(careers) or GH_LEGACY_RE.search(careers)
    if m:
        return {
            "type": "greenhouse",
            "url": f"https://boards-api.greenhouse.io/v1/boards/{m.group(1)}/jobs?content=true",
        }

    m = WORKDAY_RE.search(careers)
    if m:
        tenant, shard, site = m.group(1), m.group(2), m.group(3)
        return {
            "type": "workday",
            "host": f"{tenant}.{shard}.myworkdayjobs.com",
            "tenant": tenant,
            "site": site,
            "base_url": f"https://{tenant}.{shard}.myworkdayjobs.com/{site}",
            "api_url": f"https://{tenant}.{shard}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs",
        }

    return None


# ---------------------------------------------------------------------------
# Parsers
# ---------------------------------------------------------------------------


def _strip_html(html: str) -> str:
    """Quick & dirty HTML stripper for descriptions."""
    if not html:
        return ""
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_greenhouse(payload: dict, company_name: str) -> list[Job]:
    out: list[Job] = []
    for j in payload.get("jobs", []) or []:
        loc = ""
        if isinstance(j.get("location"), dict):
            loc = j["location"].get("name") or ""
        # GH metadata is a list of {name, value, value_type}; salary if present
        salary = ""
        for m in j.get("metadata") or []:
            if "salary" in (m.get("name") or "").lower():
                salary = str(m.get("value") or "")
                break
        out.append(
            Job(
                url=j.get("absolute_url") or "",
                title=j.get("title") or "",
                company=company_name,
                location=loc,
                source="greenhouse",
                description=_strip_html(j.get("content") or "")[:20000],
                salary_text=salary,
                # Greenhouse no devuelve remote_type estandar; inferir de location
                remote_type=("Remote" if "remote" in loc.lower() else ""),
            )
        )
    return [j for j in out if j.url and j.title]


def parse_ashby(payload: dict, company_name: str) -> list[Job]:
    jobs = payload.get("jobs") or []
    out: list[Job] = []
    for j in jobs:
        comp = j.get("compensation") or {}
        salary = (
            comp.get("compensationTierSummary")
            or comp.get("scrapeableCompensationSalarySummary")
            or ""
        )
        out.append(
            Job(
                url=j.get("jobUrl") or j.get("applyUrl") or "",
                title=j.get("title") or "",
                company=company_name,
                location=j.get("locationName") or j.get("location") or "",
                source="ashby",
                description=(j.get("descriptionPlain") or "")[:20000],
                remote_type=j.get("workplaceType") or "",
                salary_text=str(salary) if salary else "",
            )
        )
    return [j for j in out if j.url and j.title]


def parse_lever(payload, company_name: str) -> list[Job]:
    if not isinstance(payload, list):
        return []
    out: list[Job] = []
    for j in payload:
        cats = j.get("categories") or {}
        salary = j.get("salaryRange") or ""
        if isinstance(salary, dict):
            salary = (
                f"{salary.get('min', '?')}-{salary.get('max', '?')} {salary.get('currency', '')}"
            )
        out.append(
            Job(
                url=j.get("hostedUrl") or j.get("applyUrl") or "",
                title=j.get("text") or "",
                company=company_name,
                location=cats.get("location") or "",
                source="lever",
                description=(j.get("descriptionPlain") or _strip_html(j.get("description") or ""))[
                    :20000
                ],
                remote_type=cats.get("commitment") or "",
                salary_text=str(salary) if salary else "",
            )
        )
    return [j for j in out if j.url and j.title]


PARSERS: dict[str, Callable[[object, str], list[Job]]] = {
    "greenhouse": parse_greenhouse,
    "ashby": parse_ashby,
    "lever": parse_lever,
}


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------


def fetch_json(url: str) -> object:
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=TIMEOUT_S) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _post_json(url: str, body: dict, timeout: int = TIMEOUT_S) -> dict:
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_workday_job_detail(host: str, tenant: str, site: str, external_path: str) -> dict:
    """GET job detail JSON. external_path empieza con / y viene de jobPostings."""
    url = f"https://{host}/wday/cxs/{tenant}/{site}{external_path}"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_workday(
    api: dict, company_name: str, max_items: int = 200, page_size: int = 20
) -> list[Job]:
    """Workday usa POST + paginacion via offset. Para humanitarian tipicos
    (~500 ofertas), capamos en max_items para no abusar."""
    out: list[Job] = []
    base_url = api["base_url"]
    api_url = api["api_url"]
    offset = 0
    while offset < max_items:
        body = {
            "appliedFacets": {},
            "limit": min(page_size, max_items - offset),
            "offset": offset,
            "searchText": "",
        }
        try:
            payload = _post_json(api_url, body, timeout=15)
        except Exception:
            break
        postings = payload.get("jobPostings") or []
        if not postings:
            break
        for j in postings:
            ext = j.get("externalPath") or ""
            if not ext:
                continue
            url = base_url + ext if ext.startswith("/") else f"{base_url}/{ext}"
            out.append(
                Job(
                    url=url,
                    title=j.get("title") or "",
                    company=company_name,
                    location=j.get("locationsText") or "",
                    source="workday",
                    remote_type=j.get("remoteType") or "",
                    # description vacia: Workday requiere POST por job-detail; lo dejamos
                    # para fit-scanned bajo demanda
                )
            )
        if len(postings) < body["limit"]:
            break  # last page
        offset += len(postings)
    return [j for j in out if j.url and j.title]


# ---------------------------------------------------------------------------
# Title filter
# ---------------------------------------------------------------------------


def build_title_filter(profile_filters: dict, profile_tags: list[str]) -> Callable[[str], bool]:
    """Combina los filtros de cada perfil que aplica a la empresa.
    Pasa si: AL MENOS un positive de ALGUN perfil presente Y NINGUN negative."""
    positives: list[str] = []
    negatives: list[str] = []
    for tag in profile_tags or []:
        cfg = profile_filters.get(tag) or {}
        positives.extend(s.lower() for s in (cfg.get("positive") or []))
        negatives.extend(s.lower() for s in (cfg.get("negative") or []))

    pos = list({p for p in positives if p})
    neg = list({n for n in negatives if n})

    def matches(title: str) -> bool:
        t = (title or "").lower()
        if not pos:
            has_pos = True
        else:
            has_pos = any(k in t for k in pos)
        has_neg = any(k in t for k in neg)
        return has_pos and not has_neg

    return matches


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------


def _profile_tag_str(tags: list[str]) -> str:
    return ",".join(tags) if tags else ""


def _matches_profile_filter(company_tags: list[str], target: str | None) -> bool:
    if target is None:
        return True
    return target in (company_tags or [])


def scan(
    portals_path: Path | str,
    profile: str | None = None,
    company: str | None = None,
    dry_run: bool = False,
    use_apify: bool = True,
) -> ScanReport:
    """Run scan against ATS APIs and (optionally) Apify Actors."""
    portals_path = Path(portals_path)
    if not portals_path.exists():
        raise FileNotFoundError(f"portals.yml no encontrado: {portals_path}")

    cfg = yaml.safe_load(portals_path.read_text(encoding="utf-8")) or {}
    title_filters = cfg.get("title_filters") or {}
    tracked = cfg.get("tracked_companies") or []
    actors_cfg = cfg.get("apify_actors") or []

    seen = get_seen_urls()
    report = ScanReport(dry_run=dry_run)
    all_jobs: list[Job] = []

    # ----- ATS sources -----
    for c in tracked:
        if not c.get("enabled", True):
            continue
        if company and c.get("name", "").lower() != company.lower():
            continue
        tags = c.get("profile_tags") or []
        if not _matches_profile_filter(tags, profile):
            continue

        api = detect_api(c)
        cr = CompanyResult(name=c.get("name", "?"), source=api["type"] if api else "unknown")
        if not api:
            cr.error = "Sin API detectable (careers_url no apunta a Greenhouse/Ashby/Lever)"
            report.companies.append(cr)
            continue

        try:
            if api["type"] == "workday":
                jobs = fetch_workday(api, c.get("name", "?"), max_items=c.get("max_items", 200))
            else:
                payload = fetch_json(api["url"])
                parser = PARSERS[api["type"]]
                jobs = parser(payload, c.get("name", "?"))
        except urllib.error.HTTPError as e:
            cr.error = f"HTTP {e.code}"
            report.companies.append(cr)
            continue
        except Exception as e:
            cr.error = f"{type(e).__name__}: {e}"
            report.companies.append(cr)
            continue

        cr.fetched = len(jobs)

        title_match = build_title_filter(title_filters, tags)
        filtered = [j for j in jobs if title_match(j.title)]
        cr.filtered = len(filtered)

        for j in filtered:
            j.profile_tag = _profile_tag_str(tags)
        all_jobs.extend(filtered)
        report.companies.append(cr)

    # ----- Apify sources -----
    if use_apify and actors_cfg:
        from jobsearch import scanner_apify

        if scanner_apify.is_enabled():
            for actor in actors_cfg:
                if not actor.get("enabled", False):
                    continue
                tags = actor.get("profile_tags") or []
                if not _matches_profile_filter(tags, profile):
                    continue

                ar = CompanyResult(
                    name=actor.get("name", "?"), source=f"apify:{actor.get('actor_id', '?')}"
                )
                try:
                    items = scanner_apify.run_actor(
                        actor["actor_id"],
                        actor.get("input") or {},
                    )
                    jobs = scanner_apify.normalize_apify_items(
                        items,
                        actor["actor_id"],
                        actor.get("field_map"),
                        default_company=actor.get("default_company") or actor.get("name", ""),
                    )
                except Exception as e:
                    ar.error = f"{type(e).__name__}: {e}"
                    report.actors.append(ar)
                    continue

                ar.fetched = len(jobs)
                title_match = build_title_filter(title_filters, tags)
                filtered = [j for j in jobs if title_match(j.title)]
                ar.filtered = len(filtered)

                for j in filtered:
                    j.profile_tag = _profile_tag_str(tags)
                all_jobs.extend(filtered)
                report.actors.append(ar)

    # ----- Aggregate, dedup, upsert -----
    report.found_total = sum(c.fetched for c in report.companies) + sum(
        a.fetched for a in report.actors
    )
    report.after_title_filter = len(all_jobs)

    # Dedup within batch (same URL from two sources)
    seen_in_batch: set[str] = set()
    batch: list[Job] = []
    for j in all_jobs:
        if not j.url or j.url in seen_in_batch:
            continue
        seen_in_batch.add(j.url)
        batch.append(j)

    # Conteo previo para reportar "nuevas" vs "enriquecidas"
    new_jobs = [j for j in batch if j.url not in seen]
    report.after_dedup = len(new_jobs)  # nuevas (no estaban antes)
    report.samples = new_jobs[:10] if new_jobs else batch[:10]

    if not dry_run and batch:
        # Upsert TODOS: los nuevos se insertan, los existentes enriquecen
        # description / remote_type / salary_text si estaban NULL.
        report.inserted = insert_scanned_jobs([j.as_dict() for j in batch])

    return report
