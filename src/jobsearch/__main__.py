#!/usr/bin/env python3
"""career-hub CLI entry point.

Usage: ``career-hub <command> [options]`` (or ``python -m jobsearch``).

The user's career data lives in ``$JOBSEARCH_DATA_DIR``; everything in this
module reads ``ROOT``, ``ROLE_SECTOR``, ``SECTOR_FOLDER`` from the package
config, which in turn loads ``config.toml`` from that directory.
"""

import io
import os
import sys
from pathlib import Path

import click
from rich import box
from rich.console import Console
from rich.table import Table

console = Console(
    file=io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stdout, "buffer")
    else sys.stdout
)

# Load .env from the user's data dir if it exists (no dotenv dependency).
_user_env = Path(os.environ.get("JOBSEARCH_DATA_DIR", str(Path.home() / ".career-hub"))) / ".env"
if _user_env.exists():
    for line in _user_env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from jobsearch import DB_PATH, ROOT
from jobsearch.config import (
    FIT_THRESHOLD,
    ROLE_SECTOR,
    SECTOR_FOLDER,
    available_roles,
    default_role,
)
from jobsearch.database import (
    get_all_applications,
    get_application_by_company,
    init_db,
    insert_application,
    insert_jd_skills,
    rebuild_patterns,
    update_application,
    update_status,
)


def _role_choice():
    """Click Choice over the roles defined in the user's config.toml."""
    roles = available_roles() or ["data"]
    return click.Choice(roles)


# ---------------------------------------------------------------------------
# CLI Group
# ---------------------------------------------------------------------------


@click.group()
@click.version_option("0.1.0", prog_name="career-hub")
def cli():
    """career-hub: AI-first job application workflow over your centralized career data."""
    # Lazily initialize the SQLite tracker. Skip silently if the data dir
    # does not exist yet — the user has not run ``init`` yet, and we should
    # not fail ``--help`` or the ``init`` command itself because of that.
    if ROOT.exists():
        try:
            init_db()
        except Exception:
            pass


@cli.command()
@click.option(
    "--data-dir",
    "data_dir",
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Where to create the career-hub data directory (default: $JOBSEARCH_DATA_DIR or ~/.career-hub)",
)
@click.option(
    "--force",
    is_flag=True,
    default=False,
    help="Overwrite existing template files (folders are always preserved).",
)
def init(data_dir, force):
    """Initialize a fresh career-hub data directory with templates and a SQLite tracker."""
    from jobsearch.init_cmd import run_init

    target = Path(data_dir) if data_dir else ROOT
    summary = run_init(target, force=force)

    console.print()
    console.print(
        f"[bold green]✓ career-hub initialized[/bold green] at [bold]{summary['data_dir']}[/bold]"
    )
    if summary["folders_created"]:
        console.print(f"  [dim]Created folders:[/dim] {', '.join(summary['folders_created'])}")
    if summary["files_written"]:
        console.print(f"  [dim]Wrote files:[/dim] {', '.join(summary['files_written'])}")
    if summary["files_skipped"]:
        console.print(f"  [dim]Kept existing:[/dim] {', '.join(summary['files_skipped'])}")
    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print(f"  1. export JOBSEARCH_DATA_DIR={summary['data_dir']}")
    console.print("  2. Edit profiles/PROFILE_DATA.md (or PROFILE_PRODUCT.md) with your real data")
    console.print(
        '  3. Open this folder in Claude Code and ask: "explain this project and walk me through onboarding"'
    )
    console.print(
        '  4. Or run: [bold]career-hub fit --jd JD.docx --role data --company "Acme"[/bold]'
    )
    console.print()


