from abc import ABCMeta, abstractmethod, abstractproperty

from ...third_party.qtpy.QtWidgets import *
from ...third_party.qtpy.QtCore import *
from ...third_party.qtpy.QtGui import *
from ...core.comms import Dispatch, DispatchHandle

from ...ui.widgets.utils import ICON_PATH


class PluginMeta(type):
    pass


class Plugin(QDockWidget):
    """
    Base object for plugin infrastructure.
    """
    __meta__ = ABCMeta

    _all_plugins = []
    _tool_buttons = []

    location = 'left'

    def __init__(self, parent=None):
        super(Plugin, self).__init__(parent)

        # Keep a reference to the active sub window
        self._active_window = None
        self._current_layer = None

        self._all_plugins.append(self)
        DispatchHandle.setup(self)

        # GUI Setup
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.contents = QWidget()
        self.layout_vertical = QVBoxLayout(self.contents)

        self.setWidget(self.contents)

        self.setWindowTitle(self.name)
        self.setup_ui()
        self.setup_connections()

    def _set_name(self, value):
        if isinstance(value, str):
            self.name = value
        else:
            raise TypeError("Inappropriate type for 'name' property.")

    def _get_name(self):
        return self.name

    name = abstractproperty(_set_name, _get_name)

    @abstractmethod
    def setup_ui(self):
        raise NotImplementedError()

    @abstractmethod
    def setup_connections(self):
        raise NotImplementedError()

    def add_tool_button(self, icon_path, category=None, description="",
                        callback=None, enabled=True):
        button = QToolButton()
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(25, 25))
        button.setEnabled(enabled)
        button.setToolTip(description)
        button.clicked.connect(callback if callback is not None else
                               lambda: None)

        tool_button = dict(widget=button, icon_path=icon_path,
                           category=category, description=description)

        self._tool_buttons.append(tool_button)

        return button

    @property
    def active_window(self):
        return self._active_window

    @property
    def current_layer(self):
        return self._current_layer

    @DispatchHandle.register_listener("on_activated_window")
    def set_active_window(self, window):
        self._active_window = window

    @DispatchHandle.register_listener("on_selected_layer")
    def set_active_layer(self, layer_item):
        if layer_item is not None:
            self._current_layer = layer_item.data(0, Qt.UserRole)
        else:
            self._current_layer = None
