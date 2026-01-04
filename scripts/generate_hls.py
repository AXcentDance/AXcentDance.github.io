import subprocess
import os
import shutil

def generate_hls():
    # Configuration
    input_video = "assets/videos/HeroVideoAleXidan.mp4"
    output_dir = "assets/videos/hls"
    
    # Ensure output directory exists
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Command to generate HLS
    # We create two streams:
    # 1. 1080p for desktop (scaled from 4k, crf 23 for quality/size balance)
    # 2. 720x406 for mobile (re-using the scaling logic, optimized)
    # HLS segment time 4 seconds
    
    cmd = [
        "ffmpeg",
        "-i", input_video,
        
        # Stream 0: 720p (Mobile/Tablet optimized)
        "-filter:v:0", "scale=w=720:h=-2",
        "-c:v:0", "libx264", "-crf:v:0", "28", "-preset:v:0", "slow",
        "-b:v:0", "800k", "-maxrate:v:0", "1000k", "-bufsize:v:0", "1500k",
        "-g:v:0", "75", "-keyint_min:v:0", "75", "-sc_threshold:v:0", "0",
        
        # Stream 1: 1080p (Desktop optimized)
        "-filter:v:1", "scale=w=1920:h=-2",
        "-c:v:1", "libx264", "-crf:v:1", "24", "-preset:v:1", "slow",
        "-b:v:1", "4500k", "-maxrate:v:1", "6000k", "-bufsize:v:1", "9000k",
        "-g:v:1", "75", "-keyint_min:v:1", "75", "-sc_threshold:v:1", "0",

        # HLS Settings
        "-map", "0:v", "-map", "0:v",
        "-var_stream_map", "v:0,name:mobile v:1,name:desktop",
        "-master_pl_name", "playlist.m3u8",
        "-f", "hls",
        "-hls_time", "3",
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", f"{output_dir}/%v_segment_%03d.ts",
        # Remove audio as it is a background video
        "-an",
        f"{output_dir}/stream_%v.m3u8"
    ]

    print("Running FFmpeg HLS generation...")
    print(" ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("HLS Generation Successful!")
    except subprocess.CalledProcessError as e:
        print(f"Error generating HLS: {e}")

if __name__ == "__main__":
    generate_hls()
