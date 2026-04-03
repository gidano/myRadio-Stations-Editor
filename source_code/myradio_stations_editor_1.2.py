import os
import sys
import requests
import csv
import re
from datetime import datetime

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QLabel, QLineEdit, QComboBox, QHeaderView,
    QSpacerItem,
    QAbstractItemView, QSizePolicy, QStatusBar, QProgressBar
)
from PySide6.QtCore import Qt, QObject, QThread, Signal
from PySide6.QtGui import QColor, QIcon, QKeySequence, QShortcut, QPixmap


APP_VERSION = "v1.2"
APP_FOOTER = f"myRadio Stations Editor {APP_VERSION} by gidano"
SOFT_STATION_LIMIT = 300


def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)


TEXTS = {
    "en": {
        "title": "myRadio Stations Editor",
        "ip": "IP",
        "read": "Read from radio",
        "write": "Write to radio",
        "open": "Open list",
        "save": "Save list",
        "merge": "Merge list",
        "clear": "Clear list",
        "add": "Add",
        "delete": "Delete",
        "clone": "Clone",
        "undo": "Undo",
        "redo": "Redo",
        "check": "Check",
        "dedupe": "Remove duplicates",
        "uppercase": "UPPERCASE",
        "titlecase": "Title Case",
        "search": "Search",
        "search_placeholder": "Search station name or URL...",
        "filter": "Filter",
        "filter_all": "All",
        "filter_invalid": "Invalid only",
        "filter_duplicates": "Duplicates only",
        "filter_unreachable": "Unreachable only",
        "name": "Station Name",
        "url": "URL",
        "volume": "Vol",
        "status": "Status",
        "upload_ok": "Upload successful.\nPlease restart the radio to apply changes.",
        "open_title": "Open stations list",
        "save_title": "Save stations list",
        "merge_title": "Merge stations list",
        "error": "Error",
        "ok": "OK",
        "confirm_clear_title": "Clear list",
        "confirm_clear_text": "Do you really want to clear the current list?",
        "total": "Total",
        "duplicates": "Duplicates",
        "invalid": "Invalid",
        "soft_limit": "Over limit",
        "status_ok": "OK",
        "status_invalid_url": "Invalid URL",
        "status_unreachable": "Unreachable stream",
        "status_empty_name": "Empty name",
        "status_empty_url": "Empty URL",
        "status_duplicate_of": "Duplicate of #{row}",
        "status_duplicate_group": "Duplicate group",
        "status_multiple": "Multiple issues",
        "read_fail": "Could not read station list from radio:\n{err}",
        "write_fail": "Could not upload station list to radio:\n{err}",
        "open_fail": "Could not open file:\n{err}",
        "save_fail": "Could not save file:\n{err}",
        "merge_fail": "Could not merge file:\n{err}",
        "check_done": "Validation finished.",
        "unsaved_title": "Unsaved changes",
        "unsaved_text": "You have unsaved changes. Do you really want to exit?",
        "status_copied": "Row copied.",
        "status_pasted": "Row pasted.",
        "status_nothing_to_paste": "Nothing to paste.",
        "affected_rows": "Affected rows: {rows}",
        "yes": "Yes",
        "no": "No",
        "progress_idle": "Ready.",
        "progress_check": "Checking {current}/{total}: {name}",
        "progress_done": "Done. Checked: {total}",
        "progress_add": "Added row #{row}",
        "progress_prepare": "Preparing live validation...",
        "progress_error": "Validation error: {err}",
        "check_running_title": "Validation in progress",
        "check_running_text": "The live validation is already running.",
        "cancel": "Cancel",
        "cancelled": "Cancelled.",
        "check_cancelled": "Validation cancelled.",
        "backup_created": "Backup created: {name}",
        "backup_fail": "Could not create backup:\n{err}",
        "undo_done": "Undo completed.",
        "redo_done": "Redo completed.",
        "radio_type": "Radio",
        "radio_auto": "Auto",
        "radio_myradio": "myRadio",
        "radio_yoradio": "ëRadio",
        "detected_radio": "Detected: {name}",
        "using_radio": "Using: {name}",
        "read_try_myradio": "Trying myRadio...",
        "read_try_yoradio": "Trying ëRadio...",
        "write_try_myradio": "Uploading to myRadio...",
        "write_try_yoradio": "Uploading to ëRadio...",
        "upload_ok_yoradio": "Upload successful. The ëRadio playlist has been updated.",
        "read_fail_combined": "Could not read station list from radio.\nmyRadio error: {myerr}\nYoRadio error: {yoerr}"
    },
    "hu": {
        "title": "myRadio Stations Editor",
        "ip": "IP",
        "read": "Beolvasás rádióból",
        "write": "Feltöltés rádióra",
        "open": "Lista megnyitása",
        "save": "Lista mentése",
        "merge": "Lista hozzáfűzése",
        "clear": "Lista törlése",
        "add": "Hozzáadás",
        "delete": "Törlés",
        "clone": "Klónozás",
        "undo": "Visszavonás",
        "redo": "Újra",
        "check": "Ellenőrzés",
        "dedupe": "Duplikátumok eltávolítása",
        "uppercase": "NAGYBETŰS",
        "titlecase": "Kezdőbetűs",
        "search": "Keresés",
        "search_placeholder": "Keresés állomásnévre vagy linkre...",
        "filter": "Szűrő",
        "filter_all": "Összes",
        "filter_invalid": "Csak hibás",
        "filter_duplicates": "Csak duplikátum",
        "filter_unreachable": "Csak nem elérhető",
        "name": "Állomás",
        "url": "Link",
        "volume": "Hangerő",
        "status": "Státusz",
        "upload_ok": "Feltöltés sikeres.\nA módosításokhoz indítsd újra a rádiót.",
        "open_title": "Állomáslista megnyitása",
        "save_title": "Állomáslista mentése",
        "merge_title": "Állomáslista hozzáfűzése",
        "error": "Hiba",
        "ok": "OK",
        "confirm_clear_title": "Lista törlése",
        "confirm_clear_text": "Biztosan törlöd a jelenlegi listát?",
        "total": "Összesen",
        "duplicates": "Duplikátum",
        "invalid": "Hibás",
        "soft_limit": "Limit felett",
        "status_ok": "OK",
        "status_invalid_url": "Hibás URL",
        "status_unreachable": "Nem elérhető stream",
        "status_empty_name": "Üres név",
        "status_empty_url": "Üres URL",
        "status_duplicate_of": "A(z) #{row}. sor duplikátuma",
        "status_duplicate_group": "Duplikátum csoport",
        "status_multiple": "Több probléma",
        "read_fail": "Nem sikerült beolvasni az állomáslistát a rádióról:\n{err}",
        "write_fail": "Nem sikerült feltölteni az állomáslistát a rádióra:\n{err}",
        "open_fail": "Nem sikerült megnyitni a fájlt:\n{err}",
        "save_fail": "Nem sikerült menteni a fájlt:\n{err}",
        "merge_fail": "Nem sikerült hozzáfűzni a fájlt:\n{err}",
        "check_done": "Ellenőrzés kész.",
        "unsaved_title": "Nem mentett módosítások",
        "unsaved_text": "Nem mentett módosításaid vannak. Biztosan ki szeretnél lépni?",
        "status_copied": "Sor másolva.",
        "status_pasted": "Sor beillesztve.",
        "status_nothing_to_paste": "Nincs mit beilleszteni.",
        "affected_rows": "Érintett sorok: {rows}",
        "yes": "Igen",
        "no": "Nem",
        "progress_idle": "Kész.",
        "progress_check": "Ellenőrzés {current}/{total}: {name}",
        "progress_done": "Kész. Sorok: {total}",
        "progress_add": "Hozzáadva #{row}",
        "progress_prepare": "Élő ellenőrzés előkészítése...",
        "progress_error": "Ellenőrzési hiba: {err}",
        "check_running_title": "Ellenőrzés folyamatban",
        "check_running_text": "Az élő ellenőrzés már fut.",
        "cancel": "Mégse",
        "cancelled": "Megszakítva.",
        "check_cancelled": "Ellenőrzés megszakítva.",
        "backup_created": "Backup készült: {name}",
        "backup_fail": "Nem sikerült backupot készíteni:\n{err}",
        "undo_done": "Visszavonás kész.",
        "redo_done": "Újra végrehajtás kész.",
        "radio_type": "Rádió",
        "radio_auto": "Auto",
        "radio_myradio": "myRadio",
        "radio_yoradio": "ëRadio",
        "detected_radio": "Felismerve: {name}",
        "using_radio": "Használatban: {name}",
        "read_try_myradio": "myRadio próbálása...",
        "read_try_yoradio": "ëRadio próbálása...",
        "write_try_myradio": "Feltöltés myRadio-ra...",
        "write_try_yoradio": "Feltöltés ëRadio-ra...",
        "upload_ok_yoradio": "Feltöltés sikeres. A ëRadio lejátszási lista frissült.",
        "read_fail_combined": "Nem sikerült beolvasni az állomáslistát a rádióról.\nmyRadio hiba: {myerr}\nYoRadio hiba: {yoerr}"
    }
}


