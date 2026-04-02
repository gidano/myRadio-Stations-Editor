import os
import sys
import requests
import csv
import re

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QLabel, QLineEdit, QComboBox, QHeaderView,
    QAbstractItemView, QSizePolicy, QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QKeySequence, QShortcut, QPixmap


APP_VERSION = "v1.1"
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
        "check": "Check",
        "dedupe": "Remove duplicates",
        "uppercase": "UPPERCASE",
        "titlecase": "Title Case",
        "name": "Station Name",
        "url": "URL",
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
        "check": "Ellenőrzés",
        "dedupe": "Duplikátumok eltávolítása",
        "uppercase": "NAGYBETŰS",
        "titlecase": "Kezdőbetűs",
        "name": "Állomás",
        "url": "Link",
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

        self.setWindowTitle(self.t["title"])
        self.resize(1280, 820)

        self._build_ui()
        self.apply_language()
        self.apply_table_layout()
        self.setup_shortcuts()

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
        top.addWidget(self.langBox, 0)
        self.root_layout.addLayout(top)

        self.table = StationsTable(self, 0, 4)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(False)
        self.table.setWordWrap(False)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setHorizontalHeaderLabels(["#", "", "", ""])
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

        self.checkBtn = QPushButton()
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
        actions.addWidget(self.checkBtn)
        actions.addWidget(self.dedupeBtn)
        actions.addWidget(self.uppercaseBtn)
        actions.addWidget(self.titlecaseBtn)
        actions.addStretch(1)
        self.root_layout.addLayout(actions)

        footer = QHBoxLayout()
        footer.setSpacing(12)

        self.summaryLabel = QLabel("")
        self.summaryLabel.setMinimumHeight(42)
        self.summaryLabel.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
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
        self.checkBtn.setText(self.tr("check"))
        self.dedupeBtn.setText(self.tr("dedupe"))
        self.uppercaseBtn.setText(self.tr("uppercase"))
        self.titlecaseBtn.setText(self.tr("titlecase"))

        self.table.setHorizontalHeaderLabels(
            ["#", self.tr("name"), self.tr("url"), self.tr("status")]
        )

        self.update_summary()
        self.check_rows(silent=True)

    def apply_table_layout(self):
        header = self.table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionsMovable(False)

        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        self.table.setColumnWidth(0, 55)
        self.table.setColumnWidth(1, 320)
        self.table.setColumnWidth(2, 520)
        self.table.setColumnWidth(3, 180)

        header.sectionClicked.connect(self.on_header_clicked)


    def get_row_payload(self, row):
        return {
            "name": self.get_cell_text(row, 1),
            "url": self.get_cell_text(row, 2),
        }

    def rebuild_from_payloads(self, payloads, selected_row=None):
        self.table.blockSignals(True)
        try:
            self.table.setRowCount(0)
            for payload in payloads:
                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(payload.get("name", ""))
                self.table.item(r, 2).setText(payload.get("url", ""))
        finally:
            self.table.blockSignals(False)

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

    def change_lang(self):
        self.lang = "hu" if self.langBox.currentText() == "HU" else "en"
        self.apply_language()

    def mark_dirty(self, dirty=True):
        self.is_dirty = dirty

    def on_table_item_changed(self, item):
        if item is None:
            return
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()

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

    def update_numbers(self):
        self.table.blockSignals(True)
        for r in range(self.table.rowCount()):
            item = self.table.item(r, 0)
            if item is None:
                item = QTableWidgetItem(str(r + 1))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, 0, item)
            else:
                item.setText(str(r + 1))
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        self.table.blockSignals(False)

    def add_row(self):
        r = self.table.rowCount()
        self.table.insertRow(r)
        self.ensure_row_items(r)
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()

    def delete_row(self):
        r = self.table.currentRow()
        if r >= 0:
            self.table.removeRow(r)
            self.update_numbers()
            self.check_rows(silent=True)
            self.mark_dirty()

    def clone_row(self):
        r = self.table.currentRow()
        if r < 0:
            return

        name = self.get_cell_text(r, 1)
        url = self.get_cell_text(r, 2)

        new_r = r + 1
        self.table.insertRow(new_r)
        self.ensure_row_items(new_r)
        self.table.item(new_r, 1).setText(name)
        self.table.item(new_r, 2).setText(url)
        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()

    def copy_current_row(self):
        r = self.table.currentRow()
        if r < 0:
            return

        self._copied_row_data = {
            "name": self.get_cell_text(r, 1),
            "url": self.get_cell_text(r, 2),
        }
        self.statusBar().showMessage(self.tr("status_copied"), 2000)

    def paste_row_below(self):
        if not self._copied_row_data:
            self.statusBar().showMessage(self.tr("status_nothing_to_paste"), 2000)
            return

        current = self.table.currentRow()
        insert_at = current + 1 if current >= 0 else self.table.rowCount()

        self.table.insertRow(insert_at)
        self.ensure_row_items(insert_at)
        self.table.item(insert_at, 1).setText(self._copied_row_data["name"])
        self.table.item(insert_at, 2).setText(self._copied_row_data["url"])

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()
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

        self.update_numbers()
        self.check_rows(silent=True)
        self.mark_dirty()

    def convert_names_uppercase(self):
        self.convert_station_names("upper")

    def convert_names_titlecase(self):
        self.convert_station_names("title")

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

    def parse_txt_lines(self, lines, append=False):
        if not append:
            self.table.setRowCount(0)

        self.table.blockSignals(True)
        try:
            for raw_line in lines:
                line = raw_line.strip()
                if not line or "\t" not in line:
                    continue

                name, url = line.split("\t", 1)
                name = name.strip()
                url = url.strip()

                r = self.table.rowCount()
                self.table.insertRow(r)
                self.ensure_row_items(r)
                self.table.item(r, 1).setText(name)
                self.table.item(r, 2).setText(url)
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
            if not name and not url:
                continue
            converted_lines.append(f"{name}\t{url}\n")
        return converted_lines

    def load_station_lines(self, path):
        if path.lower().endswith(".csv"):
            with open(path, "r", encoding="utf-8-sig", newline="") as f:
                return self.convert_csv_text_to_station_lines(f.read())

        with open(path, "r", encoding="utf-8") as f:
            return f.readlines()

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("open_title"), "", "Station files (*.txt *.csv);;Text files (*.txt);;CSV files (*.csv);;All files (*.*)"
        )
        if not path:
            return

        try:
            self.parse_txt_lines(self.load_station_lines(path), append=False)
            self.mark_dirty(False)
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
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), self.tr("merge_fail", err=e))

    def save_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr("save_title"), "stations.txt", "Text files (*.txt);;All files (*.*)"
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                for r in range(self.table.rowCount()):
                    name = self.get_cell_text(r, 1)
                    url = self.get_cell_text(r, 2)
                    if name and url:
                        f.write(f"{name}\t{url}\n")
            self.mark_dirty(False)
        except Exception as e:
            QMessageBox.critical(self, self.tr("error"), self.tr("save_fail", err=e))

    def read_radio(self):
        ip = self.ip.text().strip()
        myradio_url = f"http://{ip}/api/stations"
        yoradio_url = f"http://{ip}/data/playlist.csv"

        try:
            resp = requests.get(myradio_url, timeout=8)
            resp.raise_for_status()
            data = resp.json()

            self.table.setRowCount(0)
            self.table.blockSignals(True)
            try:
                for station in data.get("stations", []):
                    r = self.table.rowCount()
                    self.table.insertRow(r)
                    self.ensure_row_items(r)
                    self.table.item(r, 1).setText(str(station.get("name", "")).strip())
                    self.table.item(r, 2).setText(str(station.get("url", "")).strip())
            finally:
                self.table.blockSignals(False)

            self.update_numbers()
            self.check_rows(silent=True)
            self.mark_dirty(False)
            return

        except Exception as myradio_error:
            try:
                resp = requests.get(yoradio_url, timeout=8)
                resp.raise_for_status()
                lines = self.convert_csv_text_to_station_lines(resp.text)
                self.parse_txt_lines(lines, append=False)
                self.mark_dirty(False)
                return
            except Exception:
                QMessageBox.critical(self, self.tr("error"), self.tr("read_fail", err=myradio_error))

    def write_radio(self):
        ip = self.ip.text().strip()
        url = f"http://{ip}/upload"

        text = []
        for r in range(self.table.rowCount()):
            name = self.get_cell_text(r, 1)
            link = self.get_cell_text(r, 2)
            if name and link:
                text.append(f"{name}\t{link}")

        payload = "\n".join(text) + ("\n" if text else "")
        files = {"file": ("stations.txt", payload, "text/plain")}

        try:
            resp = requests.post(url, data={"path": "/stations.txt"}, files=files, timeout=20)
            resp.raise_for_status()
            self.mark_dirty(False)
            QMessageBox.information(self, self.tr("ok"), self.tr("upload_ok"))
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
        self.check_rows(silent=False, live=True)

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

                self.table.item(r, 3).setText(status_text)

                full_url_item = self.table.item(r, 2)
                if full_url_item:
                    full_url_item.setToolTip(url)

                self.set_row_color(r, color)
                QApplication.processEvents()
        finally:
            self.table.blockSignals(False)
            QApplication.restoreOverrideCursor()

        self.update_summary(total, duplicate_count, invalid_count)

        if not silent:
            QMessageBox.information(self, self.tr("ok"), self.tr("check_done"))

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