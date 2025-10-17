from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QApplication, QComboBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget
)
from pytube import Channel, Playlist, YouTube
from pytube.exceptions import RegexMatchError
from sys import exit


class DownloadWorker(QObject):
    progress = pyqtSignal(str)
    complete = pyqtSignal()

    def download(self, url, resolution, path):
        try:
            self.download_yt_video(url, resolution, path)
        except RegexMatchError:
            self.download_playlist_videos(url, resolution, path)
        finally:
            self.complete.emit()

    def download_yt_video(self, url, resolution, path):
        video = YouTube(url)
        self.progress.emit(f'Downloading: {video.title}')
        if resolution == 'Audio Only':
            video.streams.get_audio_only().download(path)
        elif resolution == 'Highest Resolution':
            video.streams.get_highest_resolution().download(path)
        elif resolution == 'Lowest Resolution':
            video.streams.get_lowest_resolution().download(path)
        else:
            video.streams.get_by_resolution(resolution).download(path)

    def download_playlist_videos(self, url, resolution, path):
        try:
            playlist = Playlist(url)
            for video in playlist.videos:
                self.download_yt_video(video.watch_url, resolution, path)
        except AttributeError:
            channel = Channel(url)
            for video in channel.videos:
                self.download_yt_video(video.watch_url, resolution, path)


class YoutubeDownloader(QWidget):
    download_start = pyqtSignal(str, str, str)

    def __init__(self):
        super().__init__()
        self.line = None
        self.combo = None
        self.button = None
        self.label = None
        self.path = None
        self.worker = None
        self.thread = None
        self.init_ui()

    def init_ui(self):
        self.line = QLineEdit()
        self.line.setPlaceholderText('Paste the video/playlist/channel url')

        self.combo = QComboBox()
        self.combo.addItems(['Audio Only', 'Highest Resolution', 'Lowest Resolution'])

        self.button = QPushButton('Download')
        self.button.clicked.connect(self.download)

        self.label = QLabel('<a href=http://www.github.com/pedro7><font color="black">github.com/pedro7</font></a>')
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setOpenExternalLinks(True)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.line)
        top_layout.addWidget(self.combo)

        bottom_layout = QVBoxLayout()
        bottom_layout.addWidget(self.button)
        bottom_layout.addWidget(self.label)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        self.setWindowTitle('YouTube Downloader')
        self.setFixedSize(500, 96)
        self.setLayout(layout)
        self.show()

    def download(self):
        if not self.path:
            self.path = QFileDialog().getExistingDirectory()

        if not self.path:
            return

        self.button.setEnabled(False)

        self.worker = DownloadWorker()
        self.thread = QThread()
        self.worker.moveToThread(self.thread)

        self.download_start.connect(self.worker.download)
        self.worker.progress.connect(self.set_label)
        self.worker.complete.connect(lambda: self.set_label(
            '<a href=http://www.github.com/pedro7><font color="black">github.com/pedro7</font></a>'
        ))
        self.worker.complete.connect(self.worker.deleteLater)
        self.worker.complete.connect(self.thread.quit)
        self.worker.complete.connect(self.thread.deleteLater)
        self.worker.complete.connect(lambda: self.button.setEnabled(True))

        self.thread.start()

        url = self.line.text()
        resolution = self.combo.currentText()
        self.download_start.emit(url, resolution, self.path)

    def set_label(self, text):
        self.label.setText(text)


def app():
    app = QApplication([])
    app.setStyle('Fusion')
    youtube_downloader = YoutubeDownloader()
    exit(app.exec())


if __name__ == '__main__':
    app()
