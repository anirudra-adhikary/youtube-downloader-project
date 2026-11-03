import os
import yt_dlp

import subprocess

def my_hook(d):
    if d['status'] == 'finished':
        print("Done downloading, intercepting thumbnail for cropping...")
        
        try:
            # Get the exact filename yt-dlp just saved
            filename = d.get('info_dict', {}).get('_filename', d.get('filename'))
            if filename:
                base_name = os.path.splitext(filename)[0]
                
                # Check for the thumbnail file (usually .webp or .jpg)
                for ext in ['.jpg', '.webp', '.png', '.jpeg']:
                    thumb_path = base_name + ext
                    
                    if os.path.exists(thumb_path):
                        print("Cropping album art to a perfect center square...")
                        tmp_path = base_name + '_tmp' + ext
                        
                        # Force FFmpeg to slice off the sidebars directly on the disk file
                        subprocess.run([
                            'ffmpeg', '-y', '-i', thumb_path,
                            '-vf', 'crop=ih:ih', tmp_path
                        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        
                        # Overwrite the original with our cropped square
                        if os.path.exists(tmp_path):
                            os.replace(tmp_path, thumb_path)
                        break
        except Exception as e:
            print(f"Thumbnail intercept failed: {e}")

    elif d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%')
        speed = d.get('_speed_str', 'N/A')
        eta = d.get('_eta_str', 'N/A')
        print(f"Downloading: {percent} at {speed} ETA {eta}")


def search_and_select(query, num_results=5):
    print(f"\nSearching YouTube for: '{query}'...")
    
    ydl_opts = {
        'extract_flat': True, 
        'quiet': True,
        'no_warnings': True,
    }
    
    search_query = f"ytsearch{num_results}:{query}"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(search_query, download=False)
            entries = info.get('entries', [])
        except Exception as e:
            print(f"Search failed: {e}")
            return None

    if not entries:
        print("No results found.")
        return None

    print("\n--- Search Results ---")
    for i, entry in enumerate(entries):
        title = entry.get('title', 'Unknown Title')
        uploader = entry.get('uploader', 'Unknown Channel')
        duration = entry.get('duration')
        
        if duration:
            mins, secs = divmod(int(duration), 60)
            dur_str = f"{mins}:{secs:02d}"
        else:
            dur_str = "Live/Unknown"

        print(f"[{i+1}] {title}")
        print(f"    Channel: {uploader} | Duration: {dur_str}\n")

    print("[0] Cancel")

    while True:
        try:
            choice = int(input(f"Select a video (0-{len(entries)}): ").strip())
            if choice == 0:
                print("Search cancelled.")
                return None
            if 1 <= choice <= len(entries):
                selected_entry = entries[choice - 1]
                video_url = f"https://www.youtube.com/watch?v={selected_entry.get('id')}"
                return video_url
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")


def download_audio(url, output_dir='downloads'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio[ext=m4a]/bestaudio',
        'writethumbnail': True,
        'js_runtimes': {
            'node': {}
        },
        'restrictfilenames': False,
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
        'overwrites': True, # Overwrite if you are testing the same song again
        
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a', 
            },
            # Convert our newly cropped square into a standard JPG
            {
                'key': 'FFmpegThumbnailsConvertor',
                'format': 'jpg',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            },
        ],
    }

    try:
        print(f"\nStarting audio download:\n{url}\n")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nDownload complete! Check your 'downloads' folder.")
    except Exception as e:
        print(f"\nAn error occurred:\n{e}")
        
def show_formats(url):
    ydl_opts = {
        'js_runtimes': {'node': {}}, # Applied anti-bot here
        'quiet': True,
        'no_warnings': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
        except Exception as e:
            print(f"Error fetching video info: {e}")
            return None

    print(f"\nAvailable formats for:\n{info.get('title')}\n")
    print(
        f"{'ID':<10} {'EXT':<10} {'RESOLUTION':<15} "
        f"{'TYPE':<15} {'FILESIZE':<12} {'NOTE'}"
    )
    print("-" * 90)

    for f in formats:
        f_id = f.get('format_id')
        ext = f.get('ext')
        res = f.get('resolution', 'audio only')
        note = f.get('format_note', '')
        vcodec = f.get('vcodec')
        acodec = f.get('acodec')

        if vcodec != 'none' and acodec != 'none':
            content_type = "Video+Audio"
        elif vcodec != 'none':
            content_type = "Video Only"
        elif acodec != 'none':
            content_type = "Audio Only"
        else:
            content_type = "Unknown"

        size = f.get('filesize_approx') or f.get('filesize')

        if size:
            size_mb = f"{size / 1024 / 1024:.1f}MB"
        else:
            size_mb = "N/A"

        print(
            f"{f_id:<10} {ext:<10} {res:<15} "
            f"{content_type:<15} {size_mb:<12} {note}"
        )

    choice = input("\nEnter Format ID (example: 18 or 137+140): ")
    return choice


def download_video(url, output_dir='downloads'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # selected_format = show_formats(url)

    # if not selected_format:
    #     print("No format selected.")
    #     return

    ydl_opts = {
        'format': 'bestvideo[ext=mp4][vcodec^=avc]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        # REMOVED 'merge_output_format': 'mp4'. 
        # By removing this, yt-dlp will automatically choose MKV or MP4 based on the video codecs.
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'noplaylist': True,
        'progress_hooks': [my_hook],
        'restrictfilenames': False,
        'js_runtimes': {
            'node': {} # Applied anti-bot here
        },
    }

    try:
        print(f"\nStarting video download:\n{url}\n")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print("\nDownload complete! Check your 'downloads' folder.")
    except yt_dlp.utils.DownloadError as e:
        print(f"\nDownload error:\n{e}")
    except Exception as e:
        print(f"\nUnexpected error:\n{e}")

if __name__ == "__main__":
    print("=== YouTube Media Downloader ===")
    user_input = input("Enter a YouTube URL OR a Search Term:\n").strip()

    if not user_input:
        print("Invalid input")
        exit()

    if user_input.startswith("http://") or user_input.startswith("https://") or user_input.startswith("www."):
        url = user_input
    else:
        url = search_and_select(user_input)

    if not url:
        exit()

    choice = input(
        f"\nTarget URL: {url}\n"
        "Download audio only?\n"
        "Press Y for Yes\n"
        "Press N for No\n"
    ).strip().lower()

    if choice == 'y':
        download_audio(url)
    elif choice == 'n':
        download_video(url)
    else:
        print("Invalid choice")