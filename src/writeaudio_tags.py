import io
from mutagen import File
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TCON, APIC
from mutagen.flac import Picture
from mutagen.wave import WAVE
from PyQt6.QtCore import QBuffer, QIODevice 

def write_audio_tags_mutagen(file_path: str, new_tags: dict):
    """
    Writes new meta datas in MP3-, FLAC- or WAV-files.
    new_tags: {
        "title": str,
        "artist": str,
        "album": str,
        "year": str,
        "genre": str,
        "cover": QPixmap or None
    }
    """
    try:
        audio = File(file_path, easy=False)
        if audio is None:
            print("File format not supported")
            return False

        # MP3-Tags
        if file_path.lower().endswith(".mp3"):
            if not isinstance(audio, ID3):
                audio = ID3(file_path)

            # Clear old tags before writing new ones
            audio.delall("TIT2")
            audio.delall("TPE1")
            audio.delall("TALB")
            audio.delall("TDRC")
            audio.delall("TCON")
            audio.delall("APIC")

            # Now write new tags
            if new_tags.get("title"):
                audio["TIT2"] = TIT2(encoding=3, text=new_tags["title"])
            if new_tags.get("artist"):
                audio["TPE1"] = TPE1(encoding=3, text=new_tags["artist"])
            if new_tags.get("album"):
                audio["TALB"] = TALB(encoding=3, text=new_tags["album"])
            if new_tags.get("year"):
                audio["TDRC"] = TDRC(encoding=3, text=new_tags["year"])
            if new_tags.get("genre"):
                audio["TCON"] = TCON(encoding=3, text=new_tags["genre"])

            if new_tags.get("cover"):
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                new_tags["cover"].save(buffer, "PNG")
                image_bytes = buffer.data().data()
                audio.add(APIC(
                    encoding=3,
                    mime="image/png",
                    type=3,
                    desc="Cover",
                    data=image_bytes
                ))

            audio.save(v2_version=3)


        # FLAC-Tags
        elif file_path.lower().endswith(".flac"):
            if not hasattr(audio, "tags"):
                audio.add_tags()

            for key, value in [
                ("title", "TITLE"),
                ("artist", "ARTIST"),
                ("album", "ALBUM"),
                ("genre", "GENRE"),
                ("year", "DATE")
            ]:
                if new_tags.get(key):
                    audio.tags[value] = new_tags[key]

            if new_tags.get("cover"):
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                new_tags["cover"].save(buffer, "PNG")
                image_bytes = bytes(buffer.data())
                picture = Picture()
                picture.data = image_bytes
                picture.type = 3
                picture.mime = "image/png"
                audio.clear_pictures()
                audio.add_picture(picture)

            audio.save()

        # WAV-Tags
        elif file_path.lower().endswith(".wav"):
            if not isinstance(audio, WAVE):
                audio = WAVE(file_path)

            if not audio.tags:
                audio.add_tags()

            if new_tags.get("title"):
                audio.tags["TIT2"] = TIT2(encoding=3, text=new_tags["title"])
            if new_tags.get("artist"):
                audio.tags["TPE1"] = TPE1(encoding=3, text=new_tags["artist"])
            if new_tags.get("album"):
                audio.tags["TALB"] = TALB(encoding=3, text=new_tags["album"])
            if new_tags.get("year"):
                audio.tags["TDRC"] = TDRC(encoding=3, text=new_tags["year"])
            if new_tags.get("genre"):
                audio.tags["TCON"] = TCON(encoding=3, text=new_tags["genre"])

            if new_tags.get("cover"):
                buffer = QBuffer()
                buffer.open(QIODevice.OpenModeFlag.ReadWrite)
                new_tags["cover"].save(buffer, "PNG")
                image_bytes = bytes(buffer.data())
                audio.tags.delall("APIC")
                audio.tags.add(APIC(
                    encoding=3,
                    mime="image/png",
                    type=3,
                    desc="Cover",
                    data=image_bytes
                ))

            audio.save()

        else:
            print("File format not supported")
            return False

        return True

    except Exception as e:
        print(f"Error while writing audio tags: {e}")
        return False
