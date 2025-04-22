import json
import os
import math
import ffmpeg  # Import the ffmpeg-python library

def format_time(seconds):
    """Converts seconds to HH:MM:SS.ms format."""
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def split_videos(chapters_file, chapters_per_episode):
    """Splits videos based on chapter data using ffmpeg-python."""
    try:
        with open(chapters_file, 'r', encoding='utf-8') as f:
            all_chapters_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Chapters file not found at {chapters_file}")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {chapters_file}")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_output_dir = script_dir  # Output folders will be created here

    for filename, chapters in all_chapters_data.items():
        input_filepath = os.path.join(script_dir, filename)
        if not os.path.exists(input_filepath):
            print(f"Warning: Input file not found: {input_filepath}. Skipping.")
            continue

        # Create output directory for the current video
        file_base_name = os.path.splitext(filename)[0]
        output_dir = os.path.join(base_output_dir, file_base_name)
        os.makedirs(output_dir, exist_ok=True)
        print(f"\nProcessing: {filename}")
        print(f"Outputting episodes to: {output_dir}")

        num_chapters = len(chapters)
        num_episodes = math.ceil(num_chapters / chapters_per_episode)

        for i in range(num_episodes):
            start_chapter_index = i * chapters_per_episode
            end_chapter_index = min((i + 1) * chapters_per_episode - 1, num_chapters - 1)

            start_time = chapters[start_chapter_index]['start_time']
            end_time = chapters[end_chapter_index]['end_time']

            episode_num = i + 1
            output_filename = f"ep_{episode_num:02d}.mp4"
            output_filepath = os.path.join(output_dir, output_filename)

            start_time_str = format_time(start_time)
            end_time_str = format_time(end_time)

            print(f"  Creating {output_filename} (Chapters {start_chapter_index + 1}-{end_chapter_index + 1}) - Start: {start_time_str}, End: {end_time_str}")

            # Construct ffmpeg command using ffmpeg-python
            try:
                (
                    ffmpeg
                    .input(input_filepath, ss=start_time, to=end_time)
                    .output(output_filepath, c='copy', map='0', avoid_negative_ts='make_zero', y=None)
                    .run(capture_stdout=True, capture_stderr=True, overwrite_output=True)
                )
                print(f"  Successfully created {output_filename}")
            except ffmpeg.Error as e:
                print(f"  Error creating {output_filename}:")
                print(f"  Stderr: {e.stderr.decode('utf8')}")
            except FileNotFoundError:
                print("Error: 'ffmpeg' executable not found by the ffmpeg-python library. Ensure it's installed and accessible.")
                return  # Stop processing if ffmpeg is missing

if __name__ == "__main__":
    chapters_json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'chapters.json')

    while True:
        try:
            num_chapters_str = input("How many chapters form 1 episode? ")
            chapters_per_episode = int(num_chapters_str)
            if chapters_per_episode > 0:
                break
            else:
                print("Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    split_videos(chapters_json_path, chapters_per_episode)
    print("\nSplitting process finished.")
