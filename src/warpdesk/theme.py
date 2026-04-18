WINDOW_STYLESHEET = """
QWidget {
  font-family: "Noto Sans", "Inter", "Cantarell", sans-serif;
  font-size: 13px;
}

QMainWindow, QWidget {
  background: palette(window);
  color: palette(window-text);
}

QFrame#TopBar {
  background: palette(base);
  border: 1px solid palette(midlight);
  border-radius: 10px;
}

QLabel#AppMark {
  background: transparent;
}

QLabel#WindowTitle {
  font-size: 15px;
  font-weight: 700;
}

QLabel#WindowSubtitle {
  color: palette(mid);
  font-size: 12px;
}

QLabel#HeaderStatus,
QLabel#StatusBadge {
  background: palette(button);
  border: 1px solid palette(midlight);
  border-radius: 8px;
  padding: 4px 8px;
  font-weight: 600;
}

QLabel#BigState {
  font-size: 24px;
  font-weight: 700;
}

QLabel#Subline,
QLabel#DetailLabel {
  color: palette(mid);
}

QLabel#DetailLabel {
  font-weight: 600;
}

QLabel#DetailValue {
  font-weight: 600;
}

QGroupBox {
  background: palette(base);
  border: 1px solid palette(midlight);
  border-radius: 10px;
  margin-top: 8px;
  padding: 14px;
  font-weight: 700;
}

QGroupBox::title {
  subcontrol-origin: margin;
  left: 10px;
  padding: 0 4px;
}

QPushButton,
QComboBox,
QTabBar::tab {
  min-height: 28px;
}

QPushButton#ToggleButton {
  min-width: 120px;
  font-weight: 700;
}

QPushButton#DangerButton {
  color: #c23b3b;
}

QTabWidget::pane {
  border: 1px solid palette(midlight);
  border-radius: 10px;
  top: -1px;
  background: palette(base);
}

QTabBar::tab {
  background: transparent;
  border: none;
  padding: 6px 10px;
  margin-right: 4px;
}

QTabBar::tab:selected {
  background: palette(button);
  border: 1px solid palette(midlight);
  border-radius: 8px;
}

QPlainTextEdit {
  background: palette(base);
  border: 1px solid palette(midlight);
  border-radius: 8px;
  padding: 6px;
  font-family: "JetBrains Mono", "Cascadia Code", monospace;
  font-size: 12px;
}

QFormLayout QLabel {
  min-height: 22px;
}

QSplitter::handle {
  background: transparent;
}
"""
