# Video Upload Policy: 3-Second Segmented Streaming (HLS)

This policy applies to EVERY video published on the website, on both the EN and DE versions of a page. Its goal: a visitor must never download a whole video upfront. Videos are cut into a short ~1-second bootstrap chunk followed by ~3-second chunks, and the browser fetches chunk after chunk as playback progresses. The small first chunk paints the first frame quickly and keeps the initial download burst light (important since desktop playback starts directly on the 1080p rendition); a visitor who leaves after 5 seconds has downloaded roughly 3 small chunks — not the entire file.

The technology is HLS (HTTP Live Streaming): the video is encoded into small `.ts` segment files listed in an `.m3u8` playlist. The player reads the playlist and requests segments one by one, just ahead of the playhead. This works on static hosting (GitHub Pages) because segments are plain files — no streaming server is required.

## Step 1 — The master file stays out of git

Keep the original recording (`.mov` or high-bitrate `.mp4`) on local disk only. `.gitignore` already excludes `*.mp4` and `*.mov`; never force-add a master. Only the generated segments, playlists, poster, and (optionally) a compact MP4 fallback are published.

## Step 2 — Generate the segments

From the repository root:

```bash
# Background/hero video (audio stripped):
python3 scripts/generate_hls.py <path-to-master> <name>

# Demo/performance video where sound matters:
python3 scripts/generate_hls.py <path-to-master> <name> --keep-audio

# AUDIO RULE (owner directive 2026-07-27): EVERY video is published WITHOUT
# audio by default — never pass --keep-audio unless the owner explicitly says
# a specific video should keep its sound. Do not infer it from context ("it is
# a demo", "music matters here"): the owner says it, or the audio is stripped.
# Existing owner-sanctioned exception: assets/videos/hls/aitor-demo/.

# Portrait or small-display video (renders <=720px wide on the page):
# add --mobile-only to skip the desktop rendition — for long portrait clips
# the 1080p rendition can add 50+ MB for quality nobody sees.
python3 scripts/generate_hls.py <path-to-master> <name> --keep-audio --mobile-only

# Example:
python3 scripts/generate_hls.py ~/Videos/summer-party-master.mov summer-party
```

This writes to `assets/videos/hls/<name>/`:

- `playlist.m3u8` — the master playlist. This is the ONLY URL the page references.
- `playlist_desktop.m3u8` — the same master with the variant order reversed (1080p listed first). Native HLS players start on the FIRST listed variant; `hls-video.js` points desktop-sized native viewports here so the opening seconds are not soft. Same segments, no extra weight beyond the ~300-byte playlist.
- `stream_mobile.m3u8` + `mobile_segment_NNN.ts` — 720p rendition, ~800 kbps.
- `stream_desktop.m3u8` + `desktop_segment_NNN.ts` — 1080p rendition, ~4500 kbps.

Segment plan (standard since 2026-08-11): the FIRST segment of each rendition is ~1 second (`--first-segment-seconds`, default 1), the rest follow `--segment-seconds` (default 3). Keep this bootstrap segment for every future video — do not "simplify" back to uniform segments.

The player picks the rendition automatically based on measured bandwidth and switches mid-play if the connection changes.

Why the script's ffmpeg flags matter (do not remove them):

- `-force_key_frames "0,1,4,7,…"` — pins a keyframe at t=0, t=1, then every 3 seconds (the grid honors `--segment-seconds` and `--first-segment-seconds`). Segments can only be cut at keyframes, so this grid is what produces the 1s-bootstrap-then-3s segment plan; `-g`/`-keyint_min`/`-sc_threshold 0` suppress any stray keyframes between grid points. The script reads the source frame rate with ffprobe and computes everything automatically.
- `-hls_time <bootstrap length>` — set to the SHORT first-segment length, not 3: the muxer cuts at the first keyframe after each `hls_time` elapses, so a larger value would skip the t=1 keyframe and silently swallow the bootstrap segment.
- `-hls_playlist_type vod` — marks the playlist as complete video-on-demand, enabling correct seeking.
- `format=yuv420p` at the end of each scale filter — forces 8-bit output. A 10-bit master (phones and modern cameras produce these) would otherwise yield High10-profile H.264, which iPhone/Safari hardware decoders reject: the hero would silently show only its poster on iOS. Caught 2026-08-04 with the first 10-bit HEVC master.
- Two mapped streams with `-var_stream_map` — produce the mobile + desktop renditions in one pass.

## Step 3 — The poster image

Every `<video>` element MUST have a poster: WebP, maximum 1200px wide, ideally 60–80 KB (Section 6.5 of axcent-rules). The poster — not the video — is the LCP candidate. If the video is above the fold, preload the poster (`<link rel="preload" as="image" ...>`), never the video.