# ---------------------------------------------------------------------------
# fit
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--jd", required=True, help="Ruta al archivo JD (.docx/.pdf) o texto directo")
@click.option(
    "--role", type=_role_choice(), default=None, help="Perfil a usar (auto-detecta si se omite)"
)
@click.option("--company", default="", help="Nombre de la empresa")
@click.option("--save", is_flag=True, default=True, help="Guardar fit_report.md en carpeta")
def fit(jd, role, company, save):
    """Analiza el fit entre una JD y tu perfil. Genera fit_report.md."""
    from jobsearch.fit_analyzer import analyze

    # Auto-detect role from JD content if not specified.
    # The naive heuristic from earlier versions (keyword sniffing for meal/data)
    # was tied to a specific user's profiles. Now we just fall back to the
    # default_role declared in config.toml; users can pass --role explicitly.
    if not role:
        role = default_role()
        console.print(f"[dim]Using default role: [bold]{role}[/bold][/dim]")

    # Determine output path
    save_path = None
    if save and company:
        sector = ROLE_SECTOR.get(role, 1)
        folder_name = SECTOR_FOLDER[sector]
        company_folder = ROOT / folder_name / company
        if company_folder.exists():
            save_path = company_folder / "fit_report.md"
        else:
            save_path = Path(jd).parent / "fit_report.md" if Path(jd).exists() else None
    elif save and Path(jd).exists():
        save_path = Path(jd).parent / "fit_report.md"

    try:
        report, skills = analyze(jd, role, company=company, save_to=save_path)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    # Display results
    color = "green" if report.fit_score >= FIT_THRESHOLD else "yellow"
    console.print()
    console.print(
        f"[bold]Fit Score: [{color}]{report.percentage}%[/{color}][/bold]  →  {report.recommendation}"
    )
    console.print()

    t = Table(box=box.SIMPLE, show_header=True)
    t.add_column("Componente", style="dim")
    t.add_column("Score", justify="right")
    t.add_column("Detalle")
    t.add_row(
        "Skills",
        f"{report.skills_pct}%",
        f"{report.matched_required}/{report.total_required} requeridas",
    )
    t.add_row(
        "Experiencia",
        f"{report.exp_pct}%",
        f"{report.years_profile} años vs {report.years_required} requeridos",
    )
    t.add_row("[bold]TOTAL[/bold]", f"[bold {color}]{report.percentage}%[/bold {color}]", "")
    console.print(t)

    if report.gaps:
        console.print("[bold red]Gaps:[/bold red]")
        for g in report.gaps:
            console.print(f"  ❌ {g['skill']}")

    if report.matched_skills:
        console.print("[bold green]Match:[/bold green]")
        for s in report.matched_skills[:6]:
            console.print(f"  ✅ {s['skill']}")

    if save_path:
        console.print(f"\n[dim]Reporte guardado: {save_path}[/dim]")

    # Save to DB if company provided
    if company:
        existing = get_application_by_company(company)
        if existing:
            update_application(
                existing["id"],
                fit_score=report.fit_score,
                fit_report_path=str(save_path) if save_path else None,
            )
        else:
            app_id = insert_application(
                company=company,
                role=role,
                sector=ROLE_SECTOR.get(role, 1),
                jd_text=None,
                language="es",
            )
            update_application(
                app_id,
                fit_score=report.fit_score,
                fit_report_path=str(save_path) if save_path else None,
            )
            insert_jd_skills(app_id, skills)


# ---------------------------------------------------------------------------
# upword
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--jd", required=True, help="Ruta al archivo JD o texto")
@click.option("--role", required=True, type=_role_choice())
@click.option("--company", default="la organización", help="Nombre de la empresa")
@click.option("--lang", type=click.Choice(["es", "en"]), default="es")
@click.option("--out", default=None, help="Carpeta de salida (por defecto: carpeta del JD)")
def upword(jd, role, company, lang, out):
    """Genera una carta de presentación humanizada a partir de la JD."""
    from datetime import date

    from jobsearch.cover_letter import generate_cover_letter, save_cover_letter_docx
    from jobsearch.fit_analyzer import analyze, read_jd
    from jobsearch.profiles import load_profile

    try:
        jd_text = read_jd(jd)
        profile = load_profile(role)
        report, skills = analyze(jd, role, company=company)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    text = generate_cover_letter(profile, report, jd_text, company, lang=lang)

    # Determine output path
    if out:
        out_folder = Path(out)
    elif Path(jd).exists():
        out_folder = Path(jd).parent
    else:
        sector = ROLE_SECTOR.get(role, 1)
        out_folder = ROOT / SECTOR_FOLDER[sector] / company

    today = date.today().strftime("%Y%m%d")
    out_path = out_folder / f"Carta_de_Motivo_{company.replace(' ', '_')}_{today}.docx"

    saved = save_cover_letter_docx(text, out_path)

    console.print(f"\n[bold green]✓[/bold green] Carta generada: [bold]{saved}[/bold]")
    console.print("\n[dim]--- Preview ---[/dim]")
    console.print(text[:600] + ("..." if len(text) > 600 else ""))


