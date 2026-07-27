/*
   AXcent Dance — HLS playback upgrade (3-second segmented streaming).
   Workflow reference: .agent/rules/video_upload_policy.md

   Any <video data-hls="…/playlist.m3u8"> is upgraded so the browser fetches
   3-second chunks just ahead of the playhead instead of a whole video file.
   Without JavaScript the element keeps its progressive src/<source> fallback.
*/

const HLS_CDN = '/assets/vendor/hls-1.5.13.mjs';

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

    if (video.canPlayType('application/vnd.apple.mpegurl')) {
        stripProgressiveFallback(video);
        video.src = playlistUrl;
        return true;
    }

    let Hls;
    try {
        Hls = await loadHlsModule();
    } catch (e) {
        return false; // CDN unreachable: progressive fallback keeps working
    }
    if (!Hls.isSupported()) {
        return false;
    }

    stripProgressiveFallback(video);
    const hls = new Hls({ maxBufferLength: 10, autoStartLoad: autoStart });
    instances.set(video, hls);
    hls.loadSource(playlistUrl);
    hls.attachMedia(video);
    if (!autoStart) {
        video.addEventListener('play', () => hls.startLoad(), { once: true });
    }
    return true;
}

/* Expose for script.js (classic script) — used by the homepage hero switcher. */
window.AXHls = { attach, detach };

/* Auto-upgrade every declared video on the page. */
document.querySelectorAll('video[data-hls]').forEach((video) => {
    const auto = video.autoplay;
    attach(video, video.dataset.hls, { autoStart: auto })
        .then((ok) => {
            if (ok) {
                video.dataset.hlsActive = '1';
                if (auto) {
                    video.muted = true;
                    video.play().catch(() => {});
                }
            }
        })
        .catch(() => {});
});
