"""Mini-dashboard local para revisar scanned_jobs.

Levanta un servidor Flask en localhost:8765 con tabla, filtros y
botones para abrir oferta / aplicar (genera carpeta + CV + carta) /
descartar. Tambien expone reject-stats para sugerir negative keywords.

Flask is an optional dependency. Install with: ``pip install career-hub[web]``.
"""

from __future__ import annotations

import sqlite3
import traceback
from collections import Counter

from jobsearch import DB_PATH

HTML = """<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <title>JobSearch | Scanned Jobs</title>
  <style>
    body { font-family: system-ui, sans-serif; margin: 0; padding: 0; background: #fafafa; }
    header { background: #1f2937; color: #fff; padding: 12px 20px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
    header h1 { margin: 0; font-size: 18px; }
    header .meta { margin-left: auto; font-size: 13px; opacity: .8; }
    .controls { background: #fff; padding: 12px 20px; border-bottom: 1px solid #e5e7eb; display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
    .controls label { font-size: 13px; color: #374151; }
    .controls select, .controls input { padding: 6px 8px; font-size: 13px; border: 1px solid #d1d5db; border-radius: 4px; }
    .controls input[type=text] { width: 220px; }
    .controls button { padding: 6px 14px; font-size: 13px; border: 0; border-radius: 4px; background: #2563eb; color: #fff; cursor: pointer; }
    .controls button:hover { background: #1d4ed8; }
    .controls .count { margin-left: auto; font-size: 13px; color: #6b7280; }
    .controls .secondary { background: #6b7280; }
    table { width: 100%; border-collapse: collapse; background: #fff; }
    th, td { text-align: left; padding: 8px 12px; border-bottom: 1px solid #f3f4f6; font-size: 13px; vertical-align: top; }
    th { background: #f9fafb; font-weight: 600; color: #374151; position: sticky; top: 0; cursor: pointer; user-select: none; }
    tr:hover { background: #f9fafb; }
    .title { font-weight: 500; color: #111827; }
    .company { color: #2563eb; font-weight: 500; }
    .meta-tag { display: inline-block; padding: 1px 6px; font-size: 11px; background: #e5e7eb; border-radius: 3px; color: #374151; margin-right: 4px; }
    .remote-tag { background: #dbeafe; color: #1e40af; }
    .fit { font-weight: 600; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .fit-hi { background: #d1fae5; color: #065f46; }
    .fit-mid { background: #fef3c7; color: #92400e; }
    .fit-lo { background: #fee2e2; color: #991b1b; }
    .fit-na { color: #9ca3af; font-size: 11px; font-weight: normal; }
    .salary { font-size: 11px; color: #059669; }
    .actions { white-space: nowrap; }
    .actions button { padding: 4px 10px; font-size: 12px; margin-right: 4px; border: 1px solid #d1d5db; background: #fff; border-radius: 4px; cursor: pointer; }
    .actions .open { border-color: #2563eb; color: #2563eb; }
    .actions .apply { border-color: #059669; color: #059669; font-weight: 600; }
    .actions .auto { border-color: #6b7280; color: #6b7280; font-size: 11px; padding: 3px 6px; }
    .actions .reject { border-color: #dc2626; color: #dc2626; }
    .actions button:hover { background: #f3f4f6; }
    .actions button:disabled { opacity: .4; cursor: wait; }
    .empty { text-align: center; padding: 40px; color: #9ca3af; }
    .toast { position: fixed; bottom: 20px; right: 20px; background: #111827; color: #fff; padding: 12px 18px; border-radius: 6px; font-size: 13px; max-width: 400px; box-shadow: 0 4px 12px rgba(0,0,0,.2); z-index: 1000; }
    .toast.error { background: #991b1b; }
    .modal { position: fixed; inset: 0; background: rgba(0,0,0,.5); display: none; align-items: center; justify-content: center; z-index: 100; }
    .modal.show { display: flex; }
    .modal-card { background: #fff; padding: 24px; border-radius: 8px; max-width: 600px; width: 90%; max-height: 80vh; overflow-y: auto; }
    .modal-card h2 { margin-top: 0; font-size: 16px; }
    .modal-card pre { background: #f3f4f6; padding: 8px; border-radius: 4px; font-size: 12px; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
    .modal-card button { margin-top: 12px; padding: 6px 14px; border: 0; background: #2563eb; color: #fff; border-radius: 4px; cursor: pointer; margin-right: 6px; }
    .modal-card .copy-btn { background: #059669; }
    .modal-card .copy-btn:hover { background: #047857; }
    .modal-card textarea { width: 100%; min-height: 100px; font-family: monospace; font-size: 12px; padding: 8px; border: 1px solid #d1d5db; border-radius: 4px; resize: vertical; }
    .reject-list { font-size: 13px; }
    .reject-list li { margin: 2px 0; }
  </style>
</head>
<body>
<header>
  <h1>JobSearch — Scanned Jobs</h1>
  <span class="meta" id="meta">cargando...</span>
</header>
<div class="controls">
  <label>Perfil:
    <select id="profile">
      <option value="">(todos)</option>
      <option value="ai">ai</option>
      <option value="data">data</option>
      <option value="meal">meal</option>
      <option value="marketing">marketing</option>
    </select>
  </label>
  <label>Status:
    <select id="status">
      <option value="discovered" selected>discovered</option>
      <option value="evaluated">evaluated</option>
      <option value="promoted">promoted</option>
      <option value="rejected">rejected</option>
      <option value="">(todos)</option>
    </select>
  </label>
  <label>Fuente:
    <select id="source">
      <option value="">(todas)</option>
      <option value="greenhouse">greenhouse</option>
      <option value="ashby">ashby</option>
      <option value="lever">lever</option>
      <option value="workday">workday</option>
      <option value="apify:linkedin-jobs-scraper">linkedin</option>
      <option value="apify:indeed-scraper">indeed</option>
    </select>
  </label>
  <label>Remote:
    <select id="remote">
      <option value="">(todos)</option>
      <option value="remote">solo remote</option>
      <option value="onsite">solo on-site</option>
      <option value="hybrid">solo hybrid</option>
    </select>
  </label>
  <label>Buscar:
    <input type="text" id="search" placeholder="empresa o titulo">
  </label>
  <label>Limite:
    <select id="limit">
      <option value="50">50</option>
      <option value="100" selected>100</option>
      <option value="250">250</option>
      <option value="1000">1000</option>
    </select>
  </label>
  <label>Vista:
    <select id="view">
      <option value="jobs" selected>Trabajos</option>
      <option value="companies">Empresas</option>
    </select>
  </label>
  <button id="refresh">Actualizar</button>
  <button id="rejectStats" class="secondary">Ver patrones de descartes</button>
  <span class="count" id="count"></span>
</div>

<div id="breadcrumb" style="display:none; padding: 8px 20px; background: #fef3c7; border-bottom: 1px solid #fde68a; font-size: 13px;">
  <a href="#" id="back-companies" style="color:#2563eb">&larr; Volver a empresas</a>
  <span style="margin-left:8px; color:#374151"> | Empresa: <strong id="bc-company"></strong></span>
</div>

<table id="jobs-table">
  <thead>
    <tr>
      <th data-sort="fit_score">Fit %</th>
      <th data-sort="company">Empresa</th>
      <th data-sort="title">Titulo</th>
      <th>Perfil / Remote</th>
      <th>Fuente</th>
      <th>Salario</th>
      <th>Visto</th>
      <th>Acciones</th>
    </tr>
  </thead>
  <tbody id="rows"></tbody>
</table>

<table id="companies-table" style="display:none">
  <thead>
    <tr>
      <th data-csort="company">Empresa</th>
      <th data-csort="total" style="text-align:right">Total</th>
      <th data-csort="discovered" style="text-align:right">Discovered</th>
      <th data-csort="promoted" style="text-align:right">Promoted</th>
      <th data-csort="rejected" style="text-align:right">Rejected</th>
      <th data-csort="max_fit" style="text-align:right">Mejor fit</th>
      <th>Perfiles</th>
      <th data-csort="last_seen">Ultima visto</th>
    </tr>
  </thead>
  <tbody id="company-rows"></tbody>
</table>

<div class="modal" id="modal">
  <div class="modal-card">
    <h2 id="modal-title"></h2>
    <div id="modal-body"></div>
    <button onclick="document.getElementById('modal').classList.remove('show')">Cerrar</button>
  </div>
</div>

<script>
const $ = (id) => document.getElementById(id);
let sortKey = 'fit_score';
let sortDir = 'desc';
let csortKey = 'total';
let csortDir = 'desc';
let drillCompany = null;  // si esta seteado, vista jobs filtrada por esta empresa

function buildParams(extra) {
  const p = new URLSearchParams({
    profile: $('profile').value,
    status: $('status').value,
    source: $('source').value,
    remote: $('remote').value,
    search: $('search').value,
    limit: $('limit').value,
  });
  Object.entries(extra || {}).forEach(([k,v]) => p.set(k,v));
  return p;
}

async function load() {
  const view = $('view').value;
  if (view === 'companies' && !drillCompany) {
    await loadCompanies();
  } else {
    await loadJobs();
  }
}

async function loadJobs() {
  $('jobs-table').style.display = '';
  $('companies-table').style.display = 'none';
  if (drillCompany) {
    $('breadcrumb').style.display = '';
    $('bc-company').textContent = drillCompany;
  } else {
    $('breadcrumb').style.display = 'none';
  }
  const params = buildParams({sort: sortKey, dir: sortDir});
  if (drillCompany) params.set('company', drillCompany);
  $('count').textContent = 'cargando...';
  const r = await fetch('/api/jobs?' + params.toString());
  const data = await r.json();
  render(data);
}

async function loadCompanies() {
  $('jobs-table').style.display = 'none';
  $('companies-table').style.display = '';
  $('breadcrumb').style.display = 'none';
  const params = buildParams({sort: csortKey, dir: csortDir});
  $('count').textContent = 'cargando...';
  const r = await fetch('/api/companies?' + params.toString());
  const data = await r.json();
  renderCompanies(data);
}

function renderCompanies(data) {
  const tbody = $('company-rows');
  tbody.innerHTML = '';
  if (!data.companies || data.companies.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty">Sin empresas con estos filtros.</td></tr>';
    $('count').textContent = '0 empresas';
    return;
  }
  $('count').textContent = `${data.companies.length} empresas`;
  $('meta').textContent = `Total empresas: ${data.total} | Total ofertas BD: ${data.jobs_total}`;
  for (const c of data.companies) {
    const fit = c.max_fit == null ? '<span class="fit-na">sin fit</span>' : fitBadge(c.max_fit);
    const profiles = (c.profiles || []).map(p => `<span class="meta-tag">${esc(p)}</span>`).join(' ');
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';
    tr.innerHTML = `
      <td class="company">${esc(c.company)}</td>
      <td style="text-align:right; font-weight:500">${c.total}</td>
      <td style="text-align:right">${c.discovered}</td>
      <td style="text-align:right; color:#059669">${c.promoted}</td>
      <td style="text-align:right; color:#dc2626">${c.rejected}</td>
      <td style="text-align:right">${fit}</td>
      <td>${profiles}</td>
      <td style="font-size:11px;color:#6b7280">${(c.last_seen || '').slice(0,10)}</td>
    `;
    tr.onclick = () => {
      drillCompany = c.company;
      $('view').value = 'jobs';
      loadJobs();
    };
    tbody.appendChild(tr);
  }
}

function render(data) {
  const tbody = $('rows');
  tbody.innerHTML = '';
  if (!data.jobs || data.jobs.length === 0) {
    tbody.innerHTML = '<tr><td colspan="8" class="empty">Sin ofertas con estos filtros.</td></tr>';
    $('count').textContent = '0 ofertas';
    return;
  }
  $('count').textContent = `${data.jobs.length} ofertas`;
  $('meta').textContent = `Total BD: ${data.total} | Promoted: ${data.stats.promoted} | Rejected: ${data.stats.rejected}`;
  for (const j of data.jobs) {
    const tr = document.createElement('tr');
    const fit = j.fit_score == null ? '<span class="fit-na">sin fit</span>' :
                fitBadge(j.fit_score);
    const remote = j.remote_type ? `<span class="meta-tag remote-tag">${esc(j.remote_type)}</span>` : '';
    const salary = j.salary_text ? `<div class="salary">${esc(j.salary_text)}</div>` : '';
    tr.innerHTML = `
      <td>${fit}</td>
      <td class="company">${esc(j.company)}</td>
      <td class="title">${esc(j.title)}<br><span style="font-size:11px;color:#9ca3af">${esc(j.location || '')}</span></td>
      <td><span class="meta-tag">${esc(j.profile_tag || '')}</span> ${remote}</td>
      <td><span class="meta-tag">${esc((j.source || '').replace('apify:',''))}</span></td>
      <td>${salary}</td>
      <td style="font-size:11px;color:#6b7280">${(j.first_seen || '').slice(0,10)}</td>
      <td class="actions">
        <button class="open" data-url="${esc(j.url)}">Abrir</button>
        <button class="apply" data-id="${j.id}" title="Prepara carpeta + JD y genera prompt /apply">/apply</button>
        <button class="auto" data-id="${j.id}" title="Genera CV+carta automaticos sin /apply">Auto</button>
        <button class="reject" data-id="${j.id}">Descartar</button>
      </td>
    `;
    tbody.appendChild(tr);
  }
  tbody.querySelectorAll('.open').forEach(b => b.onclick = () => window.open(b.dataset.url, '_blank'));
  tbody.querySelectorAll('.apply').forEach(b => b.onclick = () => prepareApply(b.dataset.id, b));
  tbody.querySelectorAll('.auto').forEach(b => b.onclick = () => autoApply(b.dataset.id, b));
  tbody.querySelectorAll('.reject').forEach(b => b.onclick = () => mark(b.dataset.id, 'rejected', b));
}

function fitBadge(score) {
  const pct = Math.round(score * 1000) / 10;
  const cls = score >= 0.7 ? 'fit-hi' : (score >= 0.5 ? 'fit-mid' : 'fit-lo');
  return `<span class="fit ${cls}">${pct}%</span>`;
}

function esc(s) {
  return String(s == null ? '' : s).replace(/[&<>"']/g, c => (
    {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]
  ));
}

function toast(msg, isError) {
  const t = document.createElement('div');
  t.className = 'toast' + (isError ? ' error' : '');
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

async function mark(id, status, btn) {
  btn.disabled = true;
  const r = await fetch('/api/mark', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: parseInt(id), status})
  });
  if (r.ok) {
    btn.closest('tr').style.opacity = '.4';
    setTimeout(() => btn.closest('tr').remove(), 400);
    toast(`Marcado como ${status}`);
  } else {
    btn.disabled = false;
    toast('Error al marcar', true);
  }
}

async function prepareApply(id, btn) {
  btn.disabled = true;
  btn.textContent = 'Preparando...';
  try {
    const r = await fetch('/api/prepare-apply', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: parseInt(id)})
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'prepare failed');
    showPreparePrompt(data);
    btn.disabled = false;
    btn.textContent = '/apply';
  } catch (e) {
    btn.disabled = false;
    btn.textContent = '/apply';
    toast('Error: ' + e.message, true);
  }
}

function showPreparePrompt(d) {
  $('modal-title').textContent = `Listo para /apply — ${d.company}`;
  const descWarn = d.has_description ? '' :
    '<p style="color:#dc2626"><strong>Aviso:</strong> Esta oferta no tiene descripcion en BD. ' +
    'El skill /apply te pedira pegar la JD manualmente o abrir la URL.</p>';
  $('modal-body').innerHTML = `
    <p><strong>Empresa:</strong> ${esc(d.company)}<br>
       <strong>Titulo:</strong> ${esc(d.title)}<br>
       <strong>Rol detectado:</strong> ${esc(d.role_detected)}<br>
       <strong>scanned_jobs.id:</strong> ${d.scanned_id}</p>
    <p><strong>Carpeta creada:</strong></p>
    <pre>${esc(d.folder)}</pre>
    ${d.jd_path ? `<p><strong>JD guardada en:</strong> <code>JOB.txt</code> dentro de la carpeta</p>` : ''}
    ${descWarn}
    <p><strong>Prompt listo para pegar en Claude Code:</strong></p>
    <textarea id="prompt-text" readonly>${esc(d.prompt)}</textarea>
    <button class="copy-btn" onclick="copyPrompt()">Copiar prompt</button>
    <button onclick="window.open('${esc(d.url)}','_blank')">Abrir oferta original</button>
    <p style="font-size:12px;color:#6b7280;margin-top:12px">
      Pega el prompt en Claude Code. El skill <code>/apply</code> leera el JD desde
      <code>JOB.txt</code>, generara CV ATS-friendly + carta de una pagina,
      y al final podras marcar status applied con el comando que el skill te indique.
      Status actual de scanned_jobs: <strong>evaluated</strong> (no <em>promoted</em> aun).
    </p>
  `;
  $('modal').classList.add('show');
}

function copyPrompt() {
  const ta = $('prompt-text');
  ta.select();
  document.execCommand('copy');
  toast('Prompt copiado al portapapeles');
}

async function autoApply(id, btn) {
  if (!confirm('Modo Auto: crea carpeta, copia CV template y genera carta auto-humanizada (sin pasar por skill /apply). Calidad menor que /apply pero mas rapido. Continuar?')) return;
  btn.disabled = true;
  btn.textContent = '...';
  try {
    const r = await fetch('/api/apply', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({id: parseInt(id)})
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'apply failed');
    showAutoResult(data);
    btn.closest('tr').style.opacity = '.4';
    setTimeout(() => btn.closest('tr').remove(), 600);
  } catch (e) {
    btn.disabled = false;
    btn.textContent = 'Auto';
    toast('Error: ' + e.message, true);
  }
}

function showAutoResult(d) {
  $('modal-title').textContent = `Auto-apply listo — ${d.company}`;
  const fitLine = d.fit_percentage != null ? `Fit: <strong>${d.fit_percentage}%</strong>` : 'Sin fit (sin descripcion)';
  $('modal-body').innerHTML = `
    <p><strong>Rol:</strong> ${esc(d.role)} <br>${fitLine}</p>
    <p><strong>Carpeta:</strong></p><pre>${esc(d.folder)}</pre>
    ${d.cv_path ? `<p>CV copiado: <code>${esc(d.cv_path.split(/[/\\\\]/).pop())}</code></p>` : '<p style="color:#dc2626">CV no copiado</p>'}
    ${d.cover_letter_path ? `<p>Carta generada: <code>${esc(d.cover_letter_path.split(/[/\\\\]/).pop())}</code></p>` : '<p style="color:#dc2626">Carta no generada</p>'}
    <p>application_id: ${d.application_id}</p>
  `;
  $('modal').classList.add('show');
}

async function showRejectStats() {
  const r = await fetch('/api/reject-stats');
  const data = await r.json();
  $('modal-title').textContent = `Patrones de descartes (n=${data.total})`;
  if (!data.total) {
    $('modal-body').innerHTML = '<p>Aun no has descartado ofertas.</p>';
    $('modal').classList.add('show');
    return;
  }
  const list1 = data.companies.map(c => `<li>${esc(c[0])} — descartada ${c[1]}x</li>`).join('');
  const list2 = data.words.map(w => `<li><code>${esc(w[0])}</code> — ${w[1]}x en descartes vs ${w[2]}x en aceptadas</li>`).join('');
  $('modal-body').innerHTML = `
    <p>Empresas descartadas mas frecuentes (revisa si conviene quitarlas de portals.yml):</p>
    <ul class="reject-list">${list1}</ul>
    <p style="margin-top:12px">Palabras candidatas a <code>negative</code> en title_filters
       (aparecen mucho en descartes y poco en discovered/promoted):</p>
    <ul class="reject-list">${list2 || '<li>(sin candidatas claras aun)</li>'}</ul>
    <p style="font-size:12px;color:#6b7280;margin-top:12px">
      Para aplicar: edita <code>0_Internal_Organization/portals.yml</code>, anade las palabras
      a <code>title_filters.&lt;perfil&gt;.negative</code>, y corre scan otra vez.
    </p>
  `;
  $('modal').classList.add('show');
}

document.querySelectorAll('th[data-sort]').forEach(th => {
  th.onclick = () => {
    const k = th.dataset.sort;
    if (sortKey === k) sortDir = (sortDir === 'desc' ? 'asc' : 'desc');
    else { sortKey = k; sortDir = 'desc'; }
    load();
  };
});

document.querySelectorAll('th[data-csort]').forEach(th => {
  th.onclick = () => {
    const k = th.dataset.csort;
    if (csortKey === k) csortDir = (csortDir === 'desc' ? 'asc' : 'desc');
    else { csortKey = k; csortDir = 'desc'; }
    loadCompanies();
  };
});

$('refresh').onclick = load;
$('rejectStats').onclick = showRejectStats;
$('view').onchange = () => { drillCompany = null; load(); };
$('back-companies').onclick = (e) => {
  e.preventDefault();
  drillCompany = null;
  $('view').value = 'companies';
  loadCompanies();
};
['profile','status','source','remote','limit'].forEach(id => $(id).onchange = load);
$('search').oninput = (() => {
  let t;
  return () => { clearTimeout(t); t = setTimeout(load, 300); };
})();
load();
</script>
</body>
</html>"""