# ---------------------------------------------------------------------------
# apply
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--role", required=True, type=_role_choice())
@click.option("--company", required=True)
@click.option("--lang", type=click.Choice(["es", "en"]), default="es")
@click.option("--jd", default=None, help="Ruta al JD (opcional, auto-busca en carpeta)")
def apply(role, company, lang, jd):
    """Crea carpeta de postulación, copia el CV y genera la carta."""
    from datetime import date

    from jobsearch.config import ROLE_SECTOR, SECTOR_FOLDER
    from jobsearch.cover_letter import generate_cover_letter, save_cover_letter_docx
    from jobsearch.cv_builder import build_cv_copy
    from jobsearch.fit_analyzer import analyze, find_jd_in_folder
    from jobsearch.profiles import load_profile

    sector = ROLE_SECTOR.get(role, 1)
    company_folder = ROOT / SECTOR_FOLDER[sector] / company
    company_folder.mkdir(parents=True, exist_ok=True)

    console.print(f"\n[bold]Creando postulación:[/bold] {company} ({role})")

    # 1. Copy CV
    try:
        cv_path = build_cv_copy(role, company, company_folder, lang)
        console.print(f"  [green]✓[/green] CV copiado: {cv_path.name}")
    except FileNotFoundError as e:
        console.print(f"  [yellow]⚠[/yellow] {e}")
        cv_path = None

    # 2. Fit analysis if JD available
    jd_path = jd
    if not jd_path:
        detected = find_jd_in_folder(company_folder)
        if detected:
            jd_path = str(detected)
            console.print(f"  [dim]JD detectado: {detected.name}[/dim]")

    fit_report = None
    skills = []
    if jd_path:
        try:
            report, skills = analyze(
                jd_path, role, company=company, save_to=company_folder / "fit_report.md"
            )
            fit_report = report
            console.print(
                f"  [green]✓[/green] Fit score: {report.percentage}% — {report.recommendation}"
            )
        except Exception as e:
            console.print(f"  [yellow]⚠[/yellow] Fit analysis falló: {e}")

    # 3. Generate cover letter
    try:
        profile = load_profile(role)
        if fit_report is None:
            # Create minimal fit report
            from jobsearch.fit_analyzer import FitReport

            fit_report = FitReport(
                company=company,
                role=role,
                fit_score=0.7,
                skills_score=0.7,
                experience_score=0.7,
                total_required=0,
                matched_required=0,
                total_optional=0,
                matched_optional=0,
            )
        jd_text = ""
        if jd_path:
            from jobsearch.fit_analyzer import read_jd

            jd_text = read_jd(jd_path)
        text = generate_cover_letter(profile, fit_report, jd_text, company, lang)
        today = date.today().strftime("%Y%m%d")
        carta_path = company_folder / f"Carta_de_Motivo_{company.replace(' ', '_')}_{today}.docx"
        save_cover_letter_docx(text, carta_path)
        console.print(f"  [green]✓[/green] Carta generada: {carta_path.name}")
    except Exception as e:
        console.print(f"  [yellow]⚠[/yellow] Carta falló: {e}")
        carta_path = None

    # 4. Save to DB
    existing = get_application_by_company(company)
    if existing:
        update_application(
            existing["id"],
            cv_path=str(cv_path) if cv_path else None,
            cover_letter_path=str(carta_path) if carta_path else None,
            fit_score=fit_report.fit_score if fit_report else None,
        )
    else:
        app_id = insert_application(
            company=company,
            role=role,
            sector=sector,
            folder_path=str(company_folder.relative_to(ROOT)),
            language=lang,
        )
        update_application(
            app_id,
            cv_path=str(cv_path) if cv_path else None,
            cover_letter_path=str(carta_path) if carta_path else None,
            fit_score=fit_report.fit_score if fit_report else None,
        )
        if skills:
            insert_jd_skills(app_id, skills)

    console.print(f"\n[bold green]✓ Listo:[/bold green] {company_folder}")


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--company", required=True)
@click.option(
    "--status",
    required=True,
    type=click.Choice(
        [
            "pending",
            "applied",
            "interview",
            "technical_test",
            "offer",
            "hired",
            "rejected",
            "withdrawn",
        ]
    ),
)
@click.option("--role", type=_role_choice(), default=None)
@click.option("--note", default=None)
def log(company, status, role, note):
    """Registra o actualiza el estado de una postulación."""
    existing = get_application_by_company(company)
    if existing:
        update_status(existing["id"], status, note)
        console.print(f"[green]✓[/green] {company} → [bold]{status}[/bold]")
        if note:
            console.print(f"  Nota: {note}")
    else:
        if not role:
            role = click.prompt("Role", type=_role_choice())
        sector = ROLE_SECTOR.get(role, 1)
        app_id = insert_application(company=company, role=role, sector=sector)
        update_status(app_id, status, note)
        console.print(f"[green]✓[/green] Nueva entrada: {company} → [bold]{status}[/bold]")