def confirm_dialog(parent, title, text, yes_text, no_text):
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle(title)
    msg.setText(text)

    yes_button = msg.addButton(yes_text, QMessageBox.YesRole)
    no_button = msg.addButton(no_text, QMessageBox.NoRole)

    msg.setDefaultButton(no_button)
    msg.exec()

    return msg.clickedButton() == yes_button


class StationsTable(QTableWidget):
    def __init__(self, editor, rows=0, columns=0):
        super().__init__(rows, columns)
        self.editor = editor
        self._drag_row = -1

    def mousePressEvent(self, event):
        try:
            pos = event.position().toPoint()
        except AttributeError:
            pos = event.pos()
        index = self.indexAt(pos)
        self._drag_row = index.row() if index.isValid() else -1
        super().mousePressEvent(event)

    def dropEvent(self, event):
        source = event.source()
        if source is not self:
            super().dropEvent(event)
            return

        source_row = self._drag_row if self._drag_row >= 0 else self.currentRow()
        if source_row < 0:
            event.ignore()
            return

        try:
            pos = event.position().toPoint()
        except AttributeError:
            pos = event.pos()

        index = self.indexAt(pos)
        if index.isValid():
            target_row = index.row()
            if self.dropIndicatorPosition() == QAbstractItemView.BelowItem:
                target_row += 1
        else:
            target_row = self.rowCount()

        if target_row > source_row:
            target_row -= 1

        self.editor.move_row_data(source_row, target_row)
        self.clearSelection()
        self._drag_row = -1
        event.setDropAction(Qt.MoveAction)
        event.acceptProposedAction()
        event.accept()
        return





class LiveCheckWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(list, int, int, bool)
    failed = Signal(str)

    def __init__(self, rows, texts):
        super().__init__()
        self.rows = rows
        self.t = texts
        self.cancel_requested = False

    def request_cancel(self):
        self.cancel_requested = True

    def run(self):
        try:
            duplicate_map = {}
            for idx, row in enumerate(self.rows):
                url = str(row.get("url", "")).strip()
                if url:
                    duplicate_map.setdefault(url, []).append(idx)

            total = len(self.rows)
            duplicate_count = 0
            invalid_count = 0
            results = []

            for idx, row in enumerate(self.rows):
                if self.cancel_requested:
                    self.finished.emit(results, duplicate_count, invalid_count, True)
                    return

                name = str(row.get("name", "")).strip()
                url = str(row.get("url", "")).strip()

                display_name = name if name else "-"
                self.progress.emit(idx + 1, total if total > 0 else 1, display_name)

                problems = []
                color = None
                tooltip = ""
                url_valid = False

                if not name:
                    problems.append(self.t["status_empty_name"])

                if not url:
                    problems.append(self.t["status_empty_url"])
                elif not (url.startswith("http://") or url.startswith("https://")):
                    problems.append(self.t["status_invalid_url"])
                else:
                    url_valid = True

                if url_valid and not self.test_stream_reachable(url):
                    problems.append(self.t["status_unreachable"])

                if url and len(duplicate_map.get(url, [])) > 1:
                    first_row = duplicate_map[url][0]
                    if idx == first_row:
                        problems.append(self.t["status_duplicate_group"])
                    else:
                        problems.append(self.t["status_duplicate_of"].format(row=first_row + 1))
                    duplicate_count += 1
                    tooltip = self.t["affected_rows"].format(
                        rows=" | ".join(f"#{n + 1}" for n in duplicate_map[url])
                    )

                status_text = self.t["status_ok"]
                if len(problems) == 1:
                    status_text = problems[0]
                elif len(problems) > 1:
                    status_text = self.t["status_multiple"]

                if any(p in problems for p in [self.t["status_empty_name"], self.t["status_empty_url"]]):
                    color = (120, 95, 20, 90)
                    invalid_count += 1
                elif self.t["status_invalid_url"] in problems or self.t["status_unreachable"] in problems:
                    color = (160, 90, 20, 95)
                    invalid_count += 1
                elif any(("Duplicate" in p) or ("duplik" in p.lower()) for p in problems):
                    color = (140, 45, 45, 95)

                flags = {
                    "invalid": any(
                        p in problems
                        for p in [
                            self.t["status_empty_name"],
                            self.t["status_empty_url"],
                            self.t["status_invalid_url"],
                            self.t["status_unreachable"],
                        ]
                    ),
                    "duplicate": any(
                        (p == self.t["status_duplicate_group"])
                        or p.startswith(self.t["status_duplicate_of"].format(row="").strip())
                        for p in problems
                    ),
                    "unreachable": self.t["status_unreachable"] in problems,
                    "ok": len(problems) == 0,
                }

                results.append({
                    "status_text": status_text,
                    "row_tooltip": tooltip,
                    "url_tooltip": url,
                    "color": color,
                    "flags": flags,
                })

            self.finished.emit(results, duplicate_count, invalid_count, False)
        except Exception as e:
            self.failed.emit(str(e))

    def test_stream_reachable(self, url):
        try:
            resp = requests.get(url, stream=True, allow_redirects=True, timeout=(3, 5))
            ok = 200 <= resp.status_code < 300
            resp.close()
            return ok
        except Exception:
            return False

