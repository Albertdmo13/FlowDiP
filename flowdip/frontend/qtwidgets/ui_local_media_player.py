# -*- coding: utf-8 -*-
################################################################################
## LocalMediaPlayerWidget using CustomOpenGLWidget for video rendering
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QToolButton, QVBoxLayout, QWidget,
    QCheckBox, QFileDialog
)

from flowdip.frontend.qtwidgets.ui_custom_opengl_widget import CustomOpenGLWidget

class LocalMediaPlayerWidget(QWidget):
    def __init__(self, parent=None, flowdip_node=None):
        self.flowdip_node = flowdip_node  # Reference to the associated FlowDiP node
        super().__init__(parent)
        self.video_display = None
        self.setupUi(self)
        self.setupConnections()

    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"LocalMediaPlayerWidget")
        Form.resize(658, 475)
        self.gridLayout = QGridLayout(Form)
        self.gridLayout.setObjectName(u"gridLayout")

        # --- Main vertical layout ---
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")

        # --- Video display (replaced QGraphicsView with CustomOpenGLWidget) ---
        self.video_display = CustomOpenGLWidget(Form, flowdip_node=self.flowdip_node)
        self.video_display.setObjectName(u"video_display")
        self.verticalLayout.addWidget(self.video_display)

        # --- Media player buttons ---
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

        # --- File selector + checkboxes ---
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.lbl_source = QLabel(Form)
        self.lbl_source.setObjectName(u"lbl_source")
        self.horizontalLayout.addWidget(self.lbl_source)

        self.le_filepath = QLineEdit(Form)
        self.le_filepath.setObjectName(u"le_filepath")
        self.horizontalLayout.addWidget(self.le_filepath)

        self.tb_filepath = QToolButton(Form)
        self.tb_filepath.setObjectName(u"tb_filepath")
        self.horizontalLayout.addWidget(self.tb_filepath)

        self.chk_loop = QCheckBox(Form)
        self.chk_loop.setObjectName(u"chk_loop")
        self.horizontalLayout.addWidget(self.chk_loop)

        self.chk_sync = QCheckBox(Form)
        self.chk_sync.setObjectName(u"chk_sync")
        self.horizontalLayout.addWidget(self.chk_sync)

        self.verticalLayout.addLayout(self.horizontalLayout)

        # --- Finalize layouts ---
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

    def setupConnections(self):
        """Connect button events."""
        self.tb_filepath.clicked.connect(self.select_video_file)

    def select_video_file(self):
        """Open a file dialog and update the QLineEdit with the selected path."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select video file",
            "",
            "Video files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;All files (*)"
        )
        if file_path:
            self.le_filepath.setText(file_path)
            if self.flowdip_node:
                self.flowdip_node.update_videopath(file_path)


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LocalMediaPlayerWidget()
    window.show()
    sys.exit(app.exec())
