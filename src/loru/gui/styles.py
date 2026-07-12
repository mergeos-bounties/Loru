"""Modern dark theme for Loru Qt desktop."""

STYLESHEET = """
* {
  font-family: "Segoe UI", "Inter", sans-serif;
  font-size: 13px;
  color: #e2e8f0;
}
QMainWindow, QWidget#central {
  background: #0b1020;
}
QFrame#sidebar {
  background: #0a0f1a;
  border-right: 1px solid #1e293b;
}
QLabel#brand {
  font-size: 20px;
  font-weight: 800;
  color: #a78bfa;
  padding: 6px 4px 0 4px;
}
QLabel#brandSub {
  color: #64748b;
  font-size: 11px;
  padding: 0 4px 12px 4px;
}
QLabel#h1 {
  font-size: 22px;
  font-weight: 700;
  color: #f8fafc;
}
QLabel#h2 {
  color: #94a3b8;
  font-size: 13px;
}
QFrame#card {
  background: #111827;
  border: 1px solid #1f2937;
  border-radius: 14px;
}
QLineEdit, QComboBox, QSpinBox, QTextEdit, QPlainTextEdit, QListWidget {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 8px 12px;
  selection-background-color: #7c3aed;
}
QListWidget::item {
  padding: 10px;
  border-radius: 8px;
}
QListWidget::item:selected {
  background: #4c1d95;
  color: #f5f3ff;
}
QTableWidget {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 12px;
  gridline-color: #1e293b;
  selection-background-color: #5b21b6;
}
QHeaderView::section {
  background: #111827;
  color: #94a3b8;
  padding: 8px;
  border: none;
  border-bottom: 1px solid #1e293b;
  font-weight: 600;
}
QStatusBar {
  background: #0a0f1a;
  color: #64748b;
  border-top: 1px solid #1e293b;
}
QProgressBar {
  background: #1e293b;
  border: none;
  border-radius: 6px;
  text-align: center;
  color: #e2e8f0;
  height: 14px;
}
QProgressBar::chunk {
  background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #8b5cf6, stop:1 #a78bfa);
  border-radius: 6px;
}
"""
