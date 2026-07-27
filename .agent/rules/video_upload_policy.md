# Video Upload Policy: 3-Second Segmented Streaming (HLS)

This policy applies to EVERY video published on the website, on both the EN and DE versions of a page. Its goal: a visitor must never download a whole video upfront. Videos are cut into ~3-second chunks, and the browser fetches chunk after chunk as playback progresses. A visitor who leaves after 5 seconds has downloaded roughly 2 chunks — not the entire file.

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
- `stream_mobile.m3u8` + `mobile_segment_NNN.ts` — 720p rendition, ~800 kbps.
- `stream_desktop.m3u8` + `desktop_segment_NNN.ts` — 1080p rendition, ~4500 kbps.

The player picks the rendition automatically based on measured bandwidth and switches mid-play if the connection changes.

Why the script's ffmpeg flags matter (do not remove them):

- `-hls_time 3` — target segment length of 3 seconds.
- `-g <fps*3> -keyint_min <fps*3> -sc_threshold 0` — forces a keyframe exactly every 3 seconds. Segments can only be cut at keyframes, so without a fixed keyframe grid the "3-second" setting produces uneven segments (the old top-level `assets/videos/hls/` files have 4.8 s chunks for exactly this reason). The script reads the source frame rate with ffprobe and computes this automatically.
- `-hls_playlist_type vod` — marks the playlist as complete video-on-demand, enabling correct seeking.
- Two mapped streams with `-var_stream_map` — produce the mobile + desktop renditions in one pass.

## Step 3 — The poster image

Every `<video>` element MUST have a poster: WebP, maximum 1200px wide, ideally 60–80 KB (Section 6.5 of axcent-rules). The poster — not the video — is the LCP candidate. If the video is above the fold, preload the poster (`<link rel="preload" as="image" ...>`), never the video.

```bash
cwebp -resize 1200 0 -q 90 -m 6 poster-frame.png -o assets/images/<name>-poster.webp
```

## Step 4 — Playback integration (without this, segments are dead weight)

Two browser families must be handled:

- **Safari (macOS/iOS)** plays HLS natively: assign the `.m3u8` directly to `video.src`.
- **Chrome, Firefox, Edge** need the hls.js library, loaded lazily.

hls.js is VENDORED in-repo at `assets/vendor/hls-<version>.mjs` (policy since
2026-07-27, matching the self-hosted-fonts direction: no third-party runtime
dependencies). Never import it from a CDN. To upgrade: download the new pinned
`dist/hls.mjs` into `assets/vendor/`, update the constant in `hls-video.js`,
bump the `hls-video.js?v=` param on referencing pages, and delete the old file.

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

The policy is live. `hls-video.js` (repo root, loaded as `<script type="module">`) implements Step 4 for the whole site: it auto-upgrades every `<video data-hls="…/playlist.m3u8">` and exposes `window.AXHls.attach/detach` for the homepage hero switcher in `script.js`. Current streams: `assets/videos/hls/hero-home/` (homepage hero, no audio), `assets/videos/hls/aitor-demo/` (Aitor demo with audio; used by the hero choice on `index.html`/`de/index.html` and the players on `dominican-bootcamp.html` and `blog-posts/dominican-bachata-bootcamp-aitor-sara.html`, EN and DE), and `assets/videos/hls/dominican-trailer/` (homepage hero choice, no audio; regenerated 2026-07-27 (evening) from the NEW 21-second 4K master `~/Desktop/AXcent/AitorIntensive2025/Dominican_Bachata_Website_Trailer_Aitor_21s_4K.mp4` — superseding the morning 18s cut — with `--segment-seconds 2.5 --crf-desktop 21`, owner-approved: CRF 21 rides the 6000k maxrate cap for maximum crispness on this short showcase clip; 9 segments per rendition, ~18 MB total, streamed chunk-by-chunk). `generate_hls.py` accepts `--segment-seconds` (default 3) and `--crf-desktop` (default 24) for such cases; 3-second segments remain the default policy. For "crisper" requests prefer lowering desktop CRF (bounded by the 6000k cap) over adding a 1440p rendition — at hero render sizes bitrate, not resolution, is what reads as crisp, and the cap protects load statistics. NOTE: the compact no-JS fallback `assets/videos/DominicanBachataTrailer.mp4` (720p CRF 27, regenerated from the 21s master) is gitignored and currently UNTRACKED — it must be `git add -f`ed at commit time or no-JS visitors get a dead source. The progressive `HeroVideo_mobile.mp4` / `AitorGomezDemo.mp4` / `.webm` files remain committed solely as no-JavaScript fallbacks — pages keep them in `src`/`<source>` and `hls-video.js` strips them at runtime when HLS attaches. To add a new video, follow Steps 1-6; the page integration is usually just `data-hls` plus the `hls-video.js` script tag.
