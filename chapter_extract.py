import os
import json
import ffmpeg
import sys

def extract_chapters(filepath):
    """Extracts chapter information from a media file."""
    chapters = []
    try:
        probe = ffmpeg.probe(filepath, show_chapters=None)
        if 'chapters' in probe and probe['chapters']:
            for chapter in probe['chapters']:
                chapters.append({
                    'title': chapter.get('tags', {}).get('title', 'Untitled Chapter'),
                    'start_time': float(chapter.get('start_time', 0.0)),
                    'end_time': float(chapter.get('end_time', 0.0)),
                })
    except ffmpeg.Error as e:
        print(f"Error probing file {filepath}: {e.stderr.decode()}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred with file {filepath}: {e}", file=sys.stderr)
    return chapters

def scan_and_extract(directory="."):
    """Scans a directory for .m4v files and extracts chapters."""
    all_chapters_data = {}
    try:
        for filename in os.listdir(directory):
            if filename.lower().endswith(".m4v"):
                filepath = os.path.join(directory, filename)
                print(f"Processing file: {filename}")
                chapters = extract_chapters(filepath)
                if chapters:
                    all_chapters_data[filename] = chapters
                else:
                    print(f"No chapters found or error processing: {filename}")
    except FileNotFoundError:
        print(f"Error: Directory not found: {directory}", file=sys.stderr)
    except PermissionError:
        print(f"Error: Permission denied to access directory: {directory}", file=sys.stderr)
    return all_chapters_data

def main():
    """Main function to run the script."""
    current_directory = os.getcwd()
    print(f"Scanning directory: {current_directory}")
    chapter_data = scan_and_extract(current_directory)

    output_filename = "chapters.json"
    output_filepath = os.path.join(current_directory, output_filename)

    if chapter_data:
        try:
            with open(output_filepath, 'w', encoding='utf-8') as f:
                json.dump(chapter_data, f, indent=4, ensure_ascii=False)
            print(f"Chapter data successfully written to {output_filepath}")
        except IOError as e:
            print(f"Error writing JSON file {output_filepath}: {e}", file=sys.stderr)
        except Exception as e:
            print(f"An unexpected error occurred while writing JSON: {e}", file=sys.stderr)
    else:
        print("No chapter data extracted.")

if __name__ == "__main__":
    # Note: This script requires ffmpeg to be installed and accessible in the system's PATH.
    # You also need to install the ffmpeg-python library: pip install ffmpeg-python
    main()