# ---------------------------------------------------------------------------
# new
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--company", required=True)
@click.option(
    "--role", required=True, type=_role_choice(), help="Role key as defined in config.toml"
)
def new(company, role):
    """Create an empty application folder for a company under the role's sector."""
    sector_int = ROLE_SECTOR.get(role, 1)
    folder = ROOT / SECTOR_FOLDER[sector_int] / company
    folder.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]✓[/green] Folder created: {folder}")
    console.print(
        "  Drop the JD as [bold]JOB.docx[/bold] or [bold]Job.docx[/bold] into that folder."
    )


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


@cli.command()
def report():
    """Muestra el dashboard de postulaciones y patrones de skills."""
    rebuild_patterns()
    apps = get_all_applications()

    if not apps:
        console.print("[yellow]Sin postulaciones registradas. Usa 'log' para agregar.[/yellow]")
        return

    # Summary table
    from collections import Counter

    status_count = Counter(a["status"] for a in apps)
    role_count = Counter(a["role"] for a in apps)

    console.print("\n[bold]Dashboard de Postulaciones[/bold]")
    console.print(f"Total: [bold]{len(apps)}[/bold] postulaciones\n")

    t = Table(title="Por Estado", box=box.SIMPLE)
    t.add_column("Estado")
    t.add_column("Count", justify="right")
    STATUS_EMOJI = {
        "hired": "🏆",
        "interview": "🎯",
        "applied": "📤",
        "technical_test": "🧪",
        "offer": "💼",
        "rejected": "❌",
        "pending": "⏳",
        "withdrawn": "↩️",
    }
    for s, c in sorted(status_count.items(), key=lambda x: -x[1]):
        t.add_row(f"{STATUS_EMOJI.get(s, '')} {s}", str(c))
    console.print(t)

    # By role (iterate over user-defined roles from config.toml)
    t2 = Table(title="By Role", box=box.SIMPLE)
    t2.add_column("Role")
    t2.add_column("Count", justify="right")
    t2.add_column("Hired", justify="right")
    for role in available_roles():
        role_apps = [a for a in apps if a["role"] == role]
        hired = sum(1 for a in role_apps if a["status"] == "hired")
        t2.add_row(role, str(len(role_apps)), str(hired))
    console.print(t2)

    # Recent applications
    t3 = Table(title="Últimas 10 Postulaciones", box=box.SIMPLE)
    t3.add_column("Empresa")
    t3.add_column("Rol")
    t3.add_column("Estado")
    t3.add_column("Fit %", justify="right")
    for a in list(apps)[:10]:
        fit_str = f"{round(a['fit_score'] * 100, 1)}%" if a["fit_score"] else "-"
        t3.add_row(a["company"], a["role"], a["status"], fit_str)
    console.print(t3)

    # Skill gaps (skills requested but not in profile)
    from jobsearch.database import get_conn

    conn = get_conn()
    gap_skills = conn.execute("""
        SELECT skill, COUNT(*) as freq
        FROM jd_skills
        WHERE matched=0
        GROUP BY skill
        ORDER BY freq DESC
        LIMIT 8
    """).fetchall()
    conn.close()

    if gap_skills:
        t4 = Table(title="Top Skills no en tu Perfil (gaps)", box=box.SIMPLE)
        t4.add_column("Skill")
        t4.add_column("Veces pedida", justify="right")
        for g in gap_skills:
            t4.add_row(g["skill"], str(g["freq"]))
        console.print(t4)