def get_conn():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def create_app():
    """Build the Flask app. Imports flask lazily so the rest of the package
    can be imported on machines without flask installed."""
    try:
        from flask import Flask, Response, jsonify, request
    except ImportError as exc:
        raise ImportError(
            "The 'web' command requires Flask. Install with: pip install 'career-hub[web]'"
        ) from exc

    app = Flask(__name__)

    @app.route("/")
    def index():
        return Response(HTML, mimetype="text/html; charset=utf-8")

    def _build_where(args, include_status=True):
        """Return (where_clauses, params) shared by /api/jobs and /api/companies."""
        profile = (args.get("profile") or "").strip()
        status = (args.get("status") or "").strip()
        source = (args.get("source") or "").strip()
        remote = (args.get("remote") or "").strip().lower()
        search = (args.get("search") or "").strip()
        company = (args.get("company") or "").strip()

        where = []
        params: list = []
        if include_status and status:
            where.append("status = ?")
            params.append(status)
        if profile:
            where.append(
                "(profile_tag = ? OR profile_tag LIKE ? OR profile_tag LIKE ? OR profile_tag LIKE ?)"
            )
            params.extend([profile, f"{profile},%", f"%,{profile}", f"%,{profile},%"])
        if source:
            where.append("source LIKE ?")
            params.append(f"{source}%")
        if remote == "remote":
            where.append("(lower(remote_type) LIKE '%remote%' OR lower(location) LIKE '%remote%')")
        elif remote == "onsite":
            where.append(
                "(lower(remote_type) LIKE '%onsite%' OR lower(remote_type) LIKE '%on-site%')"
            )
        elif remote == "hybrid":
            where.append("lower(remote_type) LIKE '%hybrid%'")
        if search:
            where.append("(lower(company) LIKE ? OR lower(title) LIKE ?)")
            s = f"%{search.lower()}%"
            params.extend([s, s])
        if company:
            where.append("lower(company) = ?")
            params.append(company.lower())
        return where, params

    @app.route("/api/jobs")
    def api_jobs():
        sort = (request.args.get("sort") or "fit_score").strip()
        sort_dir = (request.args.get("dir") or "desc").strip().lower()
        try:
            limit = max(1, min(int(request.args.get("limit") or 100), 2000))
        except ValueError:
            limit = 100

        if sort not in {"fit_score", "company", "title", "first_seen"}:
            sort = "fit_score"
        if sort_dir not in {"asc", "desc"}:
            sort_dir = "desc"

        where, params = _build_where(request.args)

        sql = """SELECT id, url, title, company, location, source, profile_tag,
                        first_seen, status, fit_score, remote_type, salary_text,
                        salary_usd_min, salary_usd_max
                 FROM scanned_jobs"""
        if where:
            sql += " WHERE " + " AND ".join(where)
        # NULLS LAST simulado: order by IS NULL then by col
        sql += f" ORDER BY ({sort} IS NULL), {sort} {sort_dir.upper()} LIMIT ?"
        params.append(limit)

        conn = get_conn()
        rows = conn.execute(sql, params).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM scanned_jobs").fetchone()[0]
        promoted = conn.execute(
            "SELECT COUNT(*) FROM scanned_jobs WHERE status='promoted'"
        ).fetchone()[0]
        rejected = conn.execute(
            "SELECT COUNT(*) FROM scanned_jobs WHERE status='rejected'"
        ).fetchone()[0]
        conn.close()

        return jsonify(
            {
                "jobs": [dict(r) for r in rows],
                "total": total,
                "stats": {"promoted": promoted, "rejected": rejected},
            }
        )

    @app.route("/api/companies")
    def api_companies():
        sort = (request.args.get("sort") or "total").strip()
        sort_dir = (request.args.get("dir") or "desc").strip().lower()
        if sort not in {
            "company",
            "total",
            "discovered",
            "promoted",
            "rejected",
            "max_fit",
            "last_seen",
        }:
            sort = "total"
        if sort_dir not in {"asc", "desc"}:
            sort_dir = "desc"

        where, params = _build_where(request.args, include_status=False)
        where_sql = (" WHERE " + " AND ".join(where)) if where else ""

        sql = f"""
            SELECT company,
                   COUNT(*) AS total,
                   SUM(CASE WHEN status='discovered' THEN 1 ELSE 0 END) AS discovered,
                   SUM(CASE WHEN status='promoted'   THEN 1 ELSE 0 END) AS promoted,
                   SUM(CASE WHEN status='rejected'   THEN 1 ELSE 0 END) AS rejected,
                   SUM(CASE WHEN status='evaluated'  THEN 1 ELSE 0 END) AS evaluated,
                   MAX(fit_score) AS max_fit,
                   MAX(first_seen) AS last_seen,
                   GROUP_CONCAT(DISTINCT profile_tag) AS profiles_csv
            FROM scanned_jobs
            {where_sql}
            GROUP BY company
            ORDER BY ({sort} IS NULL), {sort} {sort_dir.upper()}
            LIMIT 500
        """

        conn = get_conn()
        rows = conn.execute(sql, params).fetchall()
        jobs_total = conn.execute("SELECT COUNT(*) FROM scanned_jobs").fetchone()[0]
        companies_total = conn.execute(
            "SELECT COUNT(DISTINCT company) FROM scanned_jobs"
        ).fetchone()[0]
        conn.close()

        companies = []
        for r in rows:
            d = dict(r)
            # split & flatten profile tags csv (may have "data,ai" mixed)
            tags = set()
            for chunk in (d.pop("profiles_csv") or "").split(","):
                t = chunk.strip()
                if t:
                    tags.add(t)
            d["profiles"] = sorted(tags)
            companies.append(d)

        return jsonify(
            {
                "companies": companies,
                "total": companies_total,
                "jobs_total": jobs_total,
            }
        )

    @app.route("/api/mark", methods=["POST"])
    def api_mark():
        body = request.get_json(silent=True) or {}
        scanned_id = body.get("id")
        status = body.get("status")
        if not scanned_id or status not in (
            "discovered",
            "evaluated",
            "promoted",
            "rejected",
            "expired",
        ):
            return jsonify({"error": "bad request"}), 400
        conn = get_conn()
        with conn:
            conn.execute("UPDATE scanned_jobs SET status=? WHERE id=?", (status, scanned_id))
        conn.close()
        return jsonify({"ok": True})

    @app.route("/api/apply", methods=["POST"])
    def api_apply():
        """Auto-apply legacy: ejecuta apply_from_scanned end-to-end (CV+carta+folder)."""
        from jobsearch.apply import apply_from_scanned

        body = request.get_json(silent=True) or {}
        scanned_id = body.get("id")
        lang = body.get("lang", "es")
        role_override = body.get("role")
        if not scanned_id:
            return jsonify({"error": "missing id"}), 400
        try:
            result = apply_from_scanned(int(scanned_id), lang=lang, role_override=role_override)
            return jsonify(result)
        except ValueError as e:
            return jsonify({"error": str(e)}), 404
        except Exception as e:
            traceback.print_exc()
            return jsonify({"error": f"{type(e).__name__}: {e}"}), 500

    @app.route("/api/prepare-apply", methods=["POST"])
    def api_prepare_apply():
        """Preparar carpeta + JOB.txt y devolver prompt para pegar en Claude /apply.

        NO genera CV ni carta — eso lo hace el skill /apply en Claude. Solo:
        - Crea la carpeta de la empresa
        - Guarda JOB.txt con header de metadata + descripcion completa
        - Marca scanned_job como 'evaluated' (no 'promoted' aun)
        - Devuelve el prompt /apply listo para copy/paste
        """
        from jobsearch import ROOT
        from jobsearch.apply import _resolve_role
        from jobsearch.config import ROLE_SECTOR, SECTOR_FOLDER

        body = request.get_json(silent=True) or {}
        scanned_id = body.get("id")
        if not scanned_id:
            return jsonify({"error": "missing id"}), 400

        conn = get_conn()
        row = conn.execute("SELECT * FROM scanned_jobs WHERE id=?", (scanned_id,)).fetchone()
        if not row:
            conn.close()
            return jsonify({"error": f"scanned_jobs.id={scanned_id} no existe"}), 404

        company = row["company"]
        description = row["description"] or ""
        role = _resolve_role(row["profile_tag"])
        sector = ROLE_SECTOR.get(role, 1)

        company_folder = ROOT / SECTOR_FOLDER[sector] / company
        company_folder.mkdir(parents=True, exist_ok=True)

        jd_path = None
        if description and len(description) > 100:
            jd_path = company_folder / "JOB.txt"
            header = (
                f"Source: {row['source'] or 'unknown'}\n"
                f"URL: {row['url']}\n"
                f"Company: {company}\n"
                f"Title: {row['title']}\n"
                f"Location: {row['location'] or ''}\n"
                f"Remote: {row['remote_type'] or ''}\n"
                f"Salary: {row['salary_text'] or ''}\n"
                f"scanned_jobs.id: {scanned_id}\n"
                f"---\n\n"
            )
            jd_path.write_text(header + description, encoding="utf-8")

        # Marca como evaluated (no promoted: el promoted se hace cuando se aplique de verdad)
        with conn:
            conn.execute("UPDATE scanned_jobs SET status='evaluated' WHERE id=?", (scanned_id,))
        conn.close()

        folder_str = str(company_folder)
        prompt_text = (
            f"/apply {folder_str}\n\n"
            f"Esta postulacion (scanned_jobs.id={scanned_id}): revisa todo con tu skill, "
            f"genera CV ATS-friendly + carta de una pagina con acentos correctos. "
            f"El JD esta en JOB.txt dentro de la carpeta. Cuando termines, recuerda "
            f'actualizar status con: python jobsearch.py log --company "{company}" --status applied'
        )

        return jsonify(
            {
                "scanned_id": scanned_id,
                "company": company,
                "title": row["title"],
                "role_detected": role,
                "folder": folder_str,
                "jd_path": str(jd_path) if jd_path else None,
                "has_description": bool(jd_path),
                "url": row["url"],
                "prompt": prompt_text,
            }
        )

    @app.route("/api/reject-stats")
    def api_reject_stats():
        """Devuelve patrones de palabras frecuentes en titulos descartados
        para sugerir negative keywords."""
        conn = get_conn()
        rejected = conn.execute(
            "SELECT title, company FROM scanned_jobs WHERE status='rejected'"
        ).fetchall()
        kept = conn.execute(
            "SELECT title FROM scanned_jobs WHERE status IN ('discovered','evaluated','promoted')"
        ).fetchall()
        conn.close()

        if not rejected:
            return jsonify({"total": 0, "companies": [], "words": []})

        company_counter = Counter(r["company"] for r in rejected)

        # Word frequency: count words in rejected titles vs kept titles
        import re as _re

        STOP = {
            "de",
            "y",
            "the",
            "a",
            "in",
            "of",
            "to",
            "for",
            "and",
            "&",
            "/",
            "-",
            "en",
            "la",
            "el",
            "los",
            "las",
            "un",
            "una",
            "del",
            "al",
            "con",
            "por",
            "(",
            ")",
            ",",
            ".",
            ":",
        }

        def words_of(t):
            return [
                w.lower() for w in _re.findall(r"[A-Za-zÀ-ſ]{3,}", t or "") if w.lower() not in STOP
            ]

        rej_count: Counter = Counter()
        for r in rejected:
            for w in set(words_of(r["title"])):
                rej_count[w] += 1
        kept_count: Counter = Counter()
        for r in kept:
            for w in set(words_of(r["title"])):
                kept_count[w] += 1

        n_rej = len(rejected)
        n_kept = max(1, len(kept))
        candidates = []
        for w, rc in rej_count.most_common():
            kc = kept_count.get(w, 0)
            # Heuristic: appears in >=20% of rejects AND <5% of kept
            if rc / n_rej >= 0.20 and kc / n_kept < 0.05:
                candidates.append((w, rc, kc))
            if len(candidates) >= 10:
                break

        return jsonify(
            {
                "total": len(rejected),
                "companies": company_counter.most_common(10),
                "words": candidates,
            }
        )

    return app


def serve(host: str = "127.0.0.1", port: int = 8765):
    app = create_app()
    print(f"\n  Dashboard: http://{host}:{port}\n  Ctrl+C para detener.\n")
    app.run(host=host, port=port, debug=False, use_reloader=False)
