import os
import subprocess
import base64

try:
    import mutagen
    from mutagen.oggopus import OggOpus
    from mutagen.flac import Picture
    MUTAGEN_AVAILABLE = True
except ImportError:
    MUTAGEN_AVAILABLE = False

DOWNLOADS_DIR = 'downloads'

def get_media_files():
    if not os.path.exists(DOWNLOADS_DIR):
        print(f"\nError: The '{DOWNLOADS_DIR}' folder does not exist.")
        return []
    valid_exts = ('.m4a', '.opus', '.webm', '.mp3', '.mp4', '.mkv')
    files = [f for f in os.listdir(DOWNLOADS_DIR) if f.lower().endswith(valid_exts)]
    return sorted(files)

def crop_audio():
    print("\n=== Lossless Audio Cropper (Pro Edition) ===")
    
    if not MUTAGEN_AVAILABLE:
        print("\n[WARNING] 'mutagen' library not found.")
        print("Opus cover art injection will be disabled. To enable, run: pip install mutagen\n")
    
    files = get_media_files()
    if not files:
        print("No media files found to crop. Exiting.")
        return

    print(f"\nFiles found in '{DOWNLOADS_DIR}/':")
    for i, file_name in enumerate(files):
        print(f"[{i + 1}] {file_name}")

    print("[0] Cancel")

    while True:
        try:
            choice = int(input(f"\nSelect a file to crop (0-{len(files)}): ").strip())
            if choice == 0: return
            if 1 <= choice <= len(files):
                selected_file = files[choice - 1]
                break
            print("Invalid choice. Try again.")
        except ValueError:
            print("Please enter a valid number.")

    input_path = os.path.join(DOWNLOADS_DIR, selected_file)
    base_name, original_ext = os.path.splitext(selected_file)

    print("\n--- Timestamps ---")
    start_time = input("Enter starting time (e.g., 00:00:00): ").strip()
    end_time = input("Enter ending time (e.g., 04:15): ").strip()

    if not start_time or not end_time:
        print("Invalid timestamps. Exiting.")
        return

    out_filename = f"{base_name}_cropped{original_ext}"
    output_path = os.path.join(DOWNLOADS_DIR, out_filename)

    if os.path.exists(output_path):
        if input(f"\n'{out_filename}' exists. Overwrite? (y/n): ").strip().lower() != 'y': return

    print(f"\nCropping '{selected_file}'...")
    
    is_opus = original_ext.lower() in ['.opus', '.oga', '.ogg']
    temp_jpg = os.path.join(DOWNLOADS_DIR, "temp_cover.jpg")

    # --- STEP 1: If it's an Opus file, extract the cover art first ---
    if is_opus and MUTAGEN_AVAILABLE:
        print("Extracting Opus cover art...")
        ext_cmd = ['ffmpeg', '-y', '-i', input_path, '-map', '0:v?', '-c:v', 'copy', temp_jpg]
        subprocess.run(ext_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # --- STEP 2: Build the FFmpeg Crop Command ---
    command = [
        'ffmpeg', '-y', 
        '-i', input_path, 
        '-ss', start_time, 
        '-to', end_time,
    ]

    # If it's M4A/MP3, it safely supports standard picture streaming
    if not is_opus:
        command.extend(['-map', '0']) 
    # If it's Opus, we ONLY map the audio to prevent the FFmpeg crash
    else:
        command.extend(['-map', '0:a'])

    command.extend([
        '-map_metadata', '0', 
        '-c', 'copy', 
        output_path
    ])

    try:
        # Run the crop
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        
        # --- STEP 3: Inject the Cover Art back into the Opus file ---
        if is_opus and MUTAGEN_AVAILABLE and os.path.exists(temp_jpg):
            print("Re-injecting cover art into the new Opus file...")
            try:
                audio = OggOpus(output_path)
                picture = Picture()
                
                with open(temp_jpg, "rb") as f:
                    picture.data = f.read()
                
                picture.type = 3 # 3 means "Cover (front)"
                picture.mime = "image/jpeg"
                picture.desc = "Cover"
                
                # Convert the image to base64 text and inject it
                picture_data = picture.write()
                encoded_data = base64.b64encode(picture_data).decode("ascii")
                audio["metadata_block_picture"] = [encoded_data]
                audio.save()
                
            except Exception as embed_err:
                print(f"Warning: Could not embed cover art: {embed_err}")
            finally:
                # Clean up the temporary picture
                if os.path.exists(temp_jpg):
                    os.remove(temp_jpg)

        print(f"\nSuccess! Cropped file saved as: {output_path}")
    
    except subprocess.CalledProcessError as e:
        print("\nAn error occurred while cropping:")
        print(e.stderr.decode('utf-8'))

if __name__ == "__main__":
    try:
        crop_audio()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")