# ---------------------------------------------------------------------------
# scan
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--profile",
    type=str,
    default="all",
    help="Profile tag to scan (matches portals.yml). Use 'all' to scan everything.",
)
@click.option("--company", default=None, help="Escanear solo una empresa por nombre")
@click.option("--dry-run", is_flag=True, help="Preview sin escribir a DB")
@click.option("--no-apify", is_flag=True, help="Saltar Apify Actors (solo ATS APIs)")
def scan(profile, company, dry_run, no_apify):
    """Descubre ofertas nuevas en portales configurados (portals.yml)."""
    from jobsearch.config import PORTALS_PATH
    from jobsearch.scanner import scan as run_scan

    target_profile = None if profile == "all" else profile

    try:
        report = run_scan(
            PORTALS_PATH,
            profile=target_profile,
            company=company,
            dry_run=dry_run,
            use_apify=not no_apify,
        )
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise SystemExit(1)

    console.print()
    header = "Portal Scan"
    if dry_run:
        header += " (DRY RUN)"
    console.print(f"[bold]{header}[/bold]")

    # ATS table
    if report.companies:
        t = Table(title="ATS APIs (Greenhouse / Ashby / Lever)", box=box.SIMPLE)
        t.add_column("Empresa")
        t.add_column("Fuente", style="dim")
        t.add_column("Encontradas", justify="right")
        t.add_column("Tras filtro", justify="right")
        t.add_column("Estado")
        for c in report.companies:
            estado = "[red]" + c.error + "[/red]" if c.error else "[green]ok[/green]"
            t.add_row(c.name, c.source, str(c.fetched), str(c.filtered), estado)
        console.print(t)

    # Apify table
    if report.actors:
        t = Table(title="Apify Actors", box=box.SIMPLE)
        t.add_column("Actor")
        t.add_column("Slug", style="dim")
        t.add_column("Encontradas", justify="right")
        t.add_column("Tras filtro", justify="right")
        t.add_column("Estado")
        for a in report.actors:
            estado = "[red]" + a.error + "[/red]" if a.error else "[green]ok[/green]"
            t.add_row(a.name, a.source, str(a.fetched), str(a.filtered), estado)
        console.print(t)

    # Summary
    console.print()
    console.print(f"[bold]Total encontradas:[/bold] {report.found_total}")
    console.print(f"[bold]Tras filtro de titulo:[/bold] {report.after_title_filter}")
    console.print(f"[bold]Nuevas (post-dedup):[/bold] {report.after_dedup}")
    if dry_run:
        console.print("[yellow]Dry run: nada se escribio a la BD.[/yellow]")
    else:
        console.print(f"[bold green]Insertadas en BD:[/bold green] {report.inserted}")

    if report.samples:
        console.print()
        console.print("[bold]Muestra:[/bold]")
        for j in report.samples:
            console.print(f"  [dim]{j.source}[/dim] {j.company} | {j.title}")
            console.print(f"     {j.url}")

    if not dry_run and report.inserted > 0:
        console.print()
        console.print("[dim]-> career-hub scanned --profile <perfil>  para ver detalles.[/dim]")


# ---------------------------------------------------------------------------
# scanned
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--profile", type=str, default=None)
@click.option(
    "--status",
    default="discovered",
    type=click.Choice(["discovered", "evaluated", "promoted", "rejected", "expired"]),
)
@click.option("--limit", default=20, type=int)
def scanned(profile, status, limit):
    """Lista ofertas descubiertas por el scanner."""
    from jobsearch.database import get_scanned_jobs

    rows = get_scanned_jobs(profile=profile, status=status, limit=limit)

    if not rows:
        console.print(
            f"[yellow]Sin ofertas con status={status}"
            + (f" y profile={profile}" if profile else "")
            + ".[/yellow]"
        )
        return

    t = Table(title=f"Scanned jobs (status={status})", box=box.SIMPLE)
    t.add_column("ID", style="dim", justify="right")
    t.add_column("Empresa")
    t.add_column("Titulo")
    t.add_column("Perfil", style="dim")
    t.add_column("Fuente", style="dim")
    t.add_column("Visto")
    for r in rows:
        seen = (r["first_seen"] or "")[:10]
        t.add_row(
            str(r["id"]), r["company"], r["title"], r["profile_tag"] or "", r["source"] or "", seen
        )
    console.print(t)
    console.print()
    console.print(
        "[dim]Para abrir una URL: revisa la tabla scanned_jobs en jobsearch.db (col url).[/dim]"
    )
    console.print(
        "[dim]Tras aplicar a una oferta, usa: career-hub scanned-mark --id N --status promoted[/dim]"
    )


# ---------------------------------------------------------------------------
# scanned-mark
# ---------------------------------------------------------------------------


