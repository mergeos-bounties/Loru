"""Loru modern Qt desktop demo — sign → text → voice."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import Qt, QSize, QThread, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QStatusBar,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from loru import __version__
from loru.config import OUT_DIR, SAMPLES_DIR
from loru.data.loader import list_sample_files, sequence_summary
from loru.gui.styles import STYLESHEET
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS
from loru.train.toy_train import train_toy


def _card() -> QFrame:
    f = QFrame()
    f.setObjectName("card")
    return f


def _primary(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0,y1:0,x2:1,y2:0,"
        " stop:0 #8b5cf6, stop:1 #7c3aed); color: white; border: none;"
        " border-radius: 10px; padding: 10px 18px; font-weight: 700; }"
        "QPushButton:hover { background: #a78bfa; color: #1e1b4b; }"
        "QPushButton:disabled { background: #334155; color: #94a3b8; }"
    )
    return b


def _ghost(text: str) -> QPushButton:
    b = QPushButton(text)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    b.setCheckable(True)
    b.setStyleSheet(
        "QPushButton { text-align: left; background: transparent; border: none;"
        " border-radius: 10px; padding: 12px 14px; color: #94a3b8; font-weight: 600; }"
        "QPushButton:hover { background: #1e293b; color: #e2e8f0; }"
        "QPushButton:checked { background: #5b21b6; color: #f5f3ff; }"
    )
    return b


class TrainWorker(QThread):
    finished_ok = Signal(dict)
    failed = Signal(str)

    def __init__(self, epochs: int = 2) -> None:
        super().__init__()
        self.epochs = epochs

    def run(self) -> None:
        try:
            report = train_toy(epochs=self.epochs)
            self.finished_ok.emit(report)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(f"Loru · Sign → Text → Voice · v{__version__}")
        self.resize(1120, 720)
        self.setMinimumSize(QSize(920, 580))
        self.setStyleSheet(STYLESHEET)
        self._worker: TrainWorker | None = None

        central = QWidget()
        central.setObjectName("central")
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(210)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(14, 18, 14, 14)
        brand = QLabel("🤟 Loru")
        brand.setObjectName("brand")
        sl.addWidget(brand)
        sub = QLabel("Sign language demo")
        sub.setObjectName("brandSub")
        sl.addWidget(sub)

        self._nav: list[QPushButton] = []
        self._keys = ["demo", "samples", "infer", "train", "vocab"]
        labels = {
            "demo": "▶  Full demo",
            "samples": "📁  Samples",
            "infer": "🔤  Infer",
            "train": "🧠  Train",
            "vocab": "📖  Gloss vocab",
        }
        for k in self._keys:
            b = _ghost(labels[k])
            b.clicked.connect(lambda _=False, key=k: self._goto(key))
            self._nav.append(b)
            sl.addWidget(b)
        sl.addStretch(1)
        sl.addWidget(QLabel(f"v{__version__} · offline"))
        root.addWidget(side)

        self.stack = QStackedWidget()
        root.addWidget(self.stack, 1)

        self.pages = {
            "demo": self._page_demo(),
            "samples": self._page_samples(),
            "infer": self._page_infer(),
            "train": self._page_train(),
            "vocab": self._page_vocab(),
        }
        for w in self.pages.values():
            self.stack.addWidget(w)

        self.setStatusBar(QStatusBar())
        self._status("Ready · offline sign→text→voice")
        self._goto("demo")
        self.refresh_samples()

    def _status(self, msg: str) -> None:
        self.statusBar().showMessage(msg)

    def _goto(self, key: str) -> None:
        idx = self._keys.index(key)
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self._nav):
            b.setChecked(i == idx)

    # ----- Demo -----
    def _page_demo(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(14)
        t = QLabel("Full offline demo")
        t.setObjectName("h1")
        lay.addWidget(t)
        s = QLabel("Train toy model → infer sign-to-text → export WAV voice.")
        s.setObjectName("h2")
        lay.addWidget(s)

        card = _card()
        cl = QVBoxLayout(card)
        cl.setContentsMargins(18, 18, 18, 18)
        self.demo_progress = QProgressBar()
        self.demo_progress.setRange(0, 0)
        self.demo_progress.setVisible(False)
        cl.addWidget(self.demo_progress)
        self.demo_log = QTextEdit()
        self.demo_log.setReadOnly(True)
        self.demo_log.setMinimumHeight(280)
        self.demo_log.setPlaceholderText("Click Run demo to start…")
        cl.addWidget(self.demo_log)
        lay.addWidget(card, 1)

        row = QHBoxLayout()
        btn = _primary("Run full demo")
        btn.clicked.connect(self.run_full_demo)
        row.addWidget(btn)
        row.addStretch(1)
        lay.addLayout(row)
        return page

    def run_full_demo(self) -> None:
        self.demo_progress.setVisible(True)
        self.demo_log.clear()
        self._append_demo("Starting offline demo…")
        files = list_sample_files()
        self._append_demo(f"Samples: {len(files)} in {SAMPLES_DIR}")
        try:
            report = train_toy(epochs=2)
            acc = report["history"][-1]["accuracy"]
            self._append_demo(f"Train accuracy: {acc}")
            hello = SAMPLES_DIR / "hello.json"
            if not hello.exists() and files:
                hello = files[0]
            text = sign_to_text(hello)
            self._append_demo("Sign → text:")
            self._append_demo(json.dumps(text, indent=2, ensure_ascii=False))
            wav = OUT_DIR / "demo_hello.wav"
            voice = sign_to_voice(hello, wav)
            self._append_demo(f"Voice: {voice.get('audio_path')}")
            self._append_demo("Demo complete — offline sign→text→voice works.")
            self._status("Demo complete")
            self.refresh_samples()
        except Exception as exc:  # noqa: BLE001
            self._append_demo(f"Error: {exc}")
            QMessageBox.warning(self, "Loru", str(exc))
        finally:
            self.demo_progress.setVisible(False)

    def _append_demo(self, line: str) -> None:
        self.demo_log.append(line)

    # ----- Samples -----
    def _page_samples(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        t = QLabel("Landmark samples")
        t.setObjectName("h1")
        lay.addWidget(t)
        s = QLabel(f"Directory: {SAMPLES_DIR}")
        s.setObjectName("h2")
        lay.addWidget(s)
        self.samples_table = QTableWidget(0, 3)
        self.samples_table.setHorizontalHeaderLabels(["File", "Gloss", "Frames"])
        self.samples_table.horizontalHeader().setStretchLastSection(True)
        self.samples_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.samples_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        lay.addWidget(self.samples_table, 1)
        btn = _ghost("Refresh")
        btn.setCheckable(False)
        btn.clicked.connect(self.refresh_samples)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        return page

    def refresh_samples(self) -> None:
        files = list_sample_files()
        self.samples_table.setRowCount(len(files))
        for r, path in enumerate(files):
            summary = sequence_summary(path)
            for c, val in enumerate(
                [path.name, str(summary.get("gloss", "")), str(summary.get("frames", ""))]
            ):
                self.samples_table.setItem(r, c, QTableWidgetItem(val))
        self.samples_table.resizeColumnsToContents()
        # sync infer combo
        if hasattr(self, "infer_combo"):
            cur = self.infer_combo.currentText()
            self.infer_combo.clear()
            for path in files:
                self.infer_combo.addItem(path.name, str(path))
            if cur:
                i = self.infer_combo.findText(cur)
                if i >= 0:
                    self.infer_combo.setCurrentIndex(i)

    # ----- Infer -----
    def _page_infer(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        t = QLabel("Inference")
        t.setObjectName("h1")
        lay.addWidget(t)

        card = _card()
        fl = QFormLayout(card)
        fl.setContentsMargins(18, 18, 18, 18)
        self.infer_combo = QComboBox()
        self.infer_mode = QComboBox()
        self.infer_mode.addItems(["sign → text", "sign → voice", "gloss → sentence"])
        self.gloss_edit = QComboBox()
        self.gloss_edit.setEditable(True)
        self.gloss_edit.addItems(list(DEFAULT_GLOSS))
        fl.addRow("Sample", self.infer_combo)
        fl.addRow("Mode", self.infer_mode)
        fl.addRow("Gloss (sentence)", self.gloss_edit)
        lay.addWidget(card)

        row = QHBoxLayout()
        btn = _primary("Run inference")
        btn.clicked.connect(self.run_infer)
        row.addWidget(btn)
        row.addStretch(1)
        lay.addLayout(row)

        self.infer_out = QTextEdit()
        self.infer_out.setReadOnly(True)
        lay.addWidget(self.infer_out, 1)
        return page

    def run_infer(self) -> None:
        mode = self.infer_mode.currentText()
        try:
            if mode == "gloss → sentence":
                g = self.gloss_edit.currentText().strip() or "hello"
                text = gloss_to_sentence(g)
                multi = multi_gloss_to_sentence([g])
                self.infer_out.setPlainText(
                    json.dumps({"gloss": g, "text": text, "multi": multi}, indent=2, ensure_ascii=False)
                )
                self._status(f"Gloss → {text}")
                return
            path_s = self.infer_combo.currentData()
            if not path_s:
                QMessageBox.information(self, "Loru", "No sample selected.")
                return
            path = Path(path_s)
            if mode == "sign → text":
                r = sign_to_text(path)
                self.infer_out.setPlainText(json.dumps(r, indent=2, ensure_ascii=False))
                self._status(f"Predicted: {r.get('predicted_gloss')}")
            else:
                out = OUT_DIR / f"{path.stem}.wav"
                r = sign_to_voice(path, out)
                self.infer_out.setPlainText(json.dumps(r, indent=2, ensure_ascii=False))
                self._status(f"Voice: {r.get('audio_path')}")
        except Exception as exc:  # noqa: BLE001
            self.infer_out.setPlainText(f"Error: {exc}")

    # ----- Train -----
    def _page_train(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        t = QLabel("Toy train")
        t.setObjectName("h1")
        lay.addWidget(t)
        card = _card()
        fl = QFormLayout(card)
        fl.setContentsMargins(18, 18, 18, 18)
        self.epochs = QSpinBox()
        self.epochs.setRange(1, 20)
        self.epochs.setValue(2)
        fl.addRow("Epochs", self.epochs)
        lay.addWidget(card)
        self.train_bar = QProgressBar()
        self.train_bar.setRange(0, 0)
        self.train_bar.setVisible(False)
        lay.addWidget(self.train_bar)
        btn = _primary("Start training")
        btn.clicked.connect(self.run_train)
        lay.addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.train_out = QTextEdit()
        self.train_out.setReadOnly(True)
        lay.addWidget(self.train_out, 1)
        return page

    def run_train(self) -> None:
        if self._worker and self._worker.isRunning():
            return
        self.train_bar.setVisible(True)
        self.train_out.append(f"Training epochs={self.epochs.value()}…")
        self._worker = TrainWorker(self.epochs.value())
        self._worker.finished_ok.connect(self._train_ok)
        self._worker.failed.connect(self._train_fail)
        self._worker.start()

    def _train_ok(self, report: dict) -> None:
        self.train_bar.setVisible(False)
        self.train_out.append(json.dumps(report, indent=2, default=str)[:4000])
        acc = report.get("history", [{}])[-1].get("accuracy")
        self._status(f"Train done · accuracy={acc}")

    def _train_fail(self, msg: str) -> None:
        self.train_bar.setVisible(False)
        self.train_out.append(f"Error: {msg}")

    # ----- Vocab -----
    def _page_vocab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        t = QLabel("Default gloss vocabulary")
        t.setObjectName("h1")
        lay.addWidget(t)
        s = QLabel(f"{len(DEFAULT_GLOSS)} demo glosses")
        s.setObjectName("h2")
        lay.addWidget(s)
        lst = QListWidget()
        for g in DEFAULT_GLOSS:
            lst.addItem(QListWidgetItem(g))
        lay.addWidget(lst, 1)
        return page
