/*
   AXcent Dance — HLS playback upgrade (3-second segmented streaming).
   Workflow reference: .agent/rules/video_upload_policy.md

   Any <video data-hls="…/playlist.m3u8"> is upgraded so the browser fetches
   3-second chunks just ahead of the playhead instead of a whole video file.
   Without JavaScript the element keeps its progressive src/<source> fallback.
*/

const HLS_CDN = '/assets/vendor/hls-1.5.13.min.mjs';

let hlsModulePromise = null;
const instances = new WeakMap();

function loadHlsModule() {
    if (!hlsModulePromise) {
        hlsModulePromise = import(HLS_CDN).then((m) => m.default);
    }
    return hlsModulePromise;
}

function detach(video) {
    const prev = instances.get(video);
    if (prev) {
        prev.destroy();
        instances.delete(video);
    }
}

function stripProgressiveFallback(video) {
    video.querySelectorAll('source').forEach((s) => s.remove());
    video.removeAttribute('src');
}

/*
   Attach an HLS playlist to a video element.
   - Safari plays HLS natively (src = playlist, preload attribute honored).
   - Other browsers stream via hls.js. maxBufferLength caps read-ahead at
     ~10 seconds (about 3 segments), enforcing chunk-by-chunk delivery.
   - autoStart false: segments only start downloading on user play.
   Resolves true when HLS is attached, false when unsupported (the caller
   should then leave or restore the progressive fallback).
*/
async function attach(video, playlistUrl, { autoStart = false } = {}) {
    detach(video);

    // Prefer hls.js wherever MediaSource exists (Chrome/Edge/Firefox/Electron
    // and macOS Safari) even though several of those could play HLS natively:
    // native players pick their own conservative first variant (Chromium's
    // built-in HLS player ignores the master-playlist order entirely), which
    // means visibly soft opening seconds on desktop. hls.js gives explicit
    // control of the starting rendition. Browsers without MSE (iOS Safari)
    // fall through to the native branch below.
    let Hls = null;
    if (window.MediaSource) {
        try {
            Hls = await loadHlsModule();
        } catch (e) {
            Hls = null; // vendor module unreachable: try native, else fallback
        }
    }

    if (!Hls || !Hls.isSupported()) {
        if (video.canPlayType('application/vnd.apple.mpegurl')) {
            stripProgressiveFallback(video);
            // Native HLS players built on AVPlayer (iOS/iPadOS Safari) begin
            // playback on the FIRST variant listed in the master playlist.
            // playlist.m3u8 lists 720p first — right for phones. The rare
            // desktop-sized native viewport gets the twin playlist with the
            // 1080p rendition listed first (same segments, only the variant
            // order differs).
            video.src = window.matchMedia('(min-width: 1024px)').matches
                ? playlistUrl.replace(/playlist\.m3u8$/, 'playlist_desktop.m3u8')
                : playlistUrl;
            // autoStart must kick loading here, mirroring hls.js's
            // startLoad(): preload="none" is honored natively, so a bare
            // src swap never reaches loadedmetadata and callers waiting on
            // it (the homepage hero switcher) would deadlock with the stage
            // faded out. autoStart callers are muted autoplay heroes, so
            // play() is safe without a gesture.
            if (autoStart) {
                video.muted = true;
                const p = video.play();
                if (p && typeof p.catch === 'function') p.catch(() => {});
            }
            return true;
        }
        return false; // no MSE and no native HLS: progressive fallback keeps working
    }

    stripProgressiveFallback(video);
    // autoStartLoad stays false even for autoplay: loading is kicked off in
    // MANIFEST_PARSED below, after the start level is pinned. Otherwise the
    // internal controllers (registered first) would pick the start fragment
    // before the pin applies.
    // capLevelToPlayerSize keeps ABR honest about the rendered element: a
    // phone-sized hero stays on the 720p rendition even on fast wifi instead
    // of ramping to the 1080p "desktop" rung it can never show.
    const hls = new Hls({ maxBufferLength: 10, autoStartLoad: false, capLevelToPlayerSize: true });
    instances.set(video, hls);
    hls.on(Hls.Events.MANIFEST_PARSED, (event, data) => {
        // Desktop viewports start on the top rendition instead of hls.js's
        // cautious default (a 500 kbps estimate that always lands on the 720p
        // rung, playing ~3 soft seconds before ABR ramps up). The poster
        // covers any extra first-frame wait, and ABR still down-switches if
        // the connection turns out slow. Phones keep the conservative start:
        // 720p is their target rendition anyway, and cellular is where the
        // fast-start assumption would actually stall.
        if (window.matchMedia('(min-width: 1024px)').matches) {
            hls.startLevel = data.levels.length - 1;
        }
        if (autoStart) {
            hls.startLoad();
        }
    });
    hls.loadSource(playlistUrl);
    hls.attachMedia(video);
    if (!autoStart) {
        video.addEventListener('play', () => hls.startLoad(), { once: true });
    }
    return true;
}

/* Expose for script.js (classic script) — used by the homepage hero switcher. */
window.AXHls = { attach, detach };

/* Auto-upgrade every declared video on the page.
   Autoplay heroes declare data-autoplay="1" instead of the autoplay attribute:
   a markup-level autoplay makes the browser start downloading the progressive
   mp4 the moment the tag is parsed, so visitors would pay for the full file
   AND the HLS segments. With data-autoplay the poster shows instantly, HLS
   attaches, and playback starts on segments only. */
/* Autoplaying heroes hold their first segment request until window.load so
   the stream never competes with CSS, fonts, and the poster on the critical
   path — the poster (visually the same frame) covers the wait. */
function whenLoaded(callback) {
    if (document.readyState === 'complete') {
        callback();
    } else {
        window.addEventListener('load', callback, { once: true });
    }
}

document.querySelectorAll('video[data-hls]').forEach((video) => {
    const auto = video.autoplay || video.dataset.autoplay === '1';
    const start = () => {
        attach(video, video.dataset.hls, { autoStart: auto })
            .then((ok) => {
                if (ok) {
                    video.dataset.hlsActive = '1';
                }
                if (auto) {
                    video.muted = true;
                    // Unsupported HLS leaves the progressive fallback in place —
                    // play() then streams the mp4 exactly as the old markup did.
                    video.play().catch(() => {});
                }
            })
            .catch(() => {});
    };
    // Click-to-play videos attach immediately (no bytes move until the user
    // presses play); only autoplaying heroes wait out the critical path.
    if (auto) {
        whenLoaded(start);
    } else {
        start();
    }
});