```bash
cwebp -resize 1200 0 -q 90 -m 6 poster-frame.png -o assets/images/<name>-poster.webp
```

## Autoplaying hero videos (LCP protection — MANDATORY pattern since 2026-08-14)

An autoplaying above-the-fold hero follows FOUR extra rules. Each one exists
because breaking it measurably hurt Core Web Vitals:

1. **Never put the `autoplay` attribute in the markup.** A markup-level
   `autoplay` makes the browser start downloading the progressive fallback
   `src` MP4 the moment the tag is parsed — visitors then pay for the full
   MP4 *and* the HLS segments (measured: 6 MB of double-download on the
   homepage). Instead declare `data-autoplay="1"` plus `preload="none"`;
   `hls-video.js` reads the flag, attaches HLS, and starts playback itself.
   The progressive `src` stays in the markup as the no-JS fallback.
2. **Ship the poster twice: as the `poster` attribute AND as a real `<img>`
   underneath the video** (`class="…__posterframe"`, `loading="eager"`,
   `fetchpriority="high"`, correct `width`/`height`, `alt=""` +
   `aria-hidden="true"`). The `<img>` is the page's true LCP element: it
   paints at first render with no JS dependency, while a bare `<video>`
   ties the recorded LCP to the whole streaming chain. Zero visual
   difference — the video simply covers the img once frames arrive.
3. **The stream starts at `window.load`, never earlier** (handled inside
   `hls-video.js` for `data-autoplay` videos). First segments must not
   compete with CSS, fonts, and the poster on the critical path; the poster
   covers the wait. Click-to-play videos attach immediately — they move no
   bytes until the user presses play.
4. **`capLevelToPlayerSize: true` stays in the hls.js config.** It caps ABR
   at the rendered element size, so a phone-sized hero streams the 720p
   rendition even on fast wifi instead of the 1080p rung it cannot show
   (measured: −3.4 MB per homepage view).

## Step 4 — Playback integration (without this, segments are dead weight)

Two browser families must be handled:

- **Safari (macOS/iOS)** plays HLS natively: assign the `.m3u8` directly to `video.src`.
- **Chrome, Firefox, Edge** need the hls.js library, loaded lazily.

hls.js is VENDORED in-repo at `assets/vendor/hls-<version>.min.mjs` (policy
since 2026-07-27, matching the self-hosted-fonts direction: no third-party
runtime dependencies; minified twin since 2026-08-14 — generate it with
`npx -y esbuild@0.24.0 <file>.mjs --minify --format=esm --legal-comments=eof`).
Never import it from a CDN. To upgrade: download the new pinned `dist/hls.mjs`
into `assets/vendor/`, minify it the same way, update the constant in
`hls-video.js`, bump the `hls-video.js?v=` param on referencing pages, and
delete the old files.

HTML:

```html
<video id="my-video" class="…__video" muted loop playsinline
       preload="metadata" poster="assets/images/<name>-poster.webp"
       data-hls="assets/videos/hls/<name>/playlist.m3u8"></video>
```

