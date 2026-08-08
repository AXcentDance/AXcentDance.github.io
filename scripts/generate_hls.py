import argparse
import os
import shutil
import subprocess
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HLS_ROOT = os.path.join(ROOT_DIR, "assets", "videos", "hls")
DEFAULT_SEGMENT_SECONDS = 3.0
DEFAULT_DESKTOP_CRF = 24
DEFAULT_DESKTOP_MAXRATE = 6000  # kbps ceiling for the 1080p rendition


def probe_duration(input_video):
    """Source duration in seconds (needed to place a fade-out when no --duration trim is given)."""
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_video],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    return float(out)


def probe_fps(input_video):
    """Read the source frame rate so the keyframe interval can be locked to
    exactly the segment length. HLS can only cut segments on keyframes."""
    out = subprocess.run(
        ["ffprobe", "-v", "quiet", "-select_streams", "v:0",
         "-show_entries", "stream=r_frame_rate",
         "-of", "default=noprint_wrappers=1:nokey=1", input_video],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    num, _, den = out.partition("/")
    return float(num) / float(den or 1)


def generate_hls(input_video, name, keep_audio=False, mobile_only=False,
                 segment_seconds=DEFAULT_SEGMENT_SECONDS, desktop_crf=DEFAULT_DESKTOP_CRF,
                 desktop_maxrate=DEFAULT_DESKTOP_MAXRATE, duration=None, fade=None):
    output_dir = os.path.join(HLS_ROOT, name)
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    fps = probe_fps(input_video)
    gop = round(fps * segment_seconds)  # one keyframe per segment boundary

    # Fade in from black / out to black at the clip edges, so a looping hero
    # video passes through black instead of jump-cutting mid-move.
    fade_prefix = ""
    if fade:
        clip_end = duration or probe_duration(input_video)
        fade_prefix = "fade=t=in:st=0:d=%g,fade=t=out:st=%g:d=%g," % (
            fade, clip_end - fade, fade)

    # Two renditions:
    # 1. 720p for mobile/tablet (low bitrate ceiling)
    # 2. 1080p for desktop (higher quality)
    # The browser/hls.js picks a rendition from playlist.m3u8 by bandwidth.
    cmd = [
        "ffmpeg", "-y", "-i", input_video,

        # Stream 0: 720p (Mobile/Tablet optimized). min(...) prevents upscaling
        # when the source is smaller than the rendition target.
        # format=yuv420p forces 8-bit output: a 10-bit master would otherwise
        # produce High10-profile H.264, which iPhone/Safari hardware decoders
        # reject — the hero would silently show only its poster on iOS.
        "-filter:v:0", fade_prefix + "scale=w='min(720,iw)':h=-2,format=yuv420p",
        "-c:v:0", "libx264", "-crf:v:0", "28", "-preset:v:0", "slow",
        "-b:v:0", "800k", "-maxrate:v:0", "1000k", "-bufsize:v:0", "1500k",
        "-g:v:0", str(gop), "-keyint_min:v:0", str(gop), "-sc_threshold:v:0", "0",
    ]

    if not mobile_only:
        cmd += [
            # Stream 1: 1080p (Desktop optimized)
            "-filter:v:1", fade_prefix + "scale=w='min(1920,iw)':h=-2,format=yuv420p",
            "-c:v:1", "libx264", "-crf:v:1", str(desktop_crf), "-preset:v:1", "slow",
            "-b:v:1", "%dk" % round(desktop_maxrate * 0.75),
            "-maxrate:v:1", "%dk" % desktop_maxrate,
            "-bufsize:v:1", "%dk" % round(desktop_maxrate * 1.5),
            "-g:v:1", str(gop), "-keyint_min:v:1", str(gop), "-sc_threshold:v:1", "0",
        ]

    cmd += ["-map", "0:v"] * (1 if mobile_only else 2)

    audio_maps = 1 if mobile_only else 2
    if keep_audio:
        cmd += ["-map", "0:a?"] * audio_maps + ["-c:a", "aac", "-b:a", "96k"]
        var_stream_map = "v:0,a:0,name:mobile" if mobile_only \
            else "v:0,a:0,name:mobile v:1,a:1,name:desktop"
    else:
        cmd += ["-an"]
        var_stream_map = "v:0,name:mobile" if mobile_only \
            else "v:0,name:mobile v:1,name:desktop"

    if duration:
        # Output-side trim: frame-accurate because the streams are re-encoded.
        cmd += ["-t", "%g" % duration]

    cmd += [
        "-var_stream_map", var_stream_map,
        "-master_pl_name", "playlist.m3u8",
        "-f", "hls",
        "-hls_time", "%g" % segment_seconds,
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", os.path.join(output_dir, "%v_segment_%03d.ts"),
        os.path.join(output_dir, "stream_%v.m3u8"),
    ]

    print("Running FFmpeg HLS generation (%.6g fps, keyframe every %d frames)..." % (fps, gop))
    print(" ".join(cmd))
    subprocess.run(cmd, check=True)
    print("HLS output written to %s" % os.path.relpath(output_dir, ROOT_DIR))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Segment a video into 3-second HLS chunks under assets/videos/hls/<name>/. "
                    "See .agent/rules/video_upload_policy.md for the full publishing workflow.")
    parser.add_argument("input", help="Path to the source video (master file)")
    parser.add_argument("name", help="Output folder name, e.g. 'hero-home' or 'aitor-demo'")
    parser.add_argument("--keep-audio", action="store_true",
                        help="Keep the audio track (default: stripped, for background/hero videos)")
    parser.add_argument("--mobile-only", action="store_true",
                        help="Generate only the 720p rendition (for portrait or small-display videos "
                             "where a desktop rendition wastes tens of MB)")
    parser.add_argument("--segment-seconds", type=float, default=DEFAULT_SEGMENT_SECONDS,
                        help="Target segment length in seconds (default: %g). Shorter segments "
                             "(e.g. 2.5) waste less bandwidth on early abandons, leaving budget "
                             "for a higher-quality encode of short showcase clips."
                             % DEFAULT_SEGMENT_SECONDS)
    parser.add_argument("--crf-desktop", type=int, default=DEFAULT_DESKTOP_CRF,
                        help="CRF for the 1080p desktop rendition (default: %d; lower = higher "
                             "quality/bitrate, still capped by --maxrate-desktop)" % DEFAULT_DESKTOP_CRF)
    parser.add_argument("--maxrate-desktop", type=int, default=DEFAULT_DESKTOP_MAXRATE,
                        help="Bitrate ceiling in kbps for the 1080p desktop rendition "
                             "(default: %d). A low CRF alone cannot exceed this ceiling, so raise "
                             "it deliberately for short showcase clips only — it is what protects "
                             "the page weight statistics." % DEFAULT_DESKTOP_MAXRATE)
    parser.add_argument("--duration", type=float, default=None,
                        help="Publish only the first N seconds of the source (frame-accurate "
                             "trim; default: full length). The master file is never modified.")
    parser.add_argument("--fade", type=float, default=None,
                        help="Fade in from black at the start and out to black at the end of the "
                             "published clip, N seconds each (e.g. 0.4). Recommended for looping "
                             "hero videos so the loop passes through black instead of jump-cutting.")
    args = parser.parse_args()
    if not os.path.isfile(args.input):
        sys.exit("Input file not found: %s" % args.input)
    generate_hls(args.input, args.name, keep_audio=args.keep_audio, mobile_only=args.mobile_only,
                 segment_seconds=args.segment_seconds, desktop_crf=args.crf_desktop,
                 desktop_maxrate=args.maxrate_desktop, duration=args.duration, fade=args.fade)
