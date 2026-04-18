from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import Callable

from PySide6.QtCore import QObject, QTimer, Qt, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFrame,
    QFormLayout,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QInputDialog,
    QSizePolicy,
    QSplitter,
    QSystemTrayIcon,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .icons import launcher_pixmap, make_app_icon
from .i18n import I18N
from .models import WarpProfile, WarpState
from .profile_store import ProfileStore
from .theme import WINDOW_STYLESHEET
from .warp_cli import WarpCli

PROTOCOL_OPTIONS = [
    ("MASQUE", "MASQUE"),
    ("WireGuard", "WireGuard"),
]


class UiBridge(QObject):
    state_ready = Signal(object)
    action_failed = Signal(str, str)
    busy_changed = Signal(bool)


class MainWindow(QMainWindow):
    def __init__(self, cli: WarpCli, profile_store: ProfileStore) -> None:
        super().__init__()
        self.cli = cli
        self.i18n = I18N()
        self.profile_store = profile_store
        self.profiles = self.profile_store.load()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.state = WarpState()
        self.current_jobs = 0
        self.bridge = UiBridge()
        self.bridge.state_ready.connect(self._apply_state)
        self.bridge.action_failed.connect(self._handle_error)
        self.bridge.busy_changed.connect(self._set_busy)

        self.setWindowTitle(self.i18n.t("app_title"))
        self.resize(1180, 760)
        self.setMinimumSize(1024, 680)
        self.setStyleSheet(WINDOW_STYLESHEET)
        self.setWindowIcon(make_app_icon())
        self.tray_icon: QSystemTrayIcon | None = None

        self._build_ui()
        self._build_tray()

        self.poll_timer = QTimer(self)
        self.poll_timer.setInterval(4000)
        self.poll_timer.timeout.connect(self.refresh_state)
        self.poll_timer.start()

        self.refresh_state()

    def closeEvent(self, event) -> None:  # type: ignore[override]
        if self.tray_icon is not None and self.tray_icon.isVisible():
            self.hide()
            event.ignore()
            return
        super().closeEvent(event)

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(14, 14, 14, 14)
        outer.setSpacing(12)

        topbar = QFrame(objectName="TopBar")
        topbar_layout = QHBoxLayout(topbar)
        topbar_layout.setContentsMargins(14, 12, 14, 12)
        topbar_layout.setSpacing(10)

        app_mark = QLabel()
        app_mark.setObjectName("AppMark")
        app_mark.setAlignment(Qt.AlignCenter)
        app_mark.setFixedSize(28, 28)
        app_mark.setPixmap(launcher_pixmap(22))
        topbar_layout.addWidget(app_mark)

        title_col = QVBoxLayout()
        title_col.setSpacing(1)
        title = QLabel(self.i18n.t("app_title"), objectName="WindowTitle")
        subtitle = QLabel(self.i18n.t("app_subtitle"), objectName="WindowSubtitle")
        title_col.addWidget(title)
        title_col.addWidget(subtitle)
        topbar_layout.addLayout(title_col)
        topbar_layout.addStretch(1)

        self.header_status = QLabel(self.i18n.t("loading"), objectName="HeaderStatus")
        self.header_status.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        topbar_layout.addWidget(self.header_status)

        self.refresh_button = QPushButton(self.i18n.t("refresh"))
        self.refresh_button.clicked.connect(self.refresh_state)
        topbar_layout.addWidget(self.refresh_button)

        self.toggle_button = QPushButton(self.i18n.t("connect"), objectName="ToggleButton")
        self.toggle_button.setCheckable(True)
        self.toggle_button.clicked.connect(self.toggle_connection)
        topbar_layout.addWidget(self.toggle_button)
        outer.addWidget(topbar)

        splitter = QSplitter(Qt.Horizontal)
        splitter.setChildrenCollapsible(False)
        outer.addWidget(splitter, 1)

        left_panel = QWidget()
        left_col = QVBoxLayout(left_panel)
        left_col.setContentsMargins(0, 0, 0, 0)
        left_col.setSpacing(12)

        right_panel = QWidget()
        right_col = QVBoxLayout(right_panel)
        right_col.setContentsMargins(0, 0, 0, 0)
        right_col.setSpacing(12)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([460, 620])

        summary_box = QGroupBox(self.i18n.t("connection"))
        summary_layout = QVBoxLayout(summary_box)
        summary_layout.setSpacing(8)

        self.big_state = QLabel(self.i18n.t("disconnected"), objectName="BigState")
        summary_layout.addWidget(self.big_state)
        self.secondary_state = QLabel(self.i18n.t("loading"), objectName="Subline")
        self.secondary_state.setWordWrap(True)
        summary_layout.addWidget(self.secondary_state)

        chip_row = QHBoxLayout()
        chip_row.setSpacing(8)
        self.status_badge = QLabel(self.i18n.t("loading"), objectName="StatusBadge")
        self.status_badge.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        self.mode_badge = QLabel(self.i18n.t("mode_badge", mode="--"), objectName="StatusBadge")
        self.mode_badge.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
        chip_row.addWidget(self.status_badge)
        chip_row.addWidget(self.mode_badge)
        chip_row.addStretch(1)
        summary_layout.addLayout(chip_row)

        stats_grid = QGridLayout()
        stats_grid.setHorizontalSpacing(12)
        stats_grid.setVerticalSpacing(6)
        stats_grid.addWidget(self._static_label(self.i18n.t("summary_protocol")), 0, 0)
        self.summary_protocol = QLabel("--", objectName="DetailValue")
        stats_grid.addWidget(self.summary_protocol, 0, 1)
        stats_grid.addWidget(self._static_label(self.i18n.t("summary_service")), 1, 0)
        self.summary_service = QLabel("--", objectName="DetailValue")
        stats_grid.addWidget(self.summary_service, 1, 1)
        stats_grid.addWidget(self._static_label(self.i18n.t("summary_org")), 2, 0)
        self.summary_org = QLabel("--", objectName="DetailValue")
        stats_grid.addWidget(self.summary_org, 2, 1)
        summary_layout.addLayout(stats_grid)
        left_col.addWidget(summary_box)

        controls_box = QGroupBox(self.i18n.t("controls"))
        controls_layout = QFormLayout(controls_box)
        controls_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        controls_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        controls_layout.setFormAlignment(Qt.AlignTop)
        controls_layout.setHorizontalSpacing(12)
        controls_layout.setVerticalSpacing(8)

        self.mode_combo = QComboBox()
        for label, value in self._mode_options():
            self.mode_combo.addItem(label, value)
        self.mode_combo.currentIndexChanged.connect(self.change_mode)

        self.protocol_combo = QComboBox()
        for label, value in PROTOCOL_OPTIONS:
            self.protocol_combo.addItem(label, value)
        self.protocol_combo.currentIndexChanged.connect(self.change_protocol)

        self.protocol_hint = QLabel("--", objectName="Subline")
        self.protocol_hint.setWordWrap(True)

        self.disconnect_button = QPushButton(self.i18n.t("disconnect"))
        self.disconnect_button.clicked.connect(lambda: self.run_action(self.i18n.t("disconnecting"), self.cli.disconnect))
        self.reset_protocol_button = QPushButton(self.i18n.t("reset_protocol"))
        self.reset_protocol_button.clicked.connect(lambda: self.run_action(self.i18n.t("resetting_protocol"), self.cli.reset_protocol))
        self.registration_button = QPushButton(self.i18n.t("register_device"))
        self.registration_button.clicked.connect(lambda: self.run_action(self.i18n.t("registering_device"), self.cli.register))
        self.service_button = QPushButton(self.i18n.t("start_service"))
        self.service_button.clicked.connect(partial(self.run_service_action, "start"))
        self.service_restart_button = QPushButton(self.i18n.t("restart_service"))
        self.service_restart_button.clicked.connect(partial(self.run_service_action, "restart"))
        self.copy_diag_button = QPushButton(self.i18n.t("copy_diagnostics"))
        self.copy_diag_button.clicked.connect(self.copy_diagnostics)
        self.profile_combo = QComboBox()
        self.profile_apply_button = QPushButton(self.i18n.t("apply_profile"))
        self.profile_apply_button.clicked.connect(self.apply_selected_profile)
        self.profile_save_button = QPushButton(self.i18n.t("save_current_profile"))
        self.profile_save_button.clicked.connect(self.save_current_profile)
        self.profile_delete_button = QPushButton(self.i18n.t("delete_profile"), objectName="DangerButton")
        self.profile_delete_button.clicked.connect(self.delete_selected_profile)
        controls_layout.addRow(self.i18n.t("mode"), self.mode_combo)
        controls_layout.addRow(self.i18n.t("protocol"), self.protocol_combo)
        controls_layout.addRow("", self.protocol_hint)
        controls_layout.addRow(self.i18n.t("profile"), self.profile_combo)

        action_row_1 = QWidget()
        action_row_1_layout = QHBoxLayout(action_row_1)
        action_row_1_layout.setContentsMargins(0, 0, 0, 0)
        action_row_1_layout.setSpacing(8)
        action_row_1_layout.addWidget(self.profile_apply_button)
        action_row_1_layout.addWidget(self.profile_save_button)
        controls_layout.addRow(self.i18n.t("profiles"), action_row_1)

        action_row_2 = QWidget()
        action_row_2_layout = QHBoxLayout(action_row_2)
        action_row_2_layout.setContentsMargins(0, 0, 0, 0)
        action_row_2_layout.setSpacing(8)
        action_row_2_layout.addWidget(self.reset_protocol_button)
        controls_layout.addRow(self.i18n.t("session"), action_row_2)

        action_row_3 = QWidget()
        action_row_3_layout = QHBoxLayout(action_row_3)
        action_row_3_layout.setContentsMargins(0, 0, 0, 0)
        action_row_3_layout.setSpacing(8)
        action_row_3_layout.addWidget(self.service_restart_button)
        action_row_3_layout.addWidget(self.service_button)
        controls_layout.addRow(self.i18n.t("service"), action_row_3)

        controls_layout.addRow("", self.registration_button)
        controls_layout.addRow("", self.profile_delete_button)
        left_col.addWidget(controls_box)
        left_col.addStretch(1)

        tabs = QTabWidget()

        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.setContentsMargins(10, 10, 10, 10)
        overview_layout.setSpacing(12)

        details_box = QGroupBox(self.i18n.t("details"))
        details_form = QFormLayout(details_box)
        details_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        details_form.setHorizontalSpacing(14)
        details_form.setVerticalSpacing(10)

        self.detail_labels: dict[str, QLabel] = {}
        detail_keys = [
            ("status", self.i18n.t("status")),
            ("organization", self.i18n.t("organization")),
            ("account_type", self.i18n.t("account_type")),
            ("protocol", self.i18n.t("protocol")),
            ("service_mode", self.i18n.t("service_mode")),
            ("endpoint", self.i18n.t("endpoint")),
            ("device_name", self.i18n.t("device")),
        ]
        for key, label in detail_keys:
            value = QLabel("--", objectName="DetailValue")
            value.setWordWrap(True)
            details_form.addRow(label, value)
            self.detail_labels[key] = value

        status_row = QWidget()
        status_row_layout = QHBoxLayout(status_row)
        status_row_layout.setContentsMargins(0, 0, 0, 0)
        status_row_layout.setSpacing(8)
        self.detail_status_chip = QLabel("--", objectName="StatusBadge")
        self.detail_mode_chip = QLabel("--", objectName="StatusBadge")
        self.detail_protocol_chip = QLabel("--", objectName="StatusBadge")
        status_row_layout.addWidget(self.detail_status_chip)
        status_row_layout.addWidget(self.detail_mode_chip)
        status_row_layout.addWidget(self.detail_protocol_chip)
        status_row_layout.addStretch(1)
        overview_layout.addWidget(status_row)
        overview_layout.addWidget(details_box)

        runtime_box = QGroupBox(self.i18n.t("connection"))
        runtime_form = QFormLayout(runtime_box)
        runtime_form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        runtime_form.setHorizontalSpacing(14)
        runtime_form.setVerticalSpacing(10)
        self.runtime_labels: dict[str, QLabel] = {}
        runtime_keys = [
            ("mode", self.i18n.t("mode")),
            ("status", self.i18n.t("status")),
            ("protocol", self.i18n.t("protocol")),
            ("service", self.i18n.t("service")),
        ]
        for key, label in runtime_keys:
            value = QLabel("--", objectName="DetailValue")
            value.setWordWrap(True)
            runtime_form.addRow(label, value)
            self.runtime_labels[key] = value
        overview_layout.addWidget(runtime_box)
        overview_layout.addStretch(1)

        diagnostics_tab = QWidget()
        diagnostics_layout = QVBoxLayout(diagnostics_tab)
        diagnostics_layout.setContentsMargins(10, 10, 10, 10)
        diagnostics_layout.setSpacing(10)
        diag_toolbar = QHBoxLayout()
        diag_toolbar.addStretch(1)
        diag_toolbar.addWidget(self.copy_diag_button)
        diagnostics_layout.addLayout(diag_toolbar)
        self.log_view = QPlainTextEdit()
        self.log_view.setReadOnly(True)
        diagnostics_layout.addWidget(self.log_view, 1)

        tabs.addTab(overview_tab, self.i18n.t("overview"))
        tabs.addTab(diagnostics_tab, self.i18n.t("diagnostics"))
        right_col.addWidget(tabs, 1)
        self._refresh_profile_combo()

    def _build_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return

        self.tray_menu = QMenu()

        self.action_open = QAction(self.i18n.t("app_title"), self)
        self.action_open.triggered.connect(self.show_from_tray)
        self.action_connect = QAction(self.i18n.t("connect"), self)
        self.action_connect.triggered.connect(lambda: self.run_action(self.i18n.t("connecting"), self.cli.connect))
        self.action_disconnect = QAction(self.i18n.t("disconnect"), self)
        self.action_disconnect.triggered.connect(lambda: self.run_action(self.i18n.t("disconnecting"), self.cli.disconnect))
        self.action_refresh = QAction(self.i18n.t("refresh"), self)
        self.action_refresh.triggered.connect(self.refresh_state)
        self.action_start_service = QAction(self.i18n.t("start_service"), self)
        self.action_start_service.triggered.connect(partial(self.run_service_action, "start"))
        self.action_restart_service = QAction(self.i18n.t("restart_service"), self)
        self.action_restart_service.triggered.connect(partial(self.run_service_action, "restart"))
        self.action_quit = QAction(self.i18n.t("quit"), self)
        self.action_quit.triggered.connect(QApplication.instance().quit)

        for action in (
            self.action_open,
            self.action_connect,
            self.action_disconnect,
            self.action_refresh,
            self.action_start_service,
            self.action_restart_service,
            self.action_quit,
        ):
            self.tray_menu.addAction(action)

        self.tray_icon = QSystemTrayIcon(make_app_icon(), self)
        self.tray_icon.setContextMenu(self.tray_menu)
        self.tray_icon.activated.connect(self._on_tray_activated)
        self.tray_icon.show()

    def _on_tray_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.show_from_tray()

    def show_from_tray(self) -> None:
        self.show()
        self.raise_()
        self.activateWindow()

    def _static_label(self, text: str) -> QLabel:
        label = QLabel(text, objectName="DetailLabel")
        return label

    def _mode_options(self) -> list[tuple[str, str]]:
        return [
            (self.i18n.t("warp_dns"), "warp+doh"),
            (self.i18n.t("warp"), "warp"),
            (self.i18n.t("dns_https"), "doh"),
            (self.i18n.t("dns_tls"), "dot"),
            (self.i18n.t("tunnel_only"), "tunnel_only"),
            (self.i18n.t("local_proxy"), "proxy"),
        ]

    def _display_mode(self, mode: str) -> str:
        mapping = {
            "warp+doh": self.i18n.t("warp_dns"),
            "warp": self.i18n.t("warp"),
            "doh": self.i18n.t("dns_https"),
            "dot": self.i18n.t("dns_tls"),
            "tunnel_only": self.i18n.t("tunnel_only"),
            "proxy": self.i18n.t("local_proxy"),
        }
        return mapping.get(mode, mode)

    def copy_diagnostics(self) -> None:
        QApplication.clipboard().setText(self.log_view.toPlainText())
        self.header_status.setText(self.i18n.t("copied_diagnostics"))

    def apply_selected_profile(self) -> None:
        index = self.profile_combo.currentIndex()
        if index < 0 or index >= len(self.profiles):
            return
        profile = self.profiles[index]

        def apply_profile() -> str:
            messages: list[str] = []
            if profile.protocol != self.state.protocol:
                messages.append(self.cli.set_protocol(profile.protocol))
            if profile.mode != self.state.mode:
                messages.append(self.cli.set_mode(profile.mode))
            return "\n".join(filter(None, messages)) or self.i18n.t("profile_active")

        self.run_action(self.i18n.t("applying_profile", name=profile.name), apply_profile)

    def save_current_profile(self) -> None:
        default_name = f"{self.state.display_mode} / {self.state.protocol}"
        name, accepted = QInputDialog.getText(
            self,
            self.i18n.t("save_profile_title"),
            self.i18n.t("save_profile_prompt"),
            text=default_name,
        )
        if not accepted:
            return
        profile_name = name.strip()
        if not profile_name:
            return

        profile = WarpProfile(name=profile_name, mode=self.state.mode, protocol=self.state.protocol)
        for index, existing in enumerate(self.profiles):
            if existing.name == profile_name:
                self.profiles[index] = profile
                break
        else:
            self.profiles.append(profile)

        self.profile_store.save(self.profiles)
        self._refresh_profile_combo(profile_name)
        self.header_status.setText(self.i18n.t("saved_profile", name=profile_name))

    def delete_selected_profile(self) -> None:
        index = self.profile_combo.currentIndex()
        if index < 0 or index >= len(self.profiles):
            return
        profile = self.profiles[index]
        answer = QMessageBox.question(
            self,
            self.i18n.t("delete_profile_title"),
            self.i18n.t("delete_profile_prompt", name=profile.name),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return
        del self.profiles[index]
        self.profile_store.save(self.profiles)
        self._refresh_profile_combo()
        self.header_status.setText(self.i18n.t("deleted_profile", name=profile.name))

    def refresh_state(self) -> None:
        self.run_background(self.i18n.t("refreshing_state"), self.cli.snapshot, self._apply_state, deliver_state=True)

    def toggle_connection(self, checked: bool) -> None:
        if checked:
            self.run_action(self.i18n.t("connecting"), self.cli.connect)
        else:
            self.run_action(self.i18n.t("disconnecting"), self.cli.disconnect)

    def change_mode(self) -> None:
        if not self.mode_combo.isEnabled():
            return
        mode = self.mode_combo.currentData()
        if mode and mode != self.state.mode:
            self.run_action(self.i18n.t("switching_mode", mode=mode), partial(self.cli.set_mode, mode))

    def change_protocol(self) -> None:
        if not self.protocol_combo.isEnabled():
            return
        protocol = self.protocol_combo.currentData()
        if protocol and protocol != self.state.protocol:
            self.run_action(self.i18n.t("switching_protocol", protocol=protocol), partial(self.cli.set_protocol, protocol))

    def run_service_action(self, action: str) -> None:
        def launch() -> str:
            self.cli.launch_privileged_service(action)
            return self.i18n.t("service_action_done", action=action)

        self.run_action(self.i18n.t("service_action", action=action), launch)

    def run_action(self, pending_message: str, callback: Callable[[], object]) -> None:
        self.status_badge.setText(pending_message)
        self.header_status.setText(pending_message)
        self.run_background(pending_message, callback, lambda _result: self.refresh_state())

    def run_background(
        self,
        label: str,
        callback: Callable[[], object],
        on_success: Callable[[object], None] | None = None,
        *,
        deliver_state: bool = False,
    ) -> None:
        self.current_jobs += 1
        self.bridge.busy_changed.emit(True)
        future = self.executor.submit(callback)

        def done(fut) -> None:
            self.current_jobs = max(0, self.current_jobs - 1)
            try:
                result = fut.result()
            except Exception as exc:
                self.bridge.action_failed.emit(label, str(exc))
                self.bridge.busy_changed.emit(self.current_jobs > 0)
                return

            if on_success is not None:
                if deliver_state:
                    self.bridge.state_ready.emit(result)
                else:
                    QTimer.singleShot(0, lambda r=result: on_success(r))
            self.bridge.busy_changed.emit(self.current_jobs > 0)

        future.add_done_callback(done)

    def _set_busy(self, busy: bool) -> None:
        for widget in (
            self.toggle_button,
            self.mode_combo,
            self.protocol_combo,
            self.registration_button,
            self.service_button,
            self.refresh_button,
            self.reset_protocol_button,
            self.service_restart_button,
            self.copy_diag_button,
            self.profile_combo,
            self.profile_apply_button,
            self.profile_save_button,
            self.profile_delete_button,
        ):
            widget.setEnabled(not busy)

    def _handle_error(self, label: str, message: str) -> None:
        self.status_badge.setText(self.i18n.t("action_failed"))
        self.header_status.setText(self.i18n.t("action_failed"))
        self.log_view.appendPlainText(f"{label}: {message}")
        QMessageBox.warning(self, self.i18n.t("warning_title"), self.i18n.t("action_failed_message", label=label, message=message))

    def _apply_state(self, state: WarpState) -> None:
        self.state = state
        self.setWindowIcon(make_app_icon(connected=state.connected, warning=bool(state.error)))
        if self.tray_icon is not None:
            self.tray_icon.setIcon(make_app_icon(connected=state.connected, warning=bool(state.error)))

        self.toggle_button.blockSignals(True)
        self.mode_combo.blockSignals(True)
        self.protocol_combo.blockSignals(True)

        self.toggle_button.setChecked(state.connected)
        self.toggle_button.setText(self.i18n.t("disconnect") if state.connected else self.i18n.t("connect"))

        translated_status = self._translate_runtime_value(state.status_line)
        translated_org = self._translate_runtime_value(state.organization)
        translated_account = self._translate_runtime_value(state.account_type)
        translated_service_mode = self._translate_runtime_value(state.service_mode)

        self.status_badge.setText(translated_status)
        self.header_status.setText(translated_status)
        self.mode_badge.setText(self.i18n.t("mode_badge", mode=self._display_mode(state.mode)))
        if not state.daemon_reachable:
            self.big_state.setText(self.i18n.t("service_offline_title"))
            self.secondary_state.setText(self.i18n.t("service_not_running"))
        elif state.connected:
            self.big_state.setText(self.i18n.t("protected"))
            self.secondary_state.setText(self.i18n.t("tunnel_active"))
        else:
            self.big_state.setText(self.i18n.t("disconnected"))
            self.secondary_state.setText(self.i18n.t("client_reachable"))

        self.registration_button.setVisible(not state.registered and state.daemon_reachable)
        self.service_button.setVisible(not state.daemon_reachable)
        self.service_restart_button.setVisible(state.daemon_reachable)
        self.service_button.setText(self.i18n.t("start_service"))

        self._select_combo_value(self.mode_combo, state.mode)
        self._select_combo_value(self.protocol_combo, state.protocol)

        self.summary_protocol.setText(state.protocol)
        self.summary_service.setText(self.i18n.t("service_online") if state.daemon_reachable else self.i18n.t("service_offline"))
        self.summary_org.setText(translated_org)
        self.protocol_hint.setText(
            self.i18n.t("masque_desc") if state.protocol == "MASQUE" else self.i18n.t("wireguard_desc")
        )

        self.detail_labels["status"].setText(translated_status)
        self.detail_labels["organization"].setText(translated_org)
        self.detail_labels["account_type"].setText(translated_account)
        self.detail_labels["protocol"].setText(state.protocol)
        self.detail_labels["service_mode"].setText(translated_service_mode)
        self.detail_labels["endpoint"].setText(state.endpoint or "--")
        self.detail_labels["device_name"].setText(state.device_name or "--")
        self.detail_status_chip.setText(translated_status)
        self.detail_mode_chip.setText(self._display_mode(state.mode))
        self.detail_protocol_chip.setText(state.protocol)
        self.runtime_labels["mode"].setText(self._display_mode(state.mode))
        self.runtime_labels["status"].setText(translated_status)
        self.runtime_labels["protocol"].setText(state.protocol)
        self.runtime_labels["service"].setText(self.i18n.t("service_online") if state.daemon_reachable else self.i18n.t("service_offline"))
        self._sync_profile_selection()

        diagnostic_lines = []
        if state.raw_status:
            diagnostic_lines.append(self.i18n.t("status_snapshot"))
            diagnostic_lines.append(state.raw_status)
        if state.diagnostics:
            diagnostic_lines.append("")
            diagnostic_lines.append(self.i18n.t("extra_diagnostics"))
            diagnostic_lines.extend(state.diagnostics)
        if state.error and not state.raw_status:
            diagnostic_lines.append(state.error)
        self.log_view.setPlainText("\n".join(diagnostic_lines).strip())

        if self.tray_icon is not None:
            self.action_connect.setEnabled(state.daemon_reachable and not state.connected)
            self.action_disconnect.setEnabled(state.daemon_reachable and state.connected)
            self.action_start_service.setEnabled(not state.daemon_reachable)
            self.action_restart_service.setEnabled(state.cli_available)

        self.toggle_button.blockSignals(False)
        self.mode_combo.blockSignals(False)
        self.protocol_combo.blockSignals(False)

    @staticmethod
    def _select_combo_value(combo: QComboBox, value: str) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _refresh_profile_combo(self, selected_name: str | None = None) -> None:
        self.profile_combo.blockSignals(True)
        self.profile_combo.clear()
        for profile in self.profiles:
            self.profile_combo.addItem(f"{profile.name} ({self._display_mode(profile.mode)} / {profile.protocol})", profile.name)
        self.profile_combo.blockSignals(False)
        if selected_name:
            index = self.profile_combo.findData(selected_name)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
                return
        self._sync_profile_selection()

    def _sync_profile_selection(self) -> None:
        for index, profile in enumerate(self.profiles):
            if profile.mode == self.state.mode and profile.protocol == self.state.protocol:
                self.profile_combo.setCurrentIndex(index)
                return

    def _translate_runtime_value(self, value: str) -> str:
        mapping = {
            "Unknown": self.i18n.t("unknown"),
            "Personal": self.i18n.t("personal"),
            "Free": self.i18n.t("free"),
            "Connected": self.i18n.t("connected"),
            "Disconnected": self.i18n.t("disconnected"),
        }
        return mapping.get(value, value)
