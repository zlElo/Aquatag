import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QTabWidget, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from readaudio_tags import read_audio_tags
from writeaudio_tags import write_audio_tags_mutagen


class AquatagUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aquatag – Audio Tagging Tool")
        self.setMinimumSize(800, 500)
        self.file_path = None
        self.init_ui()

    def init_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.create_main_tab(), "Editor")
        tabs.addTab(QWidget(), "Idk")
        tabs.addTab(QWidget(), "Settings")

        layout = QVBoxLayout()
        layout.addWidget(tabs)
        self.setLayout(layout)

    def create_main_tab(self):
        main_tab = QWidget()

        label_title = QLabel("Title:")
        label_artist = QLabel("Artist:")
        label_album = QLabel("Album:")
        label_year = QLabel("Year:")
        label_genre = QLabel("Genre:")

        self.input_title = QLineEdit()
        self.input_artist = QLineEdit()
        self.input_album = QLineEdit()
        self.input_year = QLineEdit()
        self.input_genre = QLineEdit()

        load_button = QPushButton("Open file")
        save_button = QPushButton("Save")
        load_cover_button = QPushButton("Load cover")

        load_button.clicked.connect(self.load_audio_file)
        save_button.clicked.connect(self.save_audio_tags)
        load_cover_button.clicked.connect(self.load_cover_image)

        self.cover_label = QLabel()
        self.cover_label.setFixedSize(200, 200)
        self.cover_label.setStyleSheet("border: 1px solid gray; background-color: #f0f0f0;")
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setText("No cover")

        form_layout = QVBoxLayout()
        for lbl, inp in [
            (label_title, self.input_title),
            (label_artist, self.input_artist),
            (label_album, self.input_album),
            (label_year, self.input_year),
            (label_genre, self.input_genre)
        ]:
            form_layout.addWidget(lbl)
            form_layout.addWidget(inp)

        button_layout = QHBoxLayout()
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)
        button_layout.addWidget(load_cover_button)
        form_layout.addLayout(button_layout)

        main_layout = QHBoxLayout()
        main_layout.addLayout(form_layout)
        main_layout.addWidget(self.cover_label, alignment=Qt.AlignmentFlag.AlignRight)

        main_tab.setLayout(main_layout)
        return main_tab

    def load_audio_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open audio", "", "Audio Files (*.mp3 *.flac *.wav)")
        if file_path:
            self.file_path = file_path
            tags = read_audio_tags(file_path)
            self.input_title.setText(tags["title"])
            self.input_artist.setText(tags["artist"])
            self.input_album.setText(tags["album"])
            self.input_year.setText(tags["year"])
            self.input_genre.setText(tags["genre"])
            if tags["cover"]:
                scaled = tags["cover"].scaled(
                    self.cover_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
                self.cover_label.setPixmap(scaled)
            else:
                self.cover_label.clear()
                self.cover_label.setText("No cover")

    def load_cover_image(self):
        image_path, _ = QFileDialog.getOpenFileName(self, "Load cover", "", "Image Files (*.png *.jpg *.jpeg)")
        if image_path:
            pixmap = QPixmap(image_path)
            scaled = pixmap.scaled(
                self.cover_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.cover_label.setPixmap(scaled)

    def save_audio_tags(self):
        if not self.file_path:
            QMessageBox.warning(self, "Error", "Please load a file first.")
            return

        tags = {
            "title": self.input_title.text(),
            "artist": self.input_artist.text(),
            "album": self.input_album.text(),
            "year": self.input_year.text(),
            "genre": self.input_genre.text(),
            "cover": self.cover_label.pixmap()
        }

        success = write_audio_tags_mutagen(self.file_path, tags)
        if success:
            QMessageBox.information(self, "Saved", "Tags saved successfully.")
        else:
            QMessageBox.critical(self, "Error", "Failed to save audio tags.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AquatagUI()
    window.show()
    sys.exit(app.exec())