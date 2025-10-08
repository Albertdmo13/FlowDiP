# -*- coding: utf-8 -*-

################################################################################
## Self-contained LocalMediaPlayerWidget widget
## Modified to be directly usable as a QWidget subclass.
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtGui import (QIcon)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QGridLayout,
    QHBoxLayout, QLabel, QPushButton, QLineEdit, QToolButton, QVBoxLayout, 
    QWidget, QCheckBox)


class LocalMediaPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"LocalMediaPlayerWidget")
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

        # --- Selector de archivo + checkboxes ---
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.lbl_source = QLabel(Form)
        self.lbl_source.setObjectName(u"lbl_source")
        self.horizontalLayout.addWidget(self.lbl_source)

        # Usamos QLineEdit en vez de QTextEdit
        self.le_filepath = QLineEdit(Form)
        self.le_filepath.setObjectName(u"le_filepath")
        self.horizontalLayout.addWidget(self.le_filepath)

        self.tb_filepath = QToolButton(Form)
        self.tb_filepath.setObjectName(u"tb_filepath")
        self.horizontalLayout.addWidget(self.tb_filepath)

        # Checkbox Loop
        self.chk_loop = QCheckBox(Form)
        self.chk_loop.setObjectName(u"chk_loop")
        self.horizontalLayout.addWidget(self.chk_loop)

        # Checkbox Sync
        self.chk_sync = QCheckBox(Form)
        self.chk_sync.setObjectName(u"chk_sync")
        self.horizontalLayout.addWidget(self.chk_sync)

        self.verticalLayout.addLayout(self.horizontalLayout)

        # --- Finalizar layouts ---
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("LocalMediaPlayerWidget", u"Local Media Player", None))
        self.btn_prev_frame.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Previous", None))
        self.btn_rewind.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Rewind", None))
        self.btn_playpause.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Play", None))
        self.btn_stop.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Stop", None))
        self.btn_forward.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Forward", None))
        self.btn_next_frame.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Next", None))
        self.lbl_source.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Source", None))
        self.tb_filepath.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"...", None))
        self.chk_loop.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Loop", None))
        self.chk_sync.setText(QCoreApplication.translate("LocalMediaPlayerWidget", u"Sync", None))

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LocalMediaPlayerWidget()
    window.show()
    sys.exit(app.exec())
