# -*- coding: utf-8 -*-

################################################################################
## Self-contained LocalMediaPlayer widget
## Generated from: localmediaplayerwhhYZz.ui
## Modified to be directly usable as a QWidget subclass.
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize, Qt)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QTextEdit, QToolButton, QVBoxLayout, QWidget)


class LocalMediaPlayer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"LocalMediaPlayer")
        Form.resize(658, 475)

        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")

        # --- Layout principal vertical ---
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        # --- Vista de video ---
        self.gv_display = QGraphicsView(Form)
        self.gv_display.setObjectName(u"gv_display")
        self.verticalLayout.addWidget(self.gv_display)

        # --- Botones del reproductor ---
        self.hla_media_player_btns = QHBoxLayout()
        self.hla_media_player_btns.setObjectName(u"hla_media_player_btns")

        self.btn_prev_frame = QPushButton(Form)
        self.btn_prev_frame.setObjectName(u"btn_prev_frame")
        self.btn_prev_frame.setIcon(QIcon.fromTheme("media-skip-backward"))
        self.hla_media_player_btns.addWidget(self.btn_prev_frame)

        self.btn_rewind = QPushButton(Form)
        self.btn_rewind.setObjectName(u"btn_rewind")
        self.btn_rewind.setIcon(QIcon.fromTheme("media-seek-backward"))
        self.hla_media_player_btns.addWidget(self.btn_rewind)

        self.btn_playpause = QPushButton(Form)
        self.btn_playpause.setObjectName(u"btn_playpause")
        self.btn_playpause.setIcon(QIcon.fromTheme("media-playback-start"))
        self.hla_media_player_btns.addWidget(self.btn_playpause)

        self.btn_stop = QPushButton(Form)
        self.btn_stop.setObjectName(u"btn_stop")
        self.btn_stop.setIcon(QIcon.fromTheme("media-playback-stop"))
        self.hla_media_player_btns.addWidget(self.btn_stop)

        self.btn_forward = QPushButton(Form)
        self.btn_forward.setObjectName(u"btn_forward")
        self.btn_forward.setIcon(QIcon.fromTheme("media-seek-forward"))
        self.hla_media_player_btns.addWidget(self.btn_forward)

        self.btn_next_frame = QPushButton(Form)
        self.btn_next_frame.setObjectName(u"btn_next_frame")
        self.btn_next_frame.setIcon(QIcon.fromTheme("media-skip-forward"))
        self.hla_media_player_btns.addWidget(self.btn_next_frame)

        self.verticalLayout.addLayout(self.hla_media_player_btns)

        # --- Selector de archivo ---
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.lbl_source = QLabel(Form)
        self.lbl_source.setObjectName(u"lbl_source")
        self.horizontalLayout.addWidget(self.lbl_source)

        self.te_filepath = QTextEdit(Form)
        self.te_filepath.setObjectName(u"te_filepath")
        self.te_filepath.setMaximumSize(QSize(16777215, 26))
        self.horizontalLayout.addWidget(self.te_filepath)

        self.tb_filepath = QToolButton(Form)
        self.tb_filepath.setObjectName(u"tb_filepath")
        self.horizontalLayout.addWidget(self.tb_filepath)

        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("LocalMediaPlayer", u"Local Media Player", None))
        self.btn_prev_frame.setText(QCoreApplication.translate("LocalMediaPlayer", u"Previous", None))
        self.btn_rewind.setText(QCoreApplication.translate("LocalMediaPlayer", u"Rewind", None))
        self.btn_playpause.setText(QCoreApplication.translate("LocalMediaPlayer", u"Play", None))
        self.btn_stop.setText(QCoreApplication.translate("LocalMediaPlayer", u"Stop", None))
        self.btn_forward.setText(QCoreApplication.translate("LocalMediaPlayer", u"Forward", None))
        self.btn_next_frame.setText(QCoreApplication.translate("LocalMediaPlayer", u"Next", None))
        self.lbl_source.setText(QCoreApplication.translate("LocalMediaPlayer", u"Source", None))
        self.tb_filepath.setText(QCoreApplication.translate("LocalMediaPlayer", u"...", None))


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LocalMediaPlayer()
    window.show()
    sys.exit(app.exec())