@cli.command(name="scanned-mark")
@click.option("--id", "scanned_id", required=True, type=int)
@click.option(
    "--status",
    required=True,
    type=click.Choice(["discovered", "evaluated", "promoted", "rejected", "expired"]),
)
@click.option("--app-id", type=int, default=None, help="ID de application si se promueve")
@click.option("--note", default=None)
def scanned_mark(scanned_id, status, app_id, note):
    """Cambia el status de una scanned_job (e.g., a promoted/rejected)."""
    from jobsearch.database import mark_scanned_status

    mark_scanned_status(scanned_id, status, application_id=app_id, note=note)
    console.print(f"[green]ok[/green] scanned_jobs.id={scanned_id} -> {status}")


# ---------------------------------------------------------------------------
# enrich-workday: rellena descripciones de Workday existentes
# ---------------------------------------------------------------------------


@cli.command(name="enrich-workday")
@click.option("--limit", default=200, type=int)
def enrich_workday(limit):
    """Para scanned_jobs Workday sin descripcion, hace job-detail fetch."""
    import re
    import sqlite3

    from jobsearch.scanner import _strip_html, fetch_workday_job_detail

    WD_RE = re.compile(r"https?://([^/]+)/([^/]+)(/job/.+)$")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, url FROM scanned_jobs WHERE source='workday' "
        "AND (description IS NULL OR description='') LIMIT ?",
        (limit,),
    ).fetchall()
    console.print(f"[bold]Enriqueciendo {len(rows)} jobs Workday sin descripcion...[/bold]")

    ok = err = 0
    for r in rows:
        url = r["url"]
        m = WD_RE.match(url)
        if not m:
            err += 1
            continue
        host, site, ext = m.group(1), m.group(2), m.group(3)
        # tenant es la parte antes del primer punto
        tenant = host.split(".")[0]
        try:
            payload = fetch_workday_job_detail(host, tenant, site, ext)
            ji = payload.get("jobPostingInfo") or {}
            desc = _strip_html(ji.get("jobDescription") or "")
            remote = ji.get("remoteType") or ""
            if not desc:
                err += 1
                continue
            with conn:
                conn.execute(
                    "UPDATE scanned_jobs SET description=?, remote_type=COALESCE(NULLIF(remote_type,''),?) WHERE id=?",
                    (desc[:20000], remote, r["id"]),
                )
            ok += 1
            if ok % 10 == 0:
                console.print(f"  [dim]{ok} ok, {err} fallidos...[/dim]")
        except Exception:
            err += 1
    conn.close()
    console.print(f"\n[bold green]Listo:[/bold green] {ok} enriquecidos, {err} fallidos")


# ---------------------------------------------------------------------------
# fit-scanned
# ---------------------------------------------------------------------------


@cli.command(name="fit-scanned")
@click.option("--profile", type=str, default=None)
@click.option("--limit", default=30, type=int, help="Cuantos scanned_jobs procesar")
def fit_scanned(profile, limit):
    """Corre fit analysis sobre scanned_jobs con descripcion."""
    from jobsearch.apply import fit_scanned_jobs

    results = fit_scanned_jobs(profile=profile, limit=limit)
    if not results:
        console.print("[yellow]Sin scanned_jobs con descripcion sin fit aun.[/yellow]")
        console.print(
            "[dim]Tip: corre 'scan' primero para que fuentes con description (Apify, Greenhouse content=true, Ashby, Lever) llenen la BD.[/dim]"
        )
        return
    ok = sum(1 for r in results if r.get("ok"))
    console.print(f"\n[bold]Fit analizados:[/bold] {ok}/{len(results)}\n")
    for r in sorted([x for x in results if x.get("ok")], key=lambda x: -x["fit_score"])[:30]:
        color = "green" if r["fit_score"] >= 0.7 else ("yellow" if r["fit_score"] >= 0.5 else "red")
        console.print(
            f"  [{color}]{r['percentage']:>5.1f}%[/{color}]  {r['company'][:30]:<30} | {r['title'][:60]}"
        )


# ---------------------------------------------------------------------------
# web
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--host", default="127.0.0.1", help="Host del servidor")
@click.option("--port", default=8765, type=int, help="Puerto")
def web(host, port):
    """Levanta dashboard web local en http://localhost:8765 para revisar scanned_jobs."""
    from jobsearch.web import serve

    serve(host=host, port=port)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    cli()
