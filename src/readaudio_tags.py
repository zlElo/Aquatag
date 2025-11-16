from mutagen import File
from PyQt6.QtGui import QPixmap

def read_audio_tags(file_path: str):
    tags = {
        "title": "",
        "artist": "",
        "album": "",
        "year": "",
        "genre": "",
        "cover": None
    }

    try:
        audio = File(file_path)

        if not audio:
            return tags

        # Allgemeine Text-Tags (funktioniert für MP3, FLAC, M4A usw.)
        if audio.tags:
            tags["title"] = audio.tags.get("TIT2") and audio.tags["TIT2"].text[0] if "TIT2" in audio else audio.tags.get("title", [""])[0]
            tags["artist"] = audio.tags.get("TPE1") and audio.tags["TPE1"].text[0] if "TPE1" in audio else audio.tags.get("artist", [""])[0]
            tags["album"] = audio.tags.get("TALB") and audio.tags["TALB"].text[0] if "TALB" in audio else audio.tags.get("album", [""])[0]
            tags["year"] = str(audio.tags.get("TDRC").text[0]) if "TDRC" in audio else audio.tags.get("date", [""])[0]
            tags["genre"] = audio.tags.get("TCON") and audio.tags["TCON"].text[0] if "TCON" in audio else audio.tags.get("genre", [""])[0]

        # Cover (bei MP3/APIC oder FLAC/pictures)
        cover_data = None
        if hasattr(audio, "pictures") and audio.pictures:
            # FLAC Cover aus pictures auslesen
            cover_data = audio.pictures[0].data
        elif hasattr(audio, "tags"):
            # MP3 Cover aus APIC Frames auslesen
            for tag in audio.tags.values():
                if hasattr(tag, "FrameID") and tag.FrameID == "APIC":
                    cover_data = tag.data
                    break


        if cover_data:
            pixmap = QPixmap()
            pixmap.loadFromData(cover_data)
            tags["cover"] = pixmap

    except Exception as e:
        print(f"Error while reading file: {e}")

    return tags