JavaScript (add to the page's module script; adjust the selector):

```html
<script type="module">
  const video = document.getElementById('my-video');
  const src = video.dataset.hls;

  async function initHls() {
    if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = src;                      // Safari: native HLS
    } else {
      const { default: Hls } = await import('/assets/vendor/hls-1.5.13.mjs');
      if (!Hls.isSupported()) return;       // very old browsers: poster only
      const hls = new Hls({ maxBufferLength: 10 });  // buffer at most ~10s ahead
      hls.loadSource(src);
      hls.attachMedia(video);
    }
    video.play().catch(() => {});           // autoplay may be blocked; poster remains
  }

  // Lazy-init: do not touch the network until the video is near the viewport
  // (axcent-rules Section 4.2). Also pause when scrolled away.
  if (!('IntersectionObserver' in window)) { initHls(); }
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting && !video.dataset.hlsStarted) {
        video.dataset.hlsStarted = '1';
        initHls();
      } else if (!e.isIntersecting && !video.paused) {
        video.pause();
      } else if (e.isIntersecting && video.dataset.hlsStarted && video.paused) {
        video.play().catch(() => {});
      }
    }
  }, { rootMargin: '200px' });
  io.observe(video);
</script>
```

`maxBufferLength: 10` is what enforces the chunk-by-chunk behavior in hls.js: it never buffers more than ~10 seconds (about 3 segments) ahead, no matter how long the video is. Safari's native player manages its own buffer conservatively.

Pin the hls.js version (as above) rather than using `@latest`, and update it deliberately.

## Step 5 — What gets committed

- COMMIT: `assets/videos/hls/<name>/` (all `.ts` and `.m3u8` files — they are the published deliverable on this static host) and the poster WebP.
- DO NOT COMMIT: the master file.
- Optional MP4 fallback for very old browsers: only if genuinely needed; it requires `git add -f` because of the gitignore rule, and it must be a compact encode (720p, CRF 26–28, `-movflags +faststart`), never the master.

## Step 6 — QA before push

1. Serve locally and open the page in Chrome AND Safari (or verify the native branch by checking `canPlayType` returns non-empty in Safari).
2. In the browser Network tab, confirm: segments (`…_segment_000.ts`, `001`, `002`, …) arrive one at a time as the video plays — NOT one single multi-MB request. Pause the video: segment requests must stop after the small buffer fills.
3. Confirm the poster renders before playback and the page's LCP element is the poster or another static element, never the video stream.
4. Apply the identical integration to the DE page (en-de rule) and run the standard QA suite (axcent-rules Section 8).

Verification caveat for agents: in headless browser previews, IntersectionObserver callbacks may never fire, so the lazy-init appears dead. To verify the streaming itself, initialize the player directly from the console (import hls.js, `loadSource`, `attachMedia`) and confirm sequential segment requests via `performance.getEntriesByType('resource')`. The IntersectionObserver path must additionally be smoke-tested in a real browser.

## Current repository state (context for future agents)

The policy is live. `hls-video.js` (repo root, loaded as `<script type="module">`, cache-busted at `?v=1.4`) implements Step 4 for the whole site: it auto-upgrades every `<video data-hls="…/playlist.m3u8">` and exposes `window.AXHls.attach/detach` for the homepage hero switcher in `script.js`. SHARP-START ROUTING (2026-08-11): adaptive streaming used to open every video on the 720p rendition for ~3 soft seconds (hls.js's conservative default bandwidth estimate, and native players' conservative first pick). `attach` now (a) prefers hls.js over native HLS wherever MediaSource exists — this matters because RECENT CHROMIUM PLAYS HLS NATIVELY (`canPlayType('application/vnd.apple.mpegurl')` returns 'maybe'), and its built-in player ignores both hls.js config and master-playlist variant order — and (b) on viewports ≥1024px pins the hls.js start level to the top rendition (`startLevel` set in MANIFEST_PARSED, with `autoStartLoad: false` so loading cannot begin before the pin). Browsers without MSE (iOS Safari) keep native playback: phones get the mobile-first `playlist.m3u8`, desktop-sized native viewports get `playlist_desktop.m3u8` (1080p listed first, honored by AVPlayer). Small viewports keep the conservative 720p start everywhere — that rendition is their ABR target anyway. When editing `hls-video.js`, bump the `?v=` param on all referencing pages (25 at last count). BOOTSTRAP SEGMENTS (2026-08-11): all five streams were regenerated with the 1s-bootstrap segment plan, each from its master with its previously documented settings. Master locations at that regeneration: hero-home ← REPLACED 2026-08-15: the owner swapped the homepage "Bachata" hero to new footage — a bachata workshop demo (couple dancing inside a seated audience circle, brick-and-neon studio). Master: the 17.5-second 1080p `~/Downloads/hero-video-2.mp4`, encoded with default settings plus `--fade 0.4` (CRF 24 / 6000k ceiling, 1s bootstrap + 3s segments, no audio, ~11 MB total; the desktop rendition is now true 1080p — the retired reel's best source was 720p). During the same session `~/Downloads/bdw17secs-afterhandbreak.mp4` (2556x1252 crop of the same footage family) was encoded first and immediately superseded by owner request; it is NOT published. The committed no-JS fallback `assets/videos/HeroVideo_mobile.mp4` was overwritten in place with a 720p CRF 27 re-encode of the new master (no audio, same 0.4s fades, `+faststart`; the file predates the gitignore rule and stays tracked, so no `git add -f` needed). The poster `assets/images/hero-poster.webp` was regenerated from the new master's 2-second frame (1200x675, ~67 KB at cwebp q72 — q90 landed at 146 KB on this busy scene, over the 80 KB budget). The VideoObject schema on `index.html`, `de/index.html`, and `palette-preview.html` was updated in step (uploadDate 2026-08-15, duration PT17S, final Clip endOffset 17). aitor-demo ← `assets/videos/AitorGomezDemo.mov` (audio kept, sanctioned exception; MOBILE-ONLY — the demo renders ≤720px on its pages, so regenerate it with `--keep-audio --mobile-only`, never with a desktop rendition), dominican-promo ← the Desktop master, milano-congress ← `~/Downloads/169 MILANO SENSUAL EVENT NOV 2026 X SITO-2.mov` (the "-3" file no longer exists; "-2" verified frame-identical to the prior stream), ladystyle-promo ← the warm-graded intermediate (re-derivable from the raw master via the grade command above). Current streams: `assets/videos/hls/hero-home/` (homepage hero, no audio), `assets/videos/hls/aitor-demo/` (Aitor demo with audio; used by the hero choice on `index.html`/`de/index.html` and the players on `dominican-bootcamp.html` and `blog-posts/dominican-bachata-bootcamp-aitor-sara.html`, EN and DE), and `assets/videos/hls/dominican-promo/` (homepage hero choice, no audio; generated 2026-08-04 from the 15-second 4K master `~/Desktop/AXcent/AitorIntensive2025/Website Promo.mp4` — superseding the retired `dominican-trailer` stream and its 21-second master — with `--segment-seconds 2.5 --crf-desktop 18 --maxrate-desktop 12000`, an owner-requested high-definition review encode; 6 segments per rendition, ~23 MB total, streamed chunk-by-chunk; regenerated 2026-08-11 with identical settings after the owner replaced the master file in place with a new 15-second edit — the fallback `DominicanBachataPromo.mp4` was re-encoded from it too), and `assets/videos/hls/milano-congress/` (homepage hero choice, no audio; generated 2026-08-04 from the first 31 seconds (owner-requested trim, `--duration 31` — the 46-second 1080p HEVC master `~/Downloads/169 MILANO SENSUAL EVENT NOV 2026 X SITO-3.mov` itself is untouched) with `--crf-desktop 18 --maxrate-desktop 12000 --fade 0.4`, same review-encode settings, default 3-second segments; ~36 MB total (the 10-bit HEVC master is forced to 8-bit for iOS compatibility, which costs some x264 efficiency; the 0.4-second edge fades make the hero loop pass through black instead of jump-cutting) — this converted the Milano hero choice from poster-only to video, so the `data-hero-poster-frame` img was removed from `index.html`/`de/index.html` (it survives on `palette-preview.html`, whose "Your First Bachata Class" choice still uses the poster mechanism, which `script.js` retains). Its no-JS fallback is `assets/videos/MilanoCongressPromo.mp4` (720p CRF 27, no audio, force-added). `assets/videos/hls/ladystyle-promo/` (homepage hero "Bachata Lady Styling" choice, no audio; generated 2026-08-10 from the 16.7-second 1080p master `~/Documents/ChatGPT/LadyStyleVideo/ladystyle_full_sequence.mp4` (superseded 2026-08-11 by the 16.1-second re-edit `ladystyle_full_sequence_modern_transitions.mp4` in the same folder, processed through the identical grade + encode pipeline) with `--crf-desktop 18 --maxrate-desktop 12000 --fade 0.4`, same review-encode settings as the sibling hero clips; regenerated 2026-08-11 with an owner-requested warm cinematic grade — the raw master is neutral/cool fluorescent, so it is first graded into a near-lossless intermediate (`ffmpeg -vf "colortemperature=temperature=4600,eq=saturation=1.08:contrast=1.02" -c:v libx264 -crf 12 -preset slow -an`) and `generate_hls.py` plus the fallback encode run on that intermediate; any future regeneration from the raw master MUST re-apply this grade or the hero loses its warmth; ~20 MB total, 6 segments per rendition — before this the Lady Styling choice reused the shared hero reel at `data-hero-start="10"`). Its no-JS fallback is `assets/videos/LadyStylingPromo.mp4` (720p CRF 27, no audio, gitignored — must be `git add -f`ed or no-JS visitors get a dead source). `generate_hls.py` accepts `--segment-seconds` (default 3), `--crf-desktop` (default 24), `--maxrate-desktop` (default 6000 kbps), `--duration` (publish only the first N seconds; the master is never modified) and `--fade` (N-second fade-in/out through black, recommended for looping hero clips) for such cases; 3-second segments and the 6000k ceiling remain the default policy. For "crisper" requests prefer lowering desktop CRF over adding a 1440p rendition — at hero render sizes bitrate, not resolution, is what reads as crisp. Note that CRF cannot exceed the maxrate ceiling: once an encode rides the cap (CRF 21 already did on this clip), only raising `--maxrate-desktop` adds quality, and that ceiling is what protects the load statistics, so raise it deliberately and only for short showcase clips. NOTE: the compact no-JS fallback `assets/videos/DominicanBachataPromo.mp4` (720p CRF 27, no audio, encoded from the same master) is gitignored and must stay `git add -f`ed or no-JS visitors get a dead source. The progressive `HeroVideo_mobile.mp4` / `AitorGomezDemo.mp4` / `.webm` files remain committed solely as no-JavaScript fallbacks — pages keep them in `src`/`<source>` and `hls-video.js` strips them at runtime when HLS attaches. To add a new video, follow Steps 1-6; the page integration is usually just `data-hls` plus the `hls-video.js` script tag.
