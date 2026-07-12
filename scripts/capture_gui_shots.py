"""Capture Loru Qt GUI screenshots into docs/screenshots/."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
OUT = ROOT / "docs" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)


def main() -> None:
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication

    from loru.gui.main_window import MainWindow

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.processEvents()

    # seed demo log without long wait on first shot
    shots = [
        ("gui-demo.png", "demo", True),
        ("gui-samples.png", "samples", False),
        ("gui-infer.png", "infer", True),
        ("gui-train.png", "train", False),
        ("gui-vocab.png", "vocab", False),
    ]

    def grab(i: int = 0) -> None:
        if i >= len(shots):
            app.quit()
            return
        name, page, act = shots[i]
        win._goto(page)
        app.processEvents()
        if act and page == "demo":
            win.run_full_demo()
            app.processEvents()
        if act and page == "infer":
            win.infer_mode.setCurrentText("sign → text")
            if win.infer_combo.count():
                win.run_infer()
            app.processEvents()
        path = OUT / name
        win.grab().save(str(path), "PNG")
        print("wrote", path, path.stat().st_size)
        QTimer.singleShot(200, lambda: grab(i + 1))

    QTimer.singleShot(350, grab)
    app.exec()


if __name__ == "__main__":
    main()
