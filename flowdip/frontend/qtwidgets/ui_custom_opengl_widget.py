import numpy as np
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL import GL
import time


class CustomOpenGLWidget(QOpenGLWidget):
    """QOpenGLWidget for displaying RGB/BGR frames from shared memory, preserving aspect ratio."""

    def __init__(self, parent=None, flowdip_node=None):
        super().__init__(parent)

        # --- OpenGL and frame state ---
        self.flowdip_node = flowdip_node
        self.frame_texture = None
        self.frame_shape = None
        self.frame_dtype = None
        self.texture_created = False
        self.texture_updated = False

        # --- FPS tracking ---
        self.framecount = 0
        self.last_fps_ts = None
        self.fps = 0.0

        # --- Minimum display size ---
        self.setMinimumSize(320, 240)

    # --------------------------------------------------------------
    # OpenGL initialization
    # --------------------------------------------------------------
    def initializeGL(self):
        """Initialize OpenGL context and configure the texture object."""
        GL.glEnable(GL.GL_TEXTURE_2D)

        # Create texture
        self.frame_texture = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.frame_texture)

        # Texture parameters for smooth sampling (no nearest filtering)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_S, GL.GL_CLAMP_TO_EDGE)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_WRAP_T, GL.GL_CLAMP_TO_EDGE)

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)

    # --------------------------------------------------------------
    # Frame update signal
    # --------------------------------------------------------------
    def update_frame(self):
        """Trigger repaint when a new frame is available in shared memory."""
        self.framecount += 1
        now = time.time()

        # Update FPS every second
        if self.last_fps_ts is None:
            self.last_fps_ts = now
        else:
            elapsed = now - self.last_fps_ts
            if elapsed >= 1.0:
                self.fps = self.framecount / elapsed
                self.framecount = 0
                self.last_fps_ts = now

        # Force texture update and repaint
        self.texture_updated = False
        self.update()

    # --------------------------------------------------------------
    # OpenGL texture synchronization
    # --------------------------------------------------------------
    def parse_frame_textureGL(self):
        """Synchronize the OpenGL texture with the shared memory buffer."""
        if self.texture_updated:
            return

        frame_shape = self.flowdip_node.frame_shape
        frame_dtype = self.flowdip_node.frame_dtype

        if frame_shape is None or frame_dtype is None:
            raise ValueError("Frame shape or dtype is None. Cannot update texture.")

        # Detect size or dtype change -> reallocate GPU texture
        if frame_shape != self.frame_shape or frame_dtype != self.frame_dtype:
            self.frame_shape = frame_shape
            self.frame_dtype = frame_dtype
            self.texture_created = False

        height, width, nchannels = self.frame_shape

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.frame_texture)
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)

        if not self.texture_created:
            # Allocate new GPU texture
            GL.glTexImage2D(
                GL.GL_TEXTURE_2D, 0, GL.GL_RGB,
                width, height, 0,
                GL.GL_BGR, GL.GL_UNSIGNED_BYTE,
                self.flowdip_node.shm.buf
            )
            self.texture_created = True
        else:
            # Update existing texture
            GL.glTexSubImage2D(
                GL.GL_TEXTURE_2D, 0, 0, 0,
                width, height,
                GL.GL_BGR, GL.GL_UNSIGNED_BYTE,
                self.flowdip_node.shm.buf
            )

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
        self.texture_updated = True

    # --------------------------------------------------------------
    # Rendering routine
    # --------------------------------------------------------------
    def paintGL(self):
        """Render the current frame, preserving the original aspect ratio."""
        GL.glClearColor(0.0, 0.0, 0.0, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)

        # Update texture if needed
        try:
            self.parse_frame_textureGL()
        except Exception:
            # No frame yet
            return

        if not self.texture_created or self.frame_shape is None:
            return

        GL.glBindTexture(GL.GL_TEXTURE_2D, self.frame_texture)

        # --- Compute aspect ratio-preserving quad ---
        widget_width = self.width()
        widget_height = self.height()

        frame_h, frame_w, _ = self.frame_shape
        frame_aspect = frame_w / frame_h
        widget_aspect = widget_width / widget_height

        # Scale quad to preserve aspect ratio
        if frame_aspect > widget_aspect:
            # Frame is wider than widget -> letterbox (black bars top/bottom)
            scale_x = 1.0
            scale_y = widget_aspect / frame_aspect
        else:
            # Frame is taller -> pillarbox (black bars sides)
            scale_x = frame_aspect / widget_aspect
            scale_y = 1.0

        # --- Draw textured quad centered with correct aspect ratio ---
        GL.glBegin(GL.GL_QUADS)
        GL.glTexCoord2f(0.0, 1.0); GL.glVertex2f(-scale_x, -scale_y)
        GL.glTexCoord2f(1.0, 1.0); GL.glVertex2f(scale_x, -scale_y)
        GL.glTexCoord2f(1.0, 0.0); GL.glVertex2f(scale_x, scale_y)
        GL.glTexCoord2f(0.0, 0.0); GL.glVertex2f(-scale_x, scale_y)
        GL.glEnd()

        GL.glBindTexture(GL.GL_TEXTURE_2D, 0)
