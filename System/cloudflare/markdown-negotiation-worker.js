/**
 * acceptmarkdown.com content negotiation for axcentdance.com (GitHub Pages origin).
 *
 * On page URLs (clean URLs without a file extension, plus "/"), the worker
 * negotiates between the HTML page and its markdown twin (<path>.md, generated
 * by scripts/generate_md_pages.py and published as static files):
 *
 *   - Accept names text/markdown EXPLICITLY and prefers it -> serve the .md
 *     twin, Content-Type: text/markdown; charset=utf-8, Vary: Accept.
 *     A wildcard match alone (* / * or text/*) never selects markdown, so
 *     generic clients (curl's default Accept, link-preview scrapers) get HTML
 *   - Accept prefers text/html (or wildcard, or no Accept header) -> serve the
 *     HTML page, Vary: Accept added
 *   - Accept matches neither (no wildcard)  -> 406 Not Acceptable
 *   - q-values are honored (RFC 9110 ordering; unsupported/malformed parts ignored)
 *
 * Asset URLs (anything with a file extension) pass through untouched.
 *
 * Deploy: Cloudflare Worker on the zone, route axcentdance.com/* (see
 * System/agent-readiness.md). No configuration or secrets needed.
 */

const MD_TYPE = 'text/markdown';
const HTML_TYPE = 'text/html';

function parseAccept(header) {
  // -> [{type, subtype, q}] sorted by q desc, specificity desc
  const out = [];
  for (const part of header.split(',')) {
    const bits = part.trim().split(';');
    const mime = bits[0].trim().toLowerCase();
    const slash = mime.indexOf('/');
    if (slash < 1) continue;
    let q = 1.0;
    for (const p of bits.slice(1)) {
      const [k, v] = p.trim().split('=');
      if (k === 'q') {
        const f = parseFloat(v);
        if (!Number.isNaN(f)) q = Math.max(0, Math.min(1, f));
      }
    }
    out.push({
      type: mime.slice(0, slash),
      subtype: mime.slice(slash + 1),
      q,
    });
  }
  return out;
}

function matchFor(mimeType, accepted) {
  // Best match for mimeType: {q, spec} with spec 2=exact, 1=type/*, 0=*/*.
  // q is -1 when nothing matches.
  const [type, subtype] = mimeType.split('/');
  let best = -1;
  let bestSpec = -1;
  for (const a of accepted) {
    let spec;
    if (a.type === type && a.subtype === subtype) spec = 2;
    else if (a.type === type && a.subtype === '*') spec = 1;
    else if (a.type === '*' && a.subtype === '*') spec = 0;
    else continue;
    if (spec > bestSpec) {
      bestSpec = spec;
      best = a.q;
    }
  }
  return { q: best, spec: bestSpec };
}

function isPageUrl(pathname) {
  if (pathname.endsWith('/')) return true;
  const last = pathname.split('/').pop();
  return !last.includes('.');
}

function mdPath(pathname) {
  if (pathname.endsWith('/')) return pathname + 'index.md';
  return pathname + '.md';
}

function withVary(response) {
  const r = new Response(response.body, response);
  const vary = r.headers.get('Vary');
  if (!vary) r.headers.set('Vary', 'Accept');
  else if (!/\baccept\b/i.test(vary.replace(/accept-\w+/gi, ''))) {
    r.headers.set('Vary', vary + ', Accept');
  }
  return r;
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method !== 'GET' && request.method !== 'HEAD') {
      return fetch(request);
    }
    if (!isPageUrl(url.pathname)) {
      return fetch(request);
    }

    const acceptHeader = request.headers.get('Accept');
    // No Accept header means "anything" (RFC 9110): serve HTML
    const accepted = acceptHeader ? parseAccept(acceptHeader) : null;
    const md = accepted ? matchFor(MD_TYPE, accepted) : { q: 0, spec: -1 };
    const html = accepted ? matchFor(HTML_TYPE, accepted) : { q: 1, spec: -1 };
    const mdScore = md.q;
    const htmlScore = html.q;
    // Markdown is served only on an EXPLICIT text/markdown entry (spec 2):
    // wildcard-only clients (curl's */*, link-preview scrapers) get HTML.
    const wantsMarkdown = md.spec === 2 && mdScore > 0 && mdScore >= htmlScore;

    if (accepted && mdScore <= 0 && htmlScore <= 0) {
      return new Response(
        '406 Not Acceptable. This URL is available as text/html or ' +
          'text/markdown. See https://axcentdance.com/llms.txt\n',
        {
          status: 406,
          headers: { 'Content-Type': 'text/plain; charset=utf-8', Vary: 'Accept' },
        },
      );
    }

    if (wantsMarkdown) {
      const twinUrl = new URL(url);
      twinUrl.pathname = mdPath(url.pathname);
      const twin = await fetch(new Request(twinUrl, request));
      if (twin.ok) {
        const r = new Response(twin.body, twin);
        r.headers.set('Content-Type', 'text/markdown; charset=utf-8');
        r.headers.set('Vary', 'Accept');
        return r;
      }
      // No twin (page is noindex or twin missing): fall through to HTML,
      // unless the client cannot accept HTML at all
      if (htmlScore <= 0) {
        return new Response('406 Not Acceptable\n', {
          status: 406,
          headers: { 'Content-Type': 'text/plain; charset=utf-8', Vary: 'Accept' },
        });
      }
    }

    return withVary(await fetch(request));
  },
};