class Editor(QMainWindow):

    def __init__(self):
        super().__init__()

        self.icon_path = resource_path("myradio_icon.png")

        if os.path.exists(self.icon_path):
            self.setWindowIcon(QIcon(self.icon_path))

        self.lang = "hu"
        self.t = TEXTS[self.lang]
        self.is_dirty = False
        self._copied_row_data = None
        self.check_thread = None
        self.check_worker = None
        self.check_in_progress = False
        self.current_file_path = None
        self.current_data_format = "txt"
        self.current_radio_mode = "auto"
        self.history = []
        self.history_index = -1
        self.history_limit = 50
        self._history_suspended = False
        self._suppress_item_changed = False

        self.setWindowTitle(self.t["title"])
        self.resize(1280, 820)

        self._build_ui()
        self.apply_language()
        self.apply_table_layout()
        self.setup_shortcuts()
        self.reset_history()

    def tr(self, key, **kwargs):
        return self.t[key].format(**kwargs)

    def _build_ui(self):
        main = QWidget()
        self.setCentralWidget(main)
        self.root_layout = QVBoxLayout(main)
        self.root_layout.setContentsMargins(10, 10, 10, 10)
        self.root_layout.setSpacing(10)

        top = QHBoxLayout()
        top.setSpacing(8)

        self.ip_label = QLabel()
        self.ip = QLineEdit("192.168.1.100")
        self.ip.setClearButtonEnabled(True)

        self.langBox = QComboBox()
        self.langBox.addItems(["HU", "EN"])
        self.langBox.setCurrentText("HU")
        self.langBox.currentIndexChanged.connect(self.change_lang)

        self.radioLabel = QLabel()
        self.radioBox = QComboBox()
        self.radioBox.currentIndexChanged.connect(self.on_radio_mode_changed)

        self.readBtn = QPushButton()
        self.readBtn.clicked.connect(self.read_radio)

        self.writeBtn = QPushButton()
        self.writeBtn.clicked.connect(self.write_radio)

        self.openBtn = QPushButton()
        self.openBtn.clicked.connect(self.open_file)

        self.saveBtn = QPushButton()
        self.saveBtn.clicked.connect(self.save_file)

        self.mergeBtn = QPushButton()
        self.mergeBtn.clicked.connect(self.merge_file)

        self.clearBtn = QPushButton()
        self.clearBtn.clicked.connect(self.clear_list)

        top.addWidget(self.ip_label)
        top.addWidget(self.ip, 1)
        top.addWidget(self.readBtn)
        top.addWidget(self.writeBtn)
        top.addWidget(self.openBtn)
        top.addWidget(self.saveBtn)
        top.addWidget(self.mergeBtn)
        top.addWidget(self.clearBtn)
        top.addWidget(self.radioLabel)
        top.addWidget(self.radioBox, 0)
        top.addWidget(self.langBox, 0)
        self.root_layout.addLayout(top)

        filter_row = QHBoxLayout()
        filter_row.setSpacing(8)

        self.searchLabel = QLabel()
        self.searchEdit = QLineEdit()
        self.searchEdit.textChanged.connect(self.apply_filters)

        self.filterLabel = QLabel()
        self.filterBox = QComboBox()
        self.filterBox.currentIndexChanged.connect(self.apply_filters)

        filter_row.addWidget(self.searchLabel)
        filter_row.addWidget(self.searchEdit, 1)
        filter_row.addWidget(self.filterLabel)
        filter_row.addWidget(self.filterBox, 0)
        self.root_layout.addLayout(filter_row)

        self.table = StationsTable(self, 0, 5)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setWordWrap(False)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["#", "", "", "", ""])
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked
            | QAbstractItemView.EditKeyPressed
            | QAbstractItemView.AnyKeyPressed
        )

        self.table.setDragDropMode(QAbstractItemView.DragDrop)
        self.table.setDragEnabled(True)
        self.table.setAcceptDrops(True)
        self.table.viewport().setAcceptDrops(True)
        self.table.setDropIndicatorShown(True)
        self.table.setDragDropOverwriteMode(False)
        self.table.setDefaultDropAction(Qt.MoveAction)

        self.table.itemChanged.connect(self.on_table_item_changed)
        self.root_layout.addWidget(self.table, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        self.addBtn = QPushButton()
        self.addBtn.clicked.connect(self.add_row)

        self.delBtn = QPushButton()
        self.delBtn.clicked.connect(self.delete_row)

        self.cloneBtn = QPushButton()
        self.cloneBtn.clicked.connect(self.clone_row)

        self.undoBtn = QPushButton()
        self.undoBtn.clicked.connect(self.undo_last_action)

        self.redoBtn = QPushButton()
        self.redoBtn.clicked.connect(self.redo_last_action)

        self.checkBtn = QPushButton()
        self.cancelBtn = QPushButton()
        self.cancelBtn.setText(self.tr('cancel'))
        self.cancelBtn.setEnabled(False)
        self.cancelBtn.clicked.connect(self.cancel_live_check)
        self.checkBtn.clicked.connect(self.run_manual_check)

        self.dedupeBtn = QPushButton()
        self.dedupeBtn.clicked.connect(self.remove_duplicates)

        self.uppercaseBtn = QPushButton()
        self.uppercaseBtn.clicked.connect(self.convert_names_uppercase)

        self.titlecaseBtn = QPushButton()
        self.titlecaseBtn.clicked.connect(self.convert_names_titlecase)

        actions.addWidget(self.addBtn)
        actions.addWidget(self.delBtn)
        actions.addWidget(self.cloneBtn)
        actions.addWidget(self.undoBtn)
        actions.addWidget(self.redoBtn)
        actions.addWidget(self.checkBtn)
        actions.addWidget(self.cancelBtn)
        actions.addWidget(self.dedupeBtn)
        actions.addWidget(self.uppercaseBtn)
        actions.addWidget(self.titlecaseBtn)
        actions.addStretch(1)
        self.root_layout.addLayout(actions)

        footer = QHBoxLayout()
        footer.setSpacing(12)

        self.progressLabel = QLabel(self.tr("progress_idle"))
        self.progressLabel.setFixedWidth(420)
        self.progressBar = QProgressBar()
        self.progressBar.setMaximumWidth(250)
        self.progressBar.setValue(0)

        footer.addWidget(self.progressLabel, 0)
        footer.addWidget(self.progressBar, 0)

        self.summaryLabel = QLabel("")
        self.summaryLabel.setMinimumHeight(42)
        self.summaryLabel.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.summaryLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.summaryLabel.setStyleSheet(
            "QLabel {"
            " padding: 6px 10px;"
            " border: 1px solid rgba(255,255,255,0.10);"
            " border-radius: 6px;"
            "}"
        )
        footer.addWidget(self.summaryLabel, 1)

        self.footerIconLabel = QLabel()
        self.footerIconLabel.setMinimumHeight(42)
        self.footerIconLabel.setAlignment(Qt.AlignVCenter | Qt.AlignRight)

        if os.path.exists(self.icon_path):
            pix = QPixmap(self.icon_path)
            if not pix.isNull():
                self.footerIconLabel.setPixmap(
                    pix.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                )

        self.footerLabel = QLabel(APP_FOOTER)
        self.footerLabel.setMinimumHeight(42)
        self.footerLabel.setAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.footerLabel.setStyleSheet(
            "QLabel {"
            " padding: 6px 6px;"
            " color: rgba(255,255,255,0.75);"
            "}"
        )

        footer.addWidget(self.footerIconLabel, 0)
        footer.addWidget(self.footerLabel, 0)

        self.root_layout.addLayout(footer)

        status = QStatusBar()
        self.setStatusBar(status)
        self.statusBar().showMessage("")

    def setup_shortcuts(self):
        self.copyShortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        self.copyShortcut.activated.connect(self.copy_current_row)

        self.pasteShortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        self.pasteShortcut.activated.connect(self.paste_row_below)

        self.undoShortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        self.undoShortcut.activated.connect(self.undo_last_action)

        self.redoShortcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        self.redoShortcut.activated.connect(self.redo_last_action)

    def apply_language(self):
        self.t = TEXTS[self.lang]
        self.setWindowTitle(self.tr("title"))

        self.ip_label.setText(self.tr("ip"))
        self.readBtn.setText(self.tr("read"))
        self.writeBtn.setText(self.tr("write"))
        self.openBtn.setText(self.tr("open"))
        self.saveBtn.setText(self.tr("save"))
        self.mergeBtn.setText(self.tr("merge"))
        self.clearBtn.setText(self.tr("clear"))
        self.addBtn.setText(self.tr("add"))
        self.delBtn.setText(self.tr("delete"))
        self.cloneBtn.setText(self.tr("clone"))
        self.undoBtn.setText(self.tr("undo"))
        self.redoBtn.setText(self.tr("redo"))
        self.checkBtn.setText(self.tr("check"))
        self.dedupeBtn.setText(self.tr("dedupe"))
        self.uppercaseBtn.setText(self.tr("uppercase"))
        self.titlecaseBtn.setText(self.tr("titlecase"))
        self.cancelBtn.setText(self.tr('cancel'))
        self.searchLabel.setText(self.tr("search"))
        self.searchEdit.setPlaceholderText(self.tr("search_placeholder"))
        self.filterLabel.setText(self.tr("filter"))
        self.radioLabel.setText(self.tr("radio_type"))

        current_radio = self.radioBox.currentData() if self.radioBox.count() else self.current_radio_mode
        self.radioBox.blockSignals(True)
        self.radioBox.clear()
        self.radioBox.addItem(self.tr("radio_auto"), "auto")
        self.radioBox.addItem(self.tr("radio_myradio"), "myradio")
        self.radioBox.addItem(self.tr("radio_yoradio"), "ëRadio")
        radio_index = self.radioBox.findData(current_radio)
        self.radioBox.setCurrentIndex(radio_index if radio_index >= 0 else 0)
        self.radioBox.blockSignals(False)

        current_filter = self.filterBox.currentData() if self.filterBox.count() else "all"
        self.filterBox.blockSignals(True)
        self.filterBox.clear()
        self.filterBox.addItem(self.tr("filter_all"), "all")
        self.filterBox.addItem(self.tr("filter_invalid"), "invalid")
        self.filterBox.addItem(self.tr("filter_duplicates"), "duplicate")
        self.filterBox.addItem(self.tr("filter_unreachable"), "unreachable")
        index = self.filterBox.findData(current_filter)
        self.filterBox.setCurrentIndex(index if index >= 0 else 0)
        self.filterBox.blockSignals(False)

        self.table.setHorizontalHeaderLabels(
            ["#", self.tr("name"), self.tr("url"), self.tr("volume"), self.tr("status")]
        )

        self.set_progress_idle()
        self.update_summary()
        self.check_rows(silent=True)
        self.apply_filters()
        self.update_undo_redo_buttons()

    def apply_table_layout(self):
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.table.setColumnWidth(0, 55)
        self.table.setColumnWidth(1, 320)
        self.table.setColumnWidth(2, 470)
        self.table.setColumnWidth(3, 80)
        self.table.setColumnWidth(4, 180)

        header.sectionClicked.connect(self.on_header_clicked)



    def capture_table_state(self):
        return {
            "rows": [self.get_row_payload(r) for r in range(self.table.rowCount())],
            "selected_row": self.table.currentRow(),
            "is_dirty": self.is_dirty,
            "current_file_path": self.current_file_path,
            "current_data_format": self.current_data_format,
        }

    def apply_state(self, state):
        self._history_suspended = True
        self._suppress_item_changed = True
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for payload in state.get("rows", []):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(payload.get("name", ""))
                self.table.item(r, 2).setText(payload.get("url", ""))
                self.table.item(r, 3).setText(payload.get("volume", "0"))
        finally:
            self.table.blockSignals(False)
            self._suppress_item_changed = False
            self._history_suspended = False

        self.update_numbers()
        self.check_rows(silent=True)
        selected_row = state.get("selected_row", -1)
        if 0 <= selected_row < self.table.rowCount():
            self.table.selectRow(selected_row)
        elif self.table.rowCount() > 0:
            self.table.selectRow(min(self.table.rowCount() - 1, 0))
        self.current_file_path = state.get("current_file_path")
        self.current_data_format = state.get("current_data_format", "txt")
        self.is_dirty = bool(state.get("is_dirty", False))
        self.apply_filters()
        self.update_undo_redo_buttons()

    def push_history_state(self):
        if self._history_suspended:
            return

        state = self.capture_table_state()
        current_state = self.history[self.history_index] if 0 <= self.history_index < len(self.history) else None
        if current_state == state:
            self.update_undo_redo_buttons()
            return

        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]

        self.history.append(state)

        if len(self.history) > self.history_limit:
            overflow = len(self.history) - self.history_limit
            self.history = self.history[overflow:]
            self.history_index = max(0, self.history_index - overflow)

        self.history_index = len(self.history) - 1
        self.update_undo_redo_buttons()

    def reset_history(self):
        self.history = [self.capture_table_state()]
        self.history_index = 0
        self.update_undo_redo_buttons()

    def update_undo_redo_buttons(self):
        if hasattr(self, "undoBtn"):
            self.undoBtn.setEnabled(self.history_index > 0 and not self.check_in_progress)
        if hasattr(self, "redoBtn"):
            self.redoBtn.setEnabled(self.history_index < len(self.history) - 1 and not self.check_in_progress)

    def undo_last_action(self):
        if self.check_in_progress or self.history_index <= 0:
            return

        self.history_index -= 1
        self.apply_state(self.history[self.history_index])
        self.statusBar().showMessage(self.tr("undo_done"), 2000)

    def redo_last_action(self):
        if self.check_in_progress or self.history_index >= len(self.history) - 1:
            return

        self.history_index += 1
        self.apply_state(self.history[self.history_index])
        self.statusBar().showMessage(self.tr("redo_done"), 2000)

    def get_row_payload(self, row):
        return {
            "name": self.get_cell_text(row, 1),
            "url": self.get_cell_text(row, 2),
            "volume": self.get_cell_text(row, 3),
        }

    def rebuild_from_payloads(self, payloads, selected_row=None):
        self._suppress_item_changed = True
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for payload in payloads:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(payload.get("name", ""))
                self.table.item(r, 2).setText(payload.get("url", ""))
                self.table.item(r, 3).setText(payload.get("volume", "0"))
        finally:
            self.table.blockSignals(False)
            self._suppress_item_changed = False

        self.update_numbers()
        self.check_rows(silent=True)
        if selected_row is not None and 0 <= selected_row < self.table.rowCount():
            self.table.selectRow(selected_row)
        self.mark_dirty()

    def move_row_data(self, source_row, target_row):
        row_count = self.table.rowCount()
        if source_row < 0 or source_row >= row_count:
            return

        if target_row < 0:
            target_row = 0
        if target_row > row_count - 1:
            target_row = row_count - 1

        if source_row == target_row:
            return

        payloads = [self.get_row_payload(r) for r in range(row_count)]
        moved = payloads.pop(source_row)
        payloads.insert(target_row, moved)
        self.rebuild_from_payloads(payloads, selected_row=target_row)
        self.push_history_state()

    def on_header_clicked(self, section):
        if section != 1:
            return

        payloads = [self.get_row_payload(r) for r in range(self.table.rowCount())]
        ascending = getattr(self, "_name_sort_ascending", True)
        payloads.sort(key=lambda p: p.get("name", "").casefold())
        if not ascending:
            payloads.reverse()
        self._name_sort_ascending = not ascending
        self.rebuild_from_payloads(payloads, selected_row=0 if payloads else None)
        self.push_history_state()

    def change_lang(self):
        self.lang = "hu" if self.langBox.currentText() == "HU" else "en"
        self.apply_language()

    def mark_dirty(self, dirty=True):
        self.is_dirty = dirty

    def on_table_item_changed(self, item):
        if item is None or self._suppress_item_changed or self._history_suspended:
            return
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()
        self.push_history_state()

    def ensure_row_items(self, row):
        for col in range(self.table.columnCount()):
            if self.table.item(row, col) is None:
                item = QTableWidgetItem("")
                if col == 0:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col, item)

    def get_cell_text(self, row, col):
        item = self.table.item(row, col)
        return item.text().strip() if item else ""

    def clear_row_tooltips(self, row):
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setToolTip("")

    def set_row_tooltip(self, row, text):
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item:
                item.setToolTip(text)

    def set_row_color(self, row, color=None):
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            if item is None:
                item = QTableWidgetItem("")
                self.table.setItem(row, col, item)

            if color is None:
                item.setBackground(QColor(0, 0, 0, 0))
            else:
                item.setBackground(color)


    def build_status_flags(self, problems):
        duplicate_flags = {
            self.tr("status_duplicate_group"),
        }
        duplicate_prefix = self.tr("status_duplicate_of", row=0).replace("0", "").strip()

        has_duplicate = False
        for problem in problems:
            if problem in duplicate_flags:
                has_duplicate = True
                break
            if duplicate_prefix and problem.startswith(duplicate_prefix):
                has_duplicate = True
                break

        has_unreachable = self.tr("status_unreachable") in problems
        has_invalid = any(
            problem in problems
            for problem in [
                self.tr("status_empty_name"),
                self.tr("status_empty_url"),
                self.tr("status_invalid_url"),
                self.tr("status_unreachable"),
            ]
        )

        return {
            "invalid": has_invalid,
            "duplicate": has_duplicate,
            "unreachable": has_unreachable,
            "ok": len(problems) == 0,
        }

    def set_status_flags_for_row(self, row, flags):
        item = self.table.item(row, 4)
        if item is None:
            item = QTableWidgetItem("")
            self.table.setItem(row, 4, item)
        item.setData(Qt.UserRole, flags)

    def get_status_flags_for_row(self, row):
        item = self.table.item(row, 4)
        if not item:
            return {"invalid": False, "duplicate": False, "unreachable": False, "ok": True}
        flags = item.data(Qt.UserRole)
        if isinstance(flags, dict):
            return flags
        return {"invalid": False, "duplicate": False, "unreachable": False, "ok": item.text().strip() == self.tr("status_ok")}

    def row_matches_current_filter(self, row):
        query = self.searchEdit.text().strip().casefold()
        name = self.get_cell_text(row, 1).casefold()
        url = self.get_cell_text(row, 2).casefold()

        if query and query not in name and query not in url:
            return False

        filter_mode = self.filterBox.currentData()
        if filter_mode == "all":
            return True

        flags = self.get_status_flags_for_row(row)

        if filter_mode == "invalid":
            return bool(flags.get("invalid"))
        if filter_mode == "duplicate":
            return bool(flags.get("duplicate"))
        if filter_mode == "unreachable":
            return bool(flags.get("unreachable"))

        return True

    def apply_filters(self):
        if not hasattr(self, "searchEdit") or not hasattr(self, "filterBox"):
            return

        for row in range(self.table.rowCount()):
            self.table.setRowHidden(row, not self.row_matches_current_filter(row))

    def update_numbers(self):
        self.table.blockSignals(True)
        try:
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 0)
                if item is None:
                    item = QTableWidgetItem(str(r + 1))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(r, 0, item)
                else:
                    item.setText(str(r + 1))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        finally:
            self.table.blockSignals(False)

    def add_row(self):
        r = self.table.rowCount()
        self._suppress_item_changed = True
        try:
            self.table.insertRow(r)
            self.ensure_row_items(r)
        finally:
            self._suppress_item_changed = False
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()
        self.table.selectRow(r)
        self.table.scrollToBottom()
        self.set_progress_step(1, 1, self.tr("progress_add", row=r + 1))
        self.push_history_state()

    def delete_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)
            self.update_numbers()
            self.check_rows(silent=True)
            self.mark_dirty()
            self.push_history_state()

    def clone_row(self):
        r = self.table.currentRow()
        if r < 0:
            return

        name = self.get_cell_text(r, 1)
        url = self.get_cell_text(r, 2)
        volume = self.get_cell_text(r, 3)

        new_r = r + 1
        self._suppress_item_changed = True
        try:
            self.table.insertRow(new_r)
            self.ensure_row_items(new_r)
            self.table.item(new_r, 1).setText(name)
            self.table.item(new_r, 2).setText(url)
            self.table.item(new_r, 3).setText(volume or "0")
        finally:
            self._suppress_item_changed = False
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()
        self.push_history_state()

    def copy_current_row(self):
        r = self.table.currentRow()
        if r < 0:
            return

        self._copied_row_data = {
            "name": self.get_cell_text(r, 1),
            "url": self.get_cell_text(r, 2),
            "volume": self.get_cell_text(r, 3),
        }
        self.statusBar().showMessage(self.tr("status_copied"), 2000)

    def paste_row_below(self):
        if not self._copied_row_data:
            self.statusBar().showMessage(self.tr("status_nothing_to_paste"), 2000)
            return

        current = self.table.currentRow()
        insert_at = current + 1 if current >= 0 else self.table.rowCount()

        self._suppress_item_changed = True
        try:
            self.table.insertRow(insert_at)
            self.ensure_row_items(insert_at)
            self.table.item(insert_at, 1).setText(self._copied_row_data["name"])
            self.table.item(insert_at, 2).setText(self._copied_row_data["url"])
            self.table.item(insert_at, 3).setText(self._copied_row_data.get("volume", "0") or "0")
        finally:
            self._suppress_item_changed = False

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()
        self.push_history_state()
        self.statusBar().showMessage(self.tr("status_pasted"), 2000)

    def smart_title_case(self, text):
        def convert_token(match):
            token = match.group(0)
            parts = re.split(r'([-_/.,:;|()\[\]{}]+)', token)
            converted = []
            for part in parts:
                if not part:
                    continue
                if re.fullmatch(r'[-_/.,:;|()\[\]{}]+', part):
                    converted.append(part)
                else:
                    lowered = part.lower()
                    for i, ch in enumerate(lowered):
                        if ch.isalpha():
                            lowered = lowered[:i] + ch.upper() + lowered[i + 1:]
                            break
                    converted.append(lowered)
            return "".join(converted)

        return re.sub(r'\S+', convert_token, text)

    def convert_station_names(self, mode):
        row_count = self.table.rowCount()
        if row_count == 0:
            return

        self._suppress_item_changed = True
        self.table.blockSignals(True)
        try:
            for r in range(row_count):
                self.ensure_row_items(r)
                current = self.get_cell_text(r, 1)
                if not current:
                    continue

                if mode == "upper":
                    new_text = current.upper()
                else:
                    new_text = self.smart_title_case(current)

                self.table.item(r, 1).setText(new_text)
        finally:
            self.table.blockSignals(False)
            self._suppress_item_changed = False

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()

    def convert_names_uppercase(self):
        self.convert_station_names("upper")
        self.push_history_state()

    def convert_names_titlecase(self):
        self.convert_station_names("title")
        self.push_history_state()

    def remove_duplicates(self):
        payloads = []
        seen_urls = set()

        for r in range(self.table.rowCount()):
            payload = self.get_row_payload(r)
            url = payload.get("url", "").strip()

            if url and url in seen_urls:
                continue

            if url:
                seen_urls.add(url)

            payloads.append(payload)

        self.rebuild_from_payloads(payloads, selected_row=0 if payloads else None)
        self.check_rows(silent=True)
        self.push_history_state()

    def clear_list(self):
        answer = confirm_dialog(
            self,
            self.tr("confirm_clear_title"),
            self.tr("confirm_clear_text"),
            self.tr("yes"),
            self.tr("no"),
        )
        if answer:
            self.table.setRowCount(0)
            self.update_summary()
            self.mark_dirty()
            self.current_file_path = None
            self.current_data_format = "txt"
            self.set_progress_idle()
            self.push_history_state()

    def parse_txt_lines(self, lines, append=False):
        if not append:
            self.table.setRowCount(0)

        self.table.blockSignals(True)
        try:
            for raw_line in lines:
                line = raw_line.strip()
                if not line or "\t" not in line:
                    continue

                parts = line.split("\t")
                if len(parts) < 2:
                    continue

                name = parts[0].strip()
                url = parts[1].strip()
                volume = parts[2].strip() if len(parts) > 2 else "0"

                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(name)
                self.table.item(r, 2).setText(url)
                self.table.item(r, 3).setText(volume if volume else "0")
        finally:
            self.table.blockSignals(False)

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()


    def convert_csv_text_to_station_lines(self, csv_text):
        converted_lines = []
        from io import StringIO

        f = StringIO(csv_text)
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except Exception:
            class _FallbackDialect(csv.Dialect):
                delimiter = ","
                quotechar = '"'
                doublequote = True
                skipinitialspace = False
                lineterminator = "\n"
                quoting = csv.QUOTE_MINIMAL
            dialect = _FallbackDialect

        reader = csv.reader(f, dialect)
        for row in reader:
            if len(row) < 2:
                continue
            name = str(row[0]).strip()
            url = str(row[1]).strip()
            volume = str(row[2]).strip() if len(row) > 2 else "0"
            if not name and not url:
                continue
            converted_lines.append(f"{name}\t{url}\t{volume}\n")
        return converted_lines


    def detect_file_format(self, path):
        return "csv" if str(path).lower().endswith(".csv") else "txt"

    def suggested_save_name(self):
        if self.current_file_path:
            base_name = os.path.basename(self.current_file_path)
            if self.current_data_format == "csv" and not base_name.lower().endswith(".csv"):
                stem, _ = os.path.splitext(base_name)
                return f"{stem}.csv"
            if self.current_data_format == "txt" and not base_name.lower().endswith(".txt"):
                stem, _ = os.path.splitext(base_name)
                return f"{stem}.txt"
            return base_name
        return "playlist.csv" if self.current_data_format == "csv" else "stations.txt"

    def convert_station_rows_to_yoradio_lines(self):
        lines = []
        for r in range(self.table.rowCount()):
            name = self.get_cell_text(r, 1)
            url = self.get_cell_text(r, 2)
            volume = self.get_cell_text(r, 3) or "0"
            if name and url:
                lines.append(f"{name}\t{url}\t{volume}\n")
        return lines

    def write_station_file(self, path, target_format):
        if target_format == "csv":
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.writelines(self.convert_station_rows_to_yoradio_lines())
            return

        with open(path, "w", encoding="utf-8") as f:
            for r in range(self.table.rowCount()):
                name = self.get_cell_text(r, 1)
                url = self.get_cell_text(r, 2)
                if name and url:
                    f.write(f"{name}\t{url}\n")

    def load_station_lines(self, path):
        if path.lower().endswith(".csv"):
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                return self.convert_csv_text_to_station_lines(f.read())

        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()


    def on_radio_mode_changed(self):
        if not hasattr(self, "radioBox"):
            return
        self.current_radio_mode = self.radioBox.currentData() or "auto"
        if self.current_radio_mode == "myradio":
            self.statusBar().showMessage(self.tr("using_radio", name=self.tr("radio_myradio")), 2500)
        elif self.current_radio_mode == "ëRadio":
            self.statusBar().showMessage(self.tr("using_radio", name=self.tr("radio_yoradio")), 2500)

    def detect_radio_type(self, ip):
        myradio_url = f"http://{ip}/api/stations"
        yoradio_url = f"http://{ip}/data/playlist.csv"
        myradio_error = ""
        yoradio_error = ""

        self.statusBar().showMessage(self.tr("read_try_myradio"))
        try:
            resp = requests.get(myradio_url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, dict) and "stations" in data:
                return "myradio", data, ""
        except Exception as e:
            myradio_error = str(e)

        self.statusBar().showMessage(self.tr("read_try_yoradio"))
        try:
            resp = requests.get(yoradio_url, timeout=5)
            resp.raise_for_status()
            return "ëRadio", resp.text, myradio_error
        except Exception as e:
            yoradio_error = str(e)

        raise RuntimeError(self.tr("read_fail_combined", myerr=myradio_error or "-", yoerr=yoradio_error or "-"))

    def populate_from_myradio_json(self, data):
        self.table.setRowCount(0)
        self.table.blockSignals(True)
        try:
            for station in data.get("stations", []):
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(str(station.get("name", "")).strip())
                self.table.item(r, 2).setText(str(station.get("url", "")).strip())
                self.table.item(r, 3).setText("0")
        finally:
            self.table.blockSignals(False)

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty(False)
        self.current_file_path = None
        self.current_data_format = "txt"
        self.reset_history()

    def populate_from_yoradio_csv(self, csv_text):
        lines = self.convert_csv_text_to_station_lines(csv_text)
        self.parse_txt_lines(lines, append=False)
        self.mark_dirty(False)
        self.current_file_path = None
        self.current_data_format = "csv"
        self.reset_history()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("open_title"), "", "Station files (*.txt *.csv);;Text files (*.txt);;CSV files (*.csv);;All files (*.*)"
        )
        if not path:
            return

        try:
            self.parse_txt_lines(self.load_station_lines(path), append=False)
            self.mark_dirty(False)
            self.current_file_path = path
            self.current_data_format = self.detect_file_format(path)
            self.reset_history()

            try:
                backup_path = self.create_pre_edit_backup(path)
                if backup_path:
                    self.statusBar().showMessage(
                        self.tr("backup_created", name=os.path.basename(backup_path)),
                        5000
                    )
            except Exception as backup_error:
                QMessageBox.critical(self, self.tr("error"), self.tr("backup_fail", err=backup_error))
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), self.tr("open_fail", err=e))

    def merge_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("merge_title"), "", "Station files (*.txt *.csv);;Text files (*.txt);;CSV files (*.csv);;All files (*.*)"
        )
        if not path:
            return

        try:
            self.parse_txt_lines(self.load_station_lines(path), append=True)
            self.push_history_state()
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), self.tr("merge_fail", err=e))


    def create_timestamped_backup(self, path, label="backup"):
        if not path or not os.path.exists(path):
            return None

        folder = os.path.dirname(path) or "."
        stem, ext = os.path.splitext(os.path.basename(path))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{stem}_{label}_{timestamp}{ext or '.txt'}"
        backup_path = os.path.join(folder, backup_name)

        with open(path, "rb") as src_f, open(backup_path, "wb") as dst_f:
            dst_f.write(src_f.read())

        return backup_path

    def create_backup_if_needed(self, path):
        return self.create_timestamped_backup(path, "backup")

    def create_pre_edit_backup(self, path):
        return self.create_timestamped_backup(path, "preedit_backup")

    def save_file(self):
        default_name = self.suggested_save_name()
        path, _ = QFileDialog.getSaveFileName(
            self,
            self.tr("save_title"),
            default_name,
            "Station files (*.txt *.csv);;Text files (*.txt);;CSV files (*.csv);;All files (*.*)"
        )
        if not path:
            return

        target_format = self.detect_file_format(path)

        try:
            backup_path = self.create_backup_if_needed(path)
            self.write_station_file(path, target_format)

            self.mark_dirty(False)
            self.current_file_path = path
            self.current_data_format = target_format
            self.push_history_state()

            if backup_path:
                self.statusBar().showMessage(
                    self.tr("backup_created", name=os.path.basename(backup_path)),
                    5000
                )
        except Exception as e:
            err_text = str(e)
            if "backup" in err_text.lower():
                QMessageBox.critical(self, self.tr("error"), self.tr("backup_fail", err=e))
            else:
                QMessageBox.critical(self, self.tr("error"), self.tr("save_fail", err=e))

    def read_radio(self):
        ip = self.ip.text().strip()
        selected_mode = self.radioBox.currentData() if hasattr(self, "radioBox") else self.current_radio_mode

        try:
            if selected_mode == "myradio":
                self.statusBar().showMessage(self.tr("read_try_myradio"))
                resp = requests.get(f"http://{ip}/api/stations", timeout=8)
                resp.raise_for_status()
                data = resp.json()
                self.populate_from_myradio_json(data)
                self.statusBar().showMessage(self.tr("using_radio", name=self.tr("radio_myradio")), 3000)
                return

            if selected_mode == "ëRadio":
                self.statusBar().showMessage(self.tr("read_try_yoradio"))
                resp = requests.get(f"http://{ip}/data/playlist.csv", timeout=8)
                resp.raise_for_status()
                self.populate_from_yoradio_csv(resp.text)
                self.statusBar().showMessage(self.tr("using_radio", name=self.tr("radio_yoradio")), 3000)
                return

            detected_type, payload, _ = self.detect_radio_type(ip)
            if detected_type == "myradio":
                self.populate_from_myradio_json(payload)
                self.statusBar().showMessage(self.tr("detected_radio", name=self.tr("radio_myradio")), 4000)
            else:
                self.populate_from_yoradio_csv(payload)
                self.statusBar().showMessage(self.tr("detected_radio", name=self.tr("radio_yoradio")), 4000)
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), str(e))

    def write_radio(self):
        ip = self.ip.text().strip()
        selected_mode = self.radioBox.currentData() if hasattr(self, "radioBox") else self.current_radio_mode

        try:
            target_mode = selected_mode
            if target_mode == "auto":
                detected_type, _, _ = self.detect_radio_type(ip)
                target_mode = detected_type
                if target_mode == "myradio":
                    self.statusBar().showMessage(self.tr("detected_radio", name=self.tr("radio_myradio")), 3000)
                else:
                    self.statusBar().showMessage(self.tr("detected_radio", name=self.tr("radio_yoradio")), 3000)

            if target_mode == "myradio":
                self.statusBar().showMessage(self.tr("write_try_myradio"))
                lines = []
                for r in range(self.table.rowCount()):
                    name = self.get_cell_text(r, 1)
                    link = self.get_cell_text(r, 2)
                    if name and link:
                        lines.append(f"{name}\t{link}")
                payload = "\n".join(lines) + ("\n" if lines else "")
                files = {"file": ("stations.txt", payload, "text/plain")}
                resp = requests.post(f"http://{ip}/upload", data={"path": "/stations.txt"}, files=files, timeout=20)
                resp.raise_for_status()
                self.mark_dirty(False)
                self.current_data_format = "txt"
                QMessageBox.information(self, self.tr("ok"), self.tr("upload_ok"))
                return

            self.statusBar().showMessage(self.tr("write_try_yoradio"))
            yoradio_payload = "".join(self.convert_station_rows_to_yoradio_lines())
            files = {"plfile": ("playlist.csv", yoradio_payload, "text/csv")}
            resp = requests.post(f"http://{ip}/upload", files=files, timeout=20)
            resp.raise_for_status()
            self.mark_dirty(False)
            self.current_data_format = "csv"
            QMessageBox.information(self, self.tr("ok"), self.tr("upload_ok_yoradio"))
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), self.tr("write_fail", err=e))

    def test_stream_reachable(self, url):
        try:
            resp = requests.get(url, stream=True, allow_redirects=True, timeout=(3, 5))
            ok = 200 <= resp.status_code < 300
            resp.close()
            return ok
        except Exception:
            return False

    def run_manual_check(self):
        self.start_live_check()

    def check_rows(self, silent=False, live=False):
        duplicate_map = {}
        for r in range(self.table.rowCount()):
            url = self.get_cell_text(r, 2)
            if url:
                duplicate_map.setdefault(url, []).append(r)

        total = self.table.rowCount()
        duplicate_count = 0
        invalid_count = 0

        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.table.blockSignals(True)
        try:
            for r in range(self.table.rowCount()):
                self.ensure_row_items(r)
                self.clear_row_tooltips(r)

                name = self.get_cell_text(r, 1)
                url = self.get_cell_text(r, 2)

                problems = []
                color = None
                url_valid = False

                if not name:
                    problems.append(self.tr("status_empty_name"))

                if not url:
                    problems.append(self.tr("status_empty_url"))
                elif not (url.startswith("http://") or url.startswith("https://")):
                    problems.append(self.tr("status_invalid_url"))
                else:
                    url_valid = True

                if live and url_valid and not self.test_stream_reachable(url):
                    problems.append(self.tr("status_unreachable"))

                if url and len(duplicate_map.get(url, [])) > 1:
                    first_row = duplicate_map[url][0]
                    if r == first_row:
                        problems.append(self.tr("status_duplicate_group"))
                    else:
                        problems.append(self.tr("status_duplicate_of", row=first_row + 1))
                    duplicate_count += 1

                    rows_text = " | ".join(f"#{idx + 1}" for idx in duplicate_map[url])
                    self.set_row_tooltip(r, self.tr("affected_rows", rows=rows_text))

                status_text = self.tr("status_ok")
                if len(problems) == 1:
                    status_text = problems[0]
                elif len(problems) > 1:
                    status_text = self.tr("status_multiple")

                if any(p in problems for p in [self.tr("status_empty_name"), self.tr("status_empty_url")]):
                    color = QColor(120, 95, 20, 90)
                    invalid_count += 1
                elif self.tr("status_invalid_url") in problems or self.tr("status_unreachable") in problems:
                    color = QColor(160, 90, 20, 95)
                    invalid_count += 1
                elif any("Duplicate" in p or "duplik" in p.lower() for p in problems):
                    color = QColor(140, 45, 45, 95)

                self.table.item(r, 4).setText(status_text)
                self.set_status_flags_for_row(r, self.build_status_flags(problems))

                full_url_item = self.table.item(r, 2)
                if full_url_item:
                    full_url_item.setToolTip(url)

                self.set_row_color(r, color)
                QApplication.processEvents()
        finally:
            self.table.blockSignals(False)
            QApplication.restoreOverrideCursor()

        self.update_summary(total, duplicate_count, invalid_count)

        if live:
            self.set_progress_step(
                total if total > 0 else 1,
                total if total > 0 else 1,
                self.tr("progress_done", total=total)
            )

        self.apply_filters()

        if not silent:
            QMessageBox.information(self, self.tr("ok"), self.tr("check_done"))


    def set_progress_idle(self):
        self.progressLabel.setText(self.tr("progress_idle"))
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(0)

    def set_progress_step(self, current, total, name_or_text):
        total = max(1, total)
        current = max(0, min(current, total))
        text = name_or_text
        self.progressLabel.setText(text)
        self.progressBar.setRange(0, total)
        self.progressBar.setValue(current)

    def set_ui_enabled_for_check(self, enabled):
        widgets = [
            self.readBtn, self.writeBtn, self.openBtn, self.saveBtn,
            self.mergeBtn, self.clearBtn, self.langBox, self.radioBox, self.addBtn,
            self.delBtn, self.cloneBtn, self.undoBtn, self.redoBtn, self.checkBtn, self.dedupeBtn,
            self.uppercaseBtn, self.titlecaseBtn, self.ip, self.table
        ]
        for w in widgets:
            w.setEnabled(enabled)

    def cancel_live_check(self):
        if self.check_worker:
            self.check_worker.request_cancel()
            self.progressLabel.setText(self.tr('cancelled'))
            self.cancelBtn.setEnabled(False)

    def start_live_check(self):
        if self.check_in_progress:
            QMessageBox.information(
                self,
                self.tr("check_running_title"),
                self.tr("check_running_text")
            )
            return

        rows = [self.get_row_payload(r) for r in range(self.table.rowCount())]
        total = len(rows)

        self.check_in_progress = True
        self.set_ui_enabled_for_check(False)
        self.cancelBtn.setEnabled(True)
        self.update_undo_redo_buttons()
        self.progressLabel.setText(self.tr("progress_prepare"))
        self.progressBar.setRange(0, max(1, total))
        self.progressBar.setValue(0)

        self.check_thread = QThread(self)
        self.check_worker = LiveCheckWorker(rows, self.t.copy())
        self.check_worker.moveToThread(self.check_thread)

        self.check_thread.started.connect(self.check_worker.run)
        self.check_worker.progress.connect(self.on_live_check_progress)
        self.check_worker.finished.connect(self.on_live_check_finished)
        self.check_worker.failed.connect(self.on_live_check_failed)

        self.check_worker.finished.connect(self.check_thread.quit)
        self.check_worker.failed.connect(self.check_thread.quit)
        self.check_thread.finished.connect(self.check_thread.deleteLater)
        self.check_thread.finished.connect(self.cleanup_live_check)

        self.check_thread.start()

    def on_live_check_progress(self, current, total, name):
        self.set_progress_step(
            current,
            total,
            self.tr("progress_check", current=current, total=total, name=name)
        )

    def on_live_check_finished(self, results, duplicate_count, invalid_count, cancelled):
        self.table.blockSignals(True)
        try:
            for r, result in enumerate(results):
                self.ensure_row_items(r)
                self.clear_row_tooltips(r)

                self.table.item(r, 4).setText(result.get("status_text", self.tr("status_ok")))

                row_tooltip = result.get("row_tooltip", "")
                if row_tooltip:
                    self.set_row_tooltip(r, row_tooltip)

                url_item = self.table.item(r, 2)
                if url_item:
                    url_item.setToolTip(result.get("url_tooltip", ""))

                color_tuple = result.get("color")
                color = QColor(*color_tuple) if color_tuple else None
                self.set_row_color(r, color)
                self.set_status_flags_for_row(r, result.get("flags", {"invalid": False, "duplicate": False, "unreachable": False, "ok": True}))
        finally:
            self.table.blockSignals(False)

        self.update_summary(self.table.rowCount(), duplicate_count, invalid_count)
        self.apply_filters()
        total = self.table.rowCount()

        if cancelled:
            self.progressLabel.setText(self.tr("check_cancelled"))
            self.progressBar.setValue(min(self.progressBar.value(), max(1, total)))
            return

        self.set_progress_step(
            total if total > 0 else 1,
            total if total > 0 else 1,
            self.tr("progress_done", total=total)
        )
        QMessageBox.information(self, self.tr("ok"), self.tr("check_done"))

    def on_live_check_failed(self, err):
        self.progressLabel.setText(self.tr("progress_error", err=err))
        QMessageBox.critical(self, self.tr("error"), self.tr("progress_error", err=err))

    def cleanup_live_check(self):
        self.check_in_progress = False
        self.set_ui_enabled_for_check(True)
        self.cancelBtn.setEnabled(False)
        self.check_worker = None
        self.check_thread = None
        self.update_undo_redo_buttons()

    def update_summary(self, total=None, duplicate_count=0, invalid_count=0):
        if total is None:
            total = self.table.rowCount()

        over_limit = max(0, total - SOFT_STATION_LIMIT)
        text = (
            f"{self.tr('total')}: {total}   |   "
            f"{self.tr('duplicates')}: {duplicate_count}   |   "
            f"{self.tr('invalid')}: {invalid_count}"
        )

        if over_limit > 0:
            text += f"   |   {self.tr('soft_limit')}: +{over_limit}"

        self.summaryLabel.setText(text)

    def closeEvent(self, event):
        if self.check_in_progress:
            event.ignore()
            return

        if not self.is_dirty:
            event.accept()
            return

        answer = confirm_dialog(
            self,
            self.tr("unsaved_title"),
            self.tr("unsaved_text"),
            self.tr("yes"),
            self.tr("no"),
        )

        if answer:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Editor()
    win.show()
    sys.exit(app.exec())