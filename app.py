from datetime import datetime, timedelta
import shutil
from PyQt5.QtCore import QRegExp, QSettings, Qt, QSize
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QToolButton,
    QWidget,
    QTableWidget,
    QTableWidgetItem,
    QCheckBox,
    QFormLayout,
    QLayout,
    QLineEdit,
    QLabel,
    QButtonGroup,
    QComboBox,
    QMenu,
    QGridLayout,
    QMessageBox,
    QErrorMessage,
    QApplication,
    QFileDialog,
    QTabWidget,
    QScrollArea,
    QGroupBox,
    QPushButton,
)

import asyncio
from quamash import QEventLoop
from PyQt5.QtGui import QCloseEvent, QIcon, QRegExpValidator, QFont

from PIL import Image
import logging
import os
import pandas as pd
import numpy as np

from structs import (
    Prints,
    Printer,
    Consummables,
    Printer_addition,
    Consummables_addition,
    Tank_addition,
)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(name)s %(levelname)s:%(message)s",
    filename="app.log",
)
logging.disable(logging.DEBUG)
logger = logging.getLogger("app.py")


class Tracker(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings("config.ini", QSettings.IniFormat)
        self.load_config()
        self.render_ui()

    def render_ui(self) -> None:
        self.tabs = QTabWidget()
        self.tab_tanks = QWidget()
        self.tab_resins = QWidget()
        self.tab_maintenance = QWidget()
        self.tab_prints = QWidget()
        self.tab_printers = QScrollArea()
        self.tab_ui = QScrollArea()

        self.tabs.addTab(self.tab_ui, "New print")
        self.tabs.addTab(self.tab_prints, "Track prints")
        self.tabs.addTab(self.tab_resins, "Track config")
        self.tabs.addTab(self.tab_tanks, "Labelling tracker")
        self.tabs.addTab(self.tab_maintenance, "Maintenance tracker")

        cartridge_tab = QTabWidget()
        cartridge_tab_content = QWidget()
        cartridge_tab.addTab(cartridge_tab_content, "Select a cartridge:")
        self.cartridge_grid = QGridLayout()
        self.cartridge_button_group = QButtonGroup(exclusive=True)

        tank_tab = QTabWidget()
        tank_tab_content = QWidget()
        tank_tab.addTab(tank_tab_content, "Select a tank:")
        self.tank_grid = QGridLayout()
        tank_tab_content.setLayout(self.tank_grid)

        inner_vertical = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setStyleSheet("""QScrollArea {border: none; background-color: white;}""")
        mygroup = QGroupBox()
        mygroup.setStyleSheet(""" QGroupBox {border:none; background-color: white;}""")
        mygroup.setLayout(self.cartridge_grid)
        scroll.setWidget(mygroup)
        scroll.setWidgetResizable(True)
        inner_vertical.addWidget(scroll)
        cartridge_tab_content.setLayout(inner_vertical)

        widget_prints = QWidget()
        self.ui_hbox = QHBoxLayout(widget_prints)
        self.ui_vbox = QVBoxLayout()
        self.preliminary_vbox = QGridLayout()
        self.preliminary_vbox.setColumnMinimumWidth(200, 200)

        self.preliminary_vbox.addWidget(QLabel("The current selection is:"), 0, 0)
        self.preliminary_vbox.addWidget(QLabel("The printer selected is:"), 1, 0)
        self.preliminary_vbox.addWidget(QLabel("The resin selected is:"), 2, 0)
        self.preliminary_vbox.addWidget(QLabel("The tank selected is:"), 3, 0)
        self.preliminary_vbox.addWidget(QLabel("Validate print:"), 4, 0)

        self.ui_vbox.addLayout(self.preliminary_vbox)
        self.ui_vertical = QFormLayout()
        self.render_printer_section()
        self.ui_vertical.addRow(cartridge_tab)
        self.ui_hbox.addLayout(self.ui_vbox)
        self.ui_hbox.addLayout(self.ui_vertical)
        self.tab_ui.setWidget(widget_prints)
        self.tab_ui.setWidgetResizable(True)
        self.tab_ui.setStyleSheet(
            """
            QScrollArea {border: none;}
        """
        )

        self.confirm_prints = QPushButton()
        self.confirm_prints.setIcon(QIcon("assets/plus-solid.svg"))
        self.confirm_prints.setToolTip("Append print to table")
        self.delete_prints = QPushButton()
        self.delete_prints.setIcon(QIcon("assets/circle-minus-solid.svg"))
        self.delete_prints.setToolTip("Delete print from table")
        self.delete_prints.pressed.connect(self.delete_print)
        self.confirm_prints.pressed.connect(self.validate_prints)
        self.preliminary_vbox.addWidget(self.confirm_prints, 4, 1)
        vertical_prints = QVBoxLayout()
        horizontal_prints = QHBoxLayout()
        grid_prints = QGridLayout()

        self.print_date = QLabel("Print date (YYYY/MM/DD):")
        self.print_date_field = QLineEdit()
        self.print_date_field.setText(datetime.now().strftime("%Y/%m/%d"))
        regex = QRegExp(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\/|/)([1-9]|0[1-9]|1[0-2])(\:|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$"
        )
        validator = QRegExpValidator(regex)
        self.print_date_field.setValidator(validator)
        self.print_date_field.textChanged.connect(
            lambda x: self.print_date_field.setStyleSheet("border: 0.5px solid black")
        )
        self.print_date_field.setMaximumWidth(220)

        self.printer_label = QLabel("Printer used:")
        self.printer_combo_box = QComboBox()
        self.printer_combo_box.addItems(self.data["printers"])
        self.printer_label.setBuddy(self.printer_combo_box)
        self.printer_combo_box.setCurrentIndex(-1)
        self.printer_combo_box.currentTextChanged.connect(
            lambda x: self.printer_combo_box.setStyleSheet("border: 0.5px solid black")
        )

        self.resin_label = QLabel("Resin type:")
        self.resin_combo_box = QComboBox()
        self.resin_combo_box.addItems(set(self.data["prints"]["Resin Cartridge"]))
        self.resin_field = QLineEdit()
        self.resin_combo_box.setLineEdit(self.resin_field)
        self.resin_label.setBuddy(self.resin_combo_box)
        self.resin_combo_box.setCurrentIndex(-1)
        self.resin_combo_box.currentTextChanged.connect(
            lambda x: self.resin_combo_box.setStyleSheet("border: 0.5px solid black")
        )

        self.cartridge_id_label = QLabel("Cartridge ID:")
        self.cartridge_id_field = QLineEdit()
        regex_2 = QRegExp("[0-999]+")
        validator_2 = QRegExpValidator(regex_2)
        self.cartridge_id_field.setValidator(validator_2)
        self.cartridge_id_combo_box = QComboBox()
        self.cartridge_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["prints"]["CartridgeID"])))
        )
        self.cartridge_id_label.setBuddy(self.cartridge_id_combo_box)
        self.cartridge_id_combo_box.setLineEdit(self.cartridge_id_field)
        self.cartridge_id_combo_box.setCurrentIndex(-1)
        self.cartridge_id_combo_box.currentTextChanged.connect(
            lambda x: self.cartridge_id_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )
        self.cartridge_id_field.setMaximumWidth(220)

        self.tank_id_label = QLabel("Tank ID:")
        self.tank_id_field = QLineEdit()
        self.tank_id_field.setValidator(validator_2)
        self.tank_id_combo_box = QComboBox()
        self.tank_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["prints"]["TankID"])))
        )
        self.tank_id_label.setBuddy(self.tank_id_combo_box)
        self.tank_id_combo_box.setLineEdit(self.tank_id_field)
        self.tank_id_combo_box.setCurrentIndex(-1)
        self.tank_id_combo_box.currentTextChanged.connect(
            lambda x: self.tank_id_combo_box.setStyleSheet("border: 0.5px solid black")
        )

        self.volume_used_label = QLabel("Volume used in mL:")
        self.volume_used_field = QLineEdit()
        regex_3 = QRegExp("[0-9999]+")
        validator_3 = QRegExpValidator(regex_3)
        self.volume_used_field.setValidator(validator_3)
        self.volume_used_field.textChanged.connect(
            lambda x: self.volume_used_field.setStyleSheet("border: 0.5px solid black")
        )

        self.tank_fill_label = QLabel("Tank fill (~260 mL):")
        self.tank_fill_field = QLineEdit()
        regex_4 = QRegExp("^[no]|^[yes]$")
        validator_4 = QRegExpValidator(regex_4)
        self.tank_fill_field.setValidator(validator_4)
        self.tank_fill_combo_box = QComboBox()
        self.tank_fill_combo_box.addItems(["no", "yes"])
        self.tank_fill_label.setBuddy(self.tank_fill_combo_box)
        self.tank_fill_combo_box.setLineEdit(self.tank_fill_field)
        self.tank_fill_combo_box.setCurrentIndex(-1)
        self.tank_fill_combo_box.currentTextChanged.connect(
            lambda x: self.tank_fill_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )

        self.fail_label = QLabel("Fail:")
        self.fail_field = QLineEdit()
        self.fail_field.setValidator(validator_4)
        self.fail_combo_box = QComboBox()
        self.fail_combo_box.addItems(["no", "yes"])
        self.fail_label.setBuddy(self.fail_combo_box)
        self.fail_combo_box.setLineEdit(self.fail_field)
        self.fail_combo_box.setCurrentIndex(-1)

        self.comments_label = QLabel("Comments:")
        self.comments_field = QLineEdit()

        self.render_tanks_section()
        export = QPushButton()
        export.pressed.connect(self.export_prints)
        export.setIcon(QIcon("assets/download-solid.svg"))
        export.setToolTip("Export prints table to excel sheet")
        grid_prints.addWidget(export, 13, 2)
        grid_prints.addWidget(self.delete_prints, 12, 2)

        vertical_prints.addLayout(grid_prints)
        self.prints_table = QTableWidget()

        font = QFont()
        font.setPointSize(8)
        self.prints_table.setFont(font)
        self.prints_table.setRowCount(self.data["prints"].shape[0] + 1)
        self.prints_table.setColumnCount(self.data["prints"].shape[1])

        self.prints_table.setHorizontalHeaderLabels(self.data["prints"].columns)
        self.prints_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
        )

        for i in range(self.data["prints"].shape[0]):
            for j in range(self.data["prints"].shape[1]):
                self.prints_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["prints"].iloc[i, j]))
                )
                self.prints_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.prints_table.cellChanged.connect(self.prints_edited)

        self.prints_table.scrollToBottom()
        self.prints_table.setSortingEnabled(True)
        horizontal_prints.addLayout(vertical_prints)
        horizontal_prints.addWidget(self.prints_table)

        # Resins tab
        vertical_resins_spliter = QVBoxLayout()
        horizontal_resins = QHBoxLayout()

        export_cartridge = QPushButton()
        export_cartridge.setIcon(QIcon("assets/download-solid.svg"))
        export_cartridge.setToolTip("Export cartridges table to excel sheet")
        export_cartridge.clicked.connect(self.export_cartridges)
        cartridge_add = QPushButton()
        cartridge_add.setIcon(QIcon("assets/plus-solid.svg"))
        cartridge_add.setToolTip("Append cartridge to table")
        cartridge_add.pressed.connect(self.validate_cartrigdes)
        cartridge_del = QPushButton()
        cartridge_del.setIcon(QIcon("assets/circle-minus-solid.svg"))
        cartridge_del.setToolTip("Delete cartridge from table")
        cartridge_del.clicked.connect(self.delete_cartridge)

        self.resins_table = QTableWidget()
        self.resins_table.setFont(font)
        self.resins_table.setRowCount(self.data["resins"].shape[0] + 1)
        self.resins_table.setColumnCount(self.data["resins"].shape[1])
        self.resins_table.setHorizontalHeaderLabels(self.data["resins"].columns)
        self.resins_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
        )

        for i in range(self.data["resins"].shape[0]):
            for j in range(self.data["resins"].shape[1]):
                self.resins_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["resins"].iloc[i, j]))
                )
                self.resins_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.resins_table.cellChanged.connect(self.resins_edited)
        self.resins_table.scrollToBottom()
        self.resins_table.setSortingEnabled(True)

        self.cartridge_table = QTableWidget()
        self.cartridge_table.setFont(font)
        self.cartridge_table.setRowCount(self.data["cartridges"].shape[0] + 1)
        self.cartridge_table.setColumnCount(self.data["cartridges"].shape[1])
        self.cartridge_table.setHorizontalHeaderLabels(self.data["cartridges"].columns)
        self.cartridge_table.horizontalHeader().setDefaultAlignment(
            Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
        )

        for i in range(self.data["cartridges"].shape[0]):
            for j in range(self.data["cartridges"].shape[1]):
                self.cartridge_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["cartridges"].iloc[i, j]))
                )
                self.cartridge_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.cartridge_table.cellChanged.connect(self.cartridges_edited)
        self.cartridge_table.scrollToBottom()
        self.cartridge_table.setSortingEnabled(True)

        horizontal_resins.addLayout(vertical_resins_spliter)
        vertical = QVBoxLayout()
        vertical.addLayout(horizontal_resins)

        horizontal_tanks = QHBoxLayout()

        export_tanks = QPushButton()
        export_tanks.setIcon(QIcon("assets/download-solid.svg"))
        export_tanks.setToolTip("Export tanks table to excel sheet")
        export_tanks.clicked.connect(self.export_tanks)
        tanks_add = QPushButton()
        tanks_add.setIcon(QIcon("assets/plus-solid.svg"))
        tanks_add.setToolTip("Append tank to table")
        # tanks_add.clicked.connect(self.validate_tanks)

        tanks_del = QPushButton()
        tanks_del.setIcon(QIcon("assets/circle-minus-solid.svg"))
        tanks_del.setToolTip("Delete tank from table")
        tanks_del.clicked.connect(self.delete_tank)

        self.tanks = QTableWidget()
        self.tanks.setFont(font)
        self.tanks.setRowCount(self.data["tanks"].shape[0] + 1)
        self.tanks.setColumnCount(self.data["tanks"].shape[1])
        self.tanks.setHorizontalHeaderLabels(self.data["tanks"].columns)
        self.tanks.horizontalHeader().setDefaultAlignment(
            Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
        )

        for i in range(self.data["tanks"].shape[0]):
            for j in range(self.data["tanks"].shape[1]):
                self.tanks.setItem(
                    i, j, QTableWidgetItem(str(self.data["tanks"].iloc[i, j]))
                )
                self.tanks.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.tanks.cellChanged.connect(self.tanks_edited)
        self.tanks.scrollToBottom()
        self.tanks.setSortingEnabled(True)

        vertical.addWidget(self.resins_table)
        vertical.addWidget(export_cartridge)
        vertical_resins_spliter.addWidget(self.tanks)
        vertical_resins_spliter.addWidget(export_tanks)
        horizontal_tanks.addWidget(self.cartridge_table)

        components_widget = QWidget()

        self.tab_printers.setWidget(components_widget)
        self.tab_printers.setWidgetResizable(True)

        # Maintenance tracker
        horizontal_maintenance = QVBoxLayout()

        h_maintenance = QHBoxLayout()
        h_maintenance_2 = QHBoxLayout()
        h_maintenance_3 = QHBoxLayout()
        v_maintenance = QVBoxLayout()
        h_maintenance_2.setSizeConstraint(QLayout.SetFixedSize)

        self.printer_maintenance_label = QLabel(
            "Printer / Consummable:                                                                                                   "
        )
        self.maintenance_printers = QToolButton(self)
        self.maintenance_printers.setFixedWidth(100)

        self.printer_maintenance_combo_box = QMenu()
        self.printers_menu = self.printer_maintenance_combo_box.addMenu("Printers")

        for _ in self.data["printers"]:
            self.printers_menu.addAction(_)

        self.cartridges_menu = self.printer_maintenance_combo_box.addMenu("Cartridges")
        for _ in set(self.data["resins"]["Resin Cartridge.1"]):
            self.cartridges_menu.addAction(_)

        self.tanks_menu = self.printer_maintenance_combo_box.addMenu("Tanks")
        for _ in set(self.data["tanks"]["Resin Tank.1"]):
            self.tanks_menu.addAction(_)

        self.maintenance_printers.setMenu(self.printer_maintenance_combo_box)
        self.maintenance_printers.setPopupMode(QToolButton.InstantPopup)
        self.maintenance_printers.triggered.connect(
            lambda x: self.maintenance_printers.setText(x.text())
        )
        self.maintenance_printers.setMinimumWidth(200)

        self.part_maintenance_label = QLabel(
            "Procedure:                                                                                                 "
        )
        self.part_maintenance_field = QLineEdit()

        self.frequency_maintenance_label = QLabel(
            "Frequency:                                                                                                 "
        )
        self.frequency_maintenance_field = QLineEdit()

        self.date_maintenance_label = QLabel(
            "Date:                                                                                                 "
        )
        self.date_maintenance_field = QLineEdit()

        h_maintenance.addWidget(self.printer_maintenance_label)
        h_maintenance_2.addWidget(self.maintenance_printers)
        h_maintenance.addWidget(self.part_maintenance_label)
        h_maintenance_2.addWidget(self.part_maintenance_field)
        h_maintenance.addWidget(self.date_maintenance_label)
        h_maintenance_2.addWidget(self.date_maintenance_field)
        h_maintenance.addWidget(self.frequency_maintenance_label)
        h_maintenance_2.addWidget(self.frequency_maintenance_field)
        maintenance_add = QPushButton()
        maintenance_add.setIcon(QIcon("assets/plus-solid.svg"))
        maintenance_add.setToolTip("Append maintenance to table")
        maintenance_add.clicked.connect(self.addMaintenance)
        h_maintenance_3.addWidget(maintenance_add)
        maintenance_del = QPushButton()
        maintenance_del.setIcon(QIcon("assets/circle-minus-solid.svg"))
        maintenance_del.setToolTip("Delete maintenance from table")
        maintenance_del.clicked.connect(self.deleteMaintenance)
        h_maintenance_3.addWidget(maintenance_del)

        self.maintenance_tab = QTabWidget()
        columns = list(self.data["maintenance"])
        columns.remove("Frequency")
        columns.remove("Procedure")

        self.maintenance = {_: None for _ in columns}
        for _ in columns:
            df = self.data["maintenance"].rename(columns={_: "Date"})
            df = df.drop(columns=[i for i in columns if i != _])

            df["Date"] = pd.to_datetime(df["Date"])

            df["Reminder"] = df.apply(self.testing, axis=1)

            self.maintenance[_] = QTableWidget()
            self.maintenance[_].setFont(font)

            self.maintenance[_].setRowCount(df.shape[0])
            self.maintenance[_].setColumnCount(df.shape[1] + 1)

            col = list(df.columns)
            col.append("Check up")
            self.maintenance[_].setHorizontalHeaderLabels(col)
            self.maintenance[_].horizontalHeader().setDefaultAlignment(
                Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
            )
            for i in range(df.shape[0]):
                for j in range(df.shape[1] + 1):
                    if j == df.shape[1]:
                        self.maintenance[_].setCellWidget(i, j, QCheckBox())
                        self.maintenance[_].cellWidget(i, j).setStyleSheet(
                            "margin-left:50%; "
                        )
                    else:
                        self.maintenance[_].setItem(
                            i, j, QTableWidgetItem(str(df.iloc[i, j]))
                        )
                        self.maintenance[_].item(i, j).setTextAlignment(
                            Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                        )

            self.maintenance[_].cellChanged.connect(self.maintenance_edited)
            self.maintenance[_].scrollToBottom()
            self.maintenance[_].setSortingEnabled(True)

            self.maintenance_tab.addTab(self.maintenance[_], _)

        v_maintenance.addLayout(h_maintenance)
        v_maintenance.addLayout(h_maintenance_2)
        v_maintenance.addLayout(h_maintenance_3)
        horizontal_maintenance.addLayout(v_maintenance)
        horizontal_maintenance.addWidget(self.maintenance_tab)

        self.tab_prints.setLayout(horizontal_prints)
        self.tab_resins.setLayout(vertical)
        self.tab_tanks.setLayout(horizontal_tanks)
        self.tab_maintenance.setLayout(horizontal_maintenance)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setWindowTitle("3D manager")
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowIcon(QIcon("assets/cube-solid.svg"))

        self.load_last_config()
        self.show()
        self.adjustSize()
        logger.info("UI rendered")

    def testing(self, value):
        if value["Frequency"].startswith("qmo"):
            return value["Date"] + timedelta(days=30)

        elif value["Frequency"].startswith("q3mo"):
            return value["Date"] + timedelta(days=90)

        elif value["Frequency"].startswith("qweekly"):
            return value["Date"] + timedelta(days=7)

    def load_last_config(self):
        try:

            printer = self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                "Printer"
            ]
            resin = self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                "Resin Cartridge"
            ]

            tank = self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                "Resin Tank"
            ]

            for button in self.printer_button_group.buttons():
                if printer in button.toolTip().replace("_", " "):
                    button.setChecked(True)
                    self.printer_button_group.buttonClicked.emit(button)
                    self.printer_button_group.buttonPressed.emit(button)

            for button in self.cartridge_button_group.buttons():
                if resin in button.toolTip().replace("_", " "):
                    button.setChecked(True)
                    self.cartridge_button_group.buttonClicked.emit(button)

            for button in self.tank_button_group.buttons():
                if tank in button.toolTip().replace("_", " "):
                    button.setChecked(True)
                    self.tank_button_group.buttonClicked.emit(button)

            self.print_date_field.setText(datetime.now().strftime("%Y/%m/%d"))

            self.version_combo_box.setCurrentText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                        "Version"
                    ]
                )
            )

            # print(self.data["prints"])
            self.volume_used_field.setText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                        "Volume used (mL)"
                    ]
                )
            )

            self.cartridge_id_combo_box.setCurrentText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                        "CartridgeID"
                    ]
                )
            )

            self.tank_id_combo_box.setCurrentText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                        "TankID"
                    ]
                )
            )

            self.tank_fill_combo_box.setCurrentText(
                self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                    "Tank fill (~260mL)"
                ]
            )

            self.fail_combo_box.setCurrentText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0] - 1, :][
                        "Fail"
                    ]
                )
            )

            self.comments_field.setText(
                str(
                    self.data["prints"].iloc[self.data["prints"].shape[0], :]["Comment"]
                )
            )

        except Exception as e:
            logger.error(e)
            pass

    def addMaintenance(self):
        delta = None
        part = self.maintenance_printers.text()
        if self.frequency_maintenance_field.text().startswith("qmo"):
            delta = 30
        elif self.frequency_maintenance_field.text().startswith("qweekly"):
            delta = 7
        elif self.frequency_maintenance_field.text().startswith("q3mo"):
            delta = 90

        df = pd.DataFrame(
            {
                "Procedure": [self.part_maintenance_field.text()],
                # self.maintenance_printers.text(): [datetime.now().strftime("%Y/%m/%d")],
                "Frequency": [self.frequency_maintenance_field.text()],
                "Date": [self.date_maintenance_field.text()],
                "Reminder": [
                    pd.to_datetime(self.date_maintenance_field.text())
                    + timedelta(days=delta)
                ],
            }
        )

        self.data["maintenance"] = pd.concat(
            [self.data["maintenance"], df], axis=0, ignore_index=True
        )

        frequency = self.data["maintenance"].pop("Frequency")
        self.data["maintenance"].insert(
            self.data["maintenance"].shape[1], "Frequency", frequency
        )

        try:
            self.maintenance[part]
        except KeyError:
            self.maintenance[part] = QTableWidget()

        self.maintenance[part].setRowCount(self.data["maintenance"].shape[0])
        self.maintenance[part].setColumnCount(self.data["maintenance"].shape[1] + 1)
        self.maintenance[part].setHorizontalHeaderLabels(
            self.data["maintenance"].columns
        )

        for i in range(self.data["maintenance"].shape[0]):
            for j in range(self.data["maintenance"].shape[1] + 1):
                if j == df.shape[1]:
                    self.maintenance[part].setCellWidget(i, j, QCheckBox())
                    self.maintenance[part].cellWidget(i, j).setStyleSheet(
                        "margin-left:50%; "
                    )
                else:
                    self.maintenance[part].setItem(
                        i, j, QTableWidgetItem(str(self.data["maintenance"].iloc[i, j]))
                    )
                    self.maintenance[part].item(i, j).setTextAlignment(
                        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                    )

        self.maintenance[part].scrollToBottom()
        self.maintenance[part].setSortingEnabled(True)
        self.maintenance[part].cellChanged.connect(self.maintenance_edited)
        logger.info("Maintenance added successfully!")

    def addPrinter(self):
        valid = True
        if self.printer_field.text() == "":
            self.printer_field.setStyleSheet("border: 1px solid red")
            valid = False

        if self.printer_resin_field.text() == "":
            self.printer_resin_field.setStyleSheet("border: 1px solid red")
            valid = False

        if self.printer_tank_field.text() == "":
            self.printer_tank_field.setStyleSheet("border: 1px solid red")
            valid = False

        if valid:
            self.printers.append(
                Printer(
                    self.printer_field.text(),
                    self.printer_resin_field.text(),
                    self.printer_tank_field.text(),
                )
            )

            self.data["printers"].append(self.printer_field.text())

            logger.info("Printer added successfully!")

    def deleteMaintenance(self):
        columns = list(self.maintenance.keys())

        try:
            if (
                len(
                    self.maintenance[
                        columns[self.maintenance_tab.currentIndex()]
                    ].selectedItems()
                )
                == 0
            ):
                raise IndexError

            else:
                ran_row = [
                    (_.row(), _.column())
                    for _ in self.maintenance[
                        columns[self.maintenance_tab.currentIndex()]
                    ].selectedItems()
                ][0][0]

            # if ran_row == 0:
            #     error = QErrorMessage(self)
            #     error.showMessage("You can't delete column, try rows instead!")
            # else:
            self.maintenance[columns[self.maintenance_tab.currentIndex()]].removeRow(
                self.maintenance[
                    columns[self.maintenance_tab.currentIndex()]
                ].currentRow()
            )
            self.maintenance[columns[self.maintenance_tab.currentIndex()]].showGrid()

            self.data["maintenance"] = self.data["maintenance"].drop(index=ran_row)
            self.data["maintenance"] = self.data["maintenance"].reset_index(drop=True)

            logger.info("Maintenance row delete successfully!")
        except IndexError:
            pass

    def highlight_selected_cartridge(self):
        printer = self.printer_button_group.button(
            self.printer_button_group.checkedId()
        ).toolTip()
        if (
            self.preliminary_vbox.itemAtPosition(2, 1) is not None
            and self.preliminary_vbox.itemAtPosition(2, 2) is not None
        ):
            self.preliminary_vbox.removeWidget(
                self.preliminary_vbox.itemAtPosition(2, 1).widget()
            )
            self.preliminary_vbox.removeWidget(
                self.preliminary_vbox.itemAtPosition(2, 2).widget()
            )

        for button in self.cartridge_button_group.buttons():
            if button.isChecked():
                button.setStyleSheet(
                    """QCheckBox::indicator {
                                image: url(assets/Resins/"""
                    + printer
                    + "/"
                    + button.toolTip()
                    + """.png);
                                border: 1px solid red;}
                        """
                )

                widgets = [
                    self.print_date,
                    self.print_date_field,
                    self.cartridge_id_label,
                    self.cartridge_id_combo_box,
                ]

                col = True
                counter = 0
                for widget in widgets:
                    if col:
                        self.cartridge_grid.addWidget(widget, 2, counter)
                        col = False
                    else:
                        self.cartridge_grid.addWidget(widget, 3, counter)
                        counter += 1
                        col = True

                self.version_combo_box.clear()
                self.version_combo_box.addItems(
                    list(
                        map(
                            lambda x: str(x),
                            set(
                                self.data["prints"]["Version"].loc[
                                    self.data["prints"]["Resin Cartridge"]
                                    == button.toolTip()
                                ]
                            ),
                        )
                    )
                )
                self.version_combo_box.setMinimumWidth(60)
                self.cartridge_id_combo_box.clear()
                self.cartridge_id_combo_box.addItems(
                    list(
                        map(
                            lambda x: str(x),
                            set(
                                self.data["prints"]["CartridgeID"].loc[
                                    self.data["prints"]["Resin Cartridge"]
                                    == button.toolTip()
                                ]
                            ),
                        )
                    )
                )
                self.preliminary_vbox.addWidget(
                    QLabel(button.toolTip().replace("_", " ")), 2, 1
                )
                self.preliminary_vbox.addWidget(self.version_combo_box, 2, 2)

            else:
                button.setStyleSheet(
                    """QCheckBox::indicator {
                            image: url(assets/Resins/"""
                    + printer
                    + "/"
                    + button.toolTip()
                    + """.png);
                            border: 0px solid black;}"""
                )

    def highlight_selected_tank(self):
        for button in self.tank_button_group.buttons():
            if button.isChecked():
                if self.preliminary_vbox.itemAtPosition(3, 1) is not None:
                    self.preliminary_vbox.removeWidget(
                        self.preliminary_vbox.itemAtPosition(3, 1).widget()
                    )
                self.preliminary_vbox.addWidget(
                    QLabel(button.toolTip().replace("_", " ")), 3, 1
                )
                button.setStyleSheet(
                    """QCheckBox::indicator {
                                image: url(assets/Tanks/"""
                    + button.toolTip()
                    + """.png);
                                border: 1px solid red;}
                        """
                )

                self.tank_id_combo_box.clear()
                self.tank_id_combo_box.addItems(
                    list(
                        map(
                            lambda x: str(x),
                            set(
                                self.data["prints"]["TankID"].loc[
                                    self.data["prints"]["Resin Tank"]
                                    == button.toolTip().replace("_", " ")
                                ]
                            ),
                        )
                    )
                )

            else:
                button.setStyleSheet(
                    """QCheckBox::indicator {
                            image: url(assets/Tanks/"""
                    + button.toolTip()
                    + """.png);
                            border: 0px solid black;}"""
                )

    def update_cartridges(self):
        for i in reversed(range(self.cartridge_grid.count())):
            self.cartridge_grid.itemAt(i).widget().deleteLater()

        for i in self.cartridge_button_group.buttons():
            i.deleteLater()

        printer = self.printer_button_group.button(
            self.printer_button_group.checkedId()
        ).toolTip()

        self.version_combo_box = QComboBox()
        self.version_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["prints"]["Version"])))
        )
        self.version_field = QLineEdit()
        regex_1 = QRegExp("[0-9]+")
        validator_1 = QRegExpValidator(regex_1)
        self.version_field.setValidator(validator_1)
        self.version_combo_box.setLineEdit(self.version_field)
        self.version_combo_box.setCurrentIndex(-1)
        self.version_combo_box.currentTextChanged.connect(
            lambda x: self.version_combo_box.setStyleSheet("border: 0.5px solid black")
        )
        # self.version_field.setMaximumWidth(220)

        counter = 0
        current_dir = os.getcwd()
        dir_items = os.listdir(current_dir + "/assets/Resins/" + printer + "/")

        for item in dir_items:
            label = QLabel(item[:-4].replace("_", " "))
            _ = QCheckBox()
            _.setStyleSheet(
                """
                QCheckBox::indicator {
                    image: url(assets/Resins/"""
                + printer
                + "/"
                + item
                + """);
                }
            """
            )
            _.toggled.connect(self.highlight_selected_cartridge)
            _.setToolTip(item[:-4])
            self.cartridge_button_group.addButton(_)

            self.cartridge_grid.addWidget(label, 1, counter)
            self.cartridge_grid.addWidget(_, 0, counter)
            counter += 1

        add_resin_button = QPushButton()
        add_resin_button.setIcon(QIcon("assets/plus-solid.svg"))
        add_resin_button.setFixedSize(QSize(40, 40))
        add_resin_button.setToolTip("Add new printer")
        add_resin_button.clicked.connect(self.save_resin)

        self.cartridge_button_group.addButton(add_resin_button)
        self.cartridge_grid.addWidget(add_resin_button, 0, counter + 1)

        self.print_date = QLabel("Print date (YYYY/MM/DD):")
        self.print_date_field = QLineEdit()
        self.print_date_field.setText(datetime.now().strftime("%Y/%m/%d"))
        regex = QRegExp(
            "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\/|/)([1-9]|0[1-9]|1[0-2])(\:|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$"
        )
        validator = QRegExpValidator(regex)
        self.print_date_field.setValidator(validator)
        self.print_date_field.textChanged.connect(
            lambda x: self.print_date_field.setStyleSheet("border: 0.5px solid black")
        )
        self.print_date_field.setMaximumWidth(220)

        self.cartridge_id_label = QLabel("Cartridge ID:")
        self.cartridge_id_field = QLineEdit()
        regex_2 = QRegExp("[0-999]+")
        validator_2 = QRegExpValidator(regex_2)
        self.cartridge_id_field.setValidator(validator_2)
        self.cartridge_id_combo_box = QComboBox()
        self.cartridge_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["prints"]["CartridgeID"])))
        )
        self.cartridge_id_label.setBuddy(self.cartridge_id_combo_box)
        self.cartridge_id_combo_box.setLineEdit(self.cartridge_id_field)
        self.cartridge_id_combo_box.setCurrentIndex(-1)
        self.cartridge_id_combo_box.currentTextChanged.connect(
            lambda x: self.cartridge_id_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )
        self.cartridge_id_field.setMaximumWidth(220)

        widgets = [
            self.print_date,
            self.print_date_field,
            # self.version_label,
            # self.version_combo_box,
            self.cartridge_id_label,
            self.cartridge_id_combo_box,
        ]

        col = True
        counter = 0
        for widget in widgets:
            if col:
                self.cartridge_grid.addWidget(widget, 2, counter)
                col = False
            else:
                self.cartridge_grid.addWidget(widget, 3, counter)
                counter += 1
                col = True

        logger.info("Updating resins selection")

    def validate_prints(self):
        valid = True
        printer = None
        resin = None
        try:
            printer = (
                self.printer_button_group.checkedButton().toolTip().replace("_", "")
            )

        except AttributeError:
            error = QErrorMessage(self)
            valid = False
            printer = None
            error.showMessage("Please select a printer")

        if valid:
            resin = self.cartridge_button_group.checkedButton().toolTip()

            tank = self.tank_button_group.checkedButton().toolTip().replace("_", " ")

            if self.print_date_field.text() == " ":
                self.print_date_field.setStyleSheet("border: 1px solid red")
                valid = False
            if self.version_combo_box.currentText() == " ":
                self.version_combo_box.setStyleSheet("border: 1px solid red")
                valid = False

            if self.cartridge_id_combo_box.currentText() == "":
                self.cartridge_id_combo_box.setStyleSheet("border: 1px solid red")
                valid = False
            if self.tank_id_combo_box.currentText() == "":
                self.tank_id_combo_box.setStyleSheet("border: 1px solid red")
                valid = False
            if self.volume_used_field.text() == "":
                self.volume_used_field.setStyleSheet("border: 1px solid red")
                valid = False
            if self.tank_fill_combo_box.currentText() == "":
                self.tank_fill_combo_box.setStyleSheet("border: 1px solid red")
                valid = False

            if self.fail_combo_box.currentText() == "":
                fail = np.NaN
            else:
                fail = self.fail_combo_box.currentText()
            if self.comments_field.text() == "":
                comments = np.NaN
            else:
                comments = self.comments_field.text()

            if valid:
                for _ in self.printers:
                    if _.name.replace(" ", "") == printer:
                        printer = _

                for _ in self.consummables:
                    if (
                        _.type == "Resin Cartridge"
                        and _.id == float(self.cartridge_id_combo_box.currentText())
                        and _.resin_type == resin
                    ):
                        resin = _

                for _ in self.consummables:
                    if (
                        _.type == "Tank"
                        and _.id == float(self.tank_id_combo_box.currentText())
                        and tank in _.resin_tank
                    ):
                        tank = _

                try:
                    resin.type += ""
                except (UnboundLocalError, AttributeError):
                    valid = False
                    printer, resin, tank = None, None, None
                    error = QErrorMessage(self)
                    error.showMessage("Please make sure that the resin is defined")
                except TypeError:
                    pass

                try:
                    tank.type += ""
                except (UnboundLocalError, AttributeError):
                    valid = False
                    printer, resin, tank = None, None, None
                    error = QErrorMessage(self)
                    error.showMessage("Please make sure that the tank is defined")
                except TypeError:
                    pass

                if valid:
                    try:
                        if not printer.can_consume(resin):
                            valid = False
                            error = QErrorMessage(self)
                            error.showMessage(
                                "Please select a resin that matches the printer"
                            )
                            printer, resin, tank = None, None, None

                        if not printer.can_consume(tank):
                            valid = False
                            printer, resin, tank = None, None, None
                            error = QErrorMessage(self)
                            error.showMessage(
                                "Please select a tank that matches the printer"
                            )
                    except AttributeError:
                        error = QErrorMessage(self)
                        valid = False
                        resin = None
                        error.showMessage(
                            "The selected combination isn't possible, please double check the items selected"
                        )

                    try:
                        prints = Prints(
                            printer,
                            resin,
                            tank,
                            pd.to_datetime(self.print_date_field.text()),
                            float(self.volume_used_field.text()),
                            self.tank_fill_combo_box.currentText(),
                            fail,
                            comments,
                        )
                        valid = True
                        if prints.date == self.prints[-1].date:
                            valid = False
                            error = QErrorMessage(self)
                            error.showMessage("Duplicate are not allowed")
                            logger.info("Repeats prints are not allowed")

                    except AttributeError:
                        valid = False
                        printer, resin, tank = None, None, None
                        error = QErrorMessage(self)
                        error.showMessage(
                            "Please make sure that the resin/tank is defined"
                        )
                        logger.info("Tank or Resin not defined")

                    if valid:
                        if not prints.can_consume(resin, tank):
                            error = QErrorMessage(self)
                            error.showMessage(
                                "Please select a resin that matches the tank"
                            )
                            printer, resin, tank = None, None, None
                            logger.info("Conflict between cartridge and tank")

                if valid:
                    self.prints.append(prints)
                    self.append_to_prints_df(fail, comments, printer, resin, tank)
                    logger.info(
                        "New print entered, updating prints/Tanks/Resins/Labelling tables"
                    )

    def append_to_prints_df(self, fail, comments, printer, resin, tank):
        df = pd.DataFrame(
            {
                "Date": [pd.to_datetime(self.print_date_field.text())],
                "Printer": [printer.name],
                "Resin Cartridge": [resin.resin_type],
                "Version": [resin.version],
                "CartridgeID": [resin.id],
                "Resin Tank": [tank.resin_tank],
                "TankID": [tank.id],
                "Volume used (mL)": [self.volume_used_field.text()],
                "Tank fill (~260mL)": [self.tank_fill_combo_box.currentText()],
                "Fail": [fail],
                "Comment": [comments],
            }
        )
        try:
            self.data["prints"] = pd.concat(
                [self.data["prints"], df], axis=0, ignore_index=True
            )

            self.prints_table.setRowCount(self.data["prints"].shape[0] + 1)
            self.prints_table.setColumnCount(self.data["prints"].shape[1])

            for i in range(self.data["prints"].shape[0]):
                for j in range(self.data["prints"].shape[1]):
                    self.prints_table.setItem(
                        i, j, QTableWidgetItem(str(self.data["prints"].iloc[i, j]))
                    )
                    self.prints_table.item(i, j).setTextAlignment(
                        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                    )

            self.prints_table.scrollToBottom()

            self.data["resins"].loc[
                (self.data["resins"]["CartridgeID.1"] == resin.id)
                & (self.data["resins"]["Resin Cartridge.1"] == resin.resin_type),
                "Total print volume (mL)",
            ] = self.data["resins"].loc[
                (self.data["resins"]["CartridgeID.1"] == resin.id)
                & (self.data["resins"]["Resin Cartridge.1"] == resin.resin_type),
                "Total print volume (mL)",
            ] + float(
                self.volume_used_field.text()
            )

            self.data["tanks"].loc[
                (self.data["tanks"]["TankID.1"] == tank.id)
                & (self.data["tanks"]["Resin Fill"] == tank.resin_fill),
                "Total print volume (mL).1",
            ] = self.data["tanks"].loc[
                (self.data["tanks"]["TankID.1"] == tank.id)
                & (self.data["tanks"]["Resin Fill"] == tank.resin_fill),
                "Total print volume (mL).1",
            ] + float(
                self.volume_used_field.text()
            )

            self.data["resins"].loc[
                (self.data["resins"]["Total print volume (mL)"] > 950.0)
                & (self.data["resins"]["Status"] != "Replaced")
                & (self.data["resins"]["CartridgeID.1"] == resin.id)
                & (self.data["resins"]["Resin Cartridge.1"] == resin.resin_type),
                "Status",
            ] = "Replaced"

            self.resins_table.setRowCount(self.data["resins"].shape[0] + 1)
            self.resins_table.setColumnCount(self.data["resins"].shape[1])

            for i in range(self.data["resins"].shape[0]):
                for j in range(self.data["resins"].shape[1]):
                    self.resins_table.setItem(
                        i, j, QTableWidgetItem(str(self.data["resins"].iloc[i, j]))
                    )
                    self.resins_table.item(i, j).setTextAlignment(
                        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                    )

            self.resins_table.scrollToBottom()

            self.tanks.setRowCount(self.data["tanks"].shape[0] + 1)
            self.tanks.setColumnCount(self.data["tanks"].shape[1])

            for i in range(self.data["tanks"].shape[0]):
                for j in range(self.data["tanks"].shape[1]):
                    self.tanks.setItem(
                        i, j, QTableWidgetItem(str(self.data["tanks"].iloc[i, j]))
                    )
                    self.tanks.item(i, j).setTextAlignment(
                        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                    )

            self.tanks.scrollToBottom()

            self.cartridge_id_combo_box.setStyleSheet("border: 0.5px solid black")
            self.resin_combo_box.setStyleSheet("border: 0.5px solid black")
        except TypeError:
            self.data["prints"] = self.data["prints"].drop(
                index=self.data["prints"].shape[0] - 1
            )
            self.data["prints"] = self.data["prints"].reset_index(drop=True)

            self.prints_table.setRowCount(self.data["prints"].shape[0] + 1)
            self.prints_table.setColumnCount(self.data["prints"].shape[1])

            for i in range(self.data["prints"].shape[0]):
                for j in range(self.data["prints"].shape[1]):
                    self.prints_table.setItem(
                        i, j, QTableWidgetItem(str(self.data["prints"].iloc[i, j]))
                    )
                    self.prints_table.item(i, j).setTextAlignment(
                        Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                    )

            self.prints_table.scrollToBottom()

            self.prints.pop()

    def export_prints(self):
        filename = QFileDialog.getSaveFileName(self, "Save configuration", os.getcwd(),)

        if filename[0]:
            with pd.ExcelWriter(filename[0] + ".xlsx") as writer:
                self.data["prints"].to_excel(writer, sheet_name="Tracking", index=False)

    def export_cartridges(self):
        filename = QFileDialog.getSaveFileName(self, "Save configuration", os.getcwd(),)

        if filename[0]:
            with pd.ExcelWriter(filename[0] + ".xlsx") as writer:
                self.data["resins"].to_excel(
                    writer, sheet_name="Cartridges", index=False
                )

        logger.info("Exporting cartridges to excel sheet")

    def export_tanks(self):
        filename = QFileDialog.getSaveFileName(self, "Save configuration", os.getcwd(),)

        if filename[0]:
            with pd.ExcelWriter(filename[0] + ".xlsx") as writer:
                self.data["tanks"].to_excel(writer, sheet_name="Tanks", index=False)

        logger.info("Exporting tanks to excel sheet")

    def validate_cartrigdes(self):
        valid = True
        if self.cartridge_id_resins_combo_box.currentText() == "":
            self.cartridge_id_resins_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.resin_type_resins_combo_box.currentText() == "":
            self.resin_type_resins_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.version_resins_combo_box.currentText() == "":
            self.version_resins_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.batch_date_resins_field.text() == "":
            self.batch_date_resins_field.setStyleSheet("border: 1px solid red")
            valid = False

        if self.comments_resins_field.text() == "":
            comments = "nan"
        else:
            comments = self.comments_resins_field.text()

        try:
            self.data["resins"]["CartridgeID.1"] = self.data["resins"][
                "CartridgeID.1"
            ].astype(float)
            i = self.data["resins"].loc[
                (
                    self.data["resins"]["CartridgeID.1"]
                    == float(self.cartridge_id_resins_combo_box.currentText())
                )
                & (
                    self.data["resins"]["Resin Cartridge.1"]
                    == self.resin_type_resins_combo_box.currentText()
                )
            ]

            if isinstance(i.index[0], np.int64):
                self.cartridge_id_resins_combo_box.setStyleSheet(
                    "border: 1px solid red"
                )
                self.resin_type_resins_combo_box.setStyleSheet("border: 1px solid red")
                valid = False
                id = self.data["cartridges"]["Next Cartridge ID"].loc[
                    self.data["cartridges"]["Cartridge"]
                    == self.resin_type_resins_combo_box.currentText()
                ]

                error = QErrorMessage(self)
                error.showMessage(
                    f"Cartridge already in use, please choose the next ID available {id[id.index[0]]}"
                )
                logger.info("User is selecting an already taken cartridge ID")
        except:
            if valid:
                self.append_to_resins_df(comments)
                logger.info("New cartridge entered, updating Resins/Labelling tables")

    def append_to_resins_df(self, data, comments):
        df = pd.DataFrame(
            {
                "CartridgeID.1": [data["CartridgeID.1"]],
                "Resin Cartridge.1": [data["Resin Cartridge.1"]],
                "Version.1": [data["Version"]],
                "Total print volume (mL)": [0.0],
                "Status": ["Cartridge OK"],
                "Batch date": [data["Batch Date"]],
                "Comments": [comments],
            }
        )

        self.data["resins"] = pd.concat(
            [self.data["resins"], df], axis=0, ignore_index=True
        )

        self.resins_table.setRowCount(self.data["resins"].shape[0] + 1)
        self.resins_table.setColumnCount(self.data["resins"].shape[1])

        for i in range(self.data["resins"].shape[0]):
            for j in range(self.data["resins"].shape[1]):
                self.resins_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["resins"].iloc[i, j]))
                )
                self.resins_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        cartridge = Consummables("Resin Cartridge", data["Company"])
        cartridge.requierment_per_type(df.to_dict(orient="records"))
        self.consummables.append(cartridge)

        self.data["cartridges"]["Active Count"].loc[
            self.data["cartridges"]["Cartridge"] == cartridge.resin_type
        ] = (
            self.data["resins"]
            .loc[
                (self.data["resins"]["Resin Cartridge.1"] == cartridge.resin_type)
                & (self.data["resins"]["Status"] == "Cartridge OK")
            ]
            .count()[0]
        )

        self.data["resins"]["Total print volume (mL)"] = self.data["resins"][
            "Total print volume (mL)"
        ].astype(float)

        self.data["cartridges"].loc[
            (self.data["cartridges"]["Cartridge"] == cartridge.resin_type),
            "Next Cartridge ID",
        ] = (
            float(
                list(
                    self.data["resins"]
                    .loc[
                        (self.data["resins"]["Total print volume (mL)"] == 0)
                        & (
                            self.data["resins"]["Resin Cartridge.1"]
                            == cartridge.resin_type
                        ),
                        "CartridgeID.1",
                    ]
                    .sort_values()
                )[-1]
            )
            + 1
        )

        self.data["cartridges"].loc[
            (self.data["cartridges"]["Cartridge"] == cartridge.resin_type),
            "Unused count",
        ] = (
            self.data["resins"]
            .loc[
                (self.data["resins"]["Total print volume (mL)"] == 0.0)
                & (self.data["resins"]["Resin Cartridge.1"] == cartridge.resin_type),
                "CartridgeID.1",
            ]
            .count()
        )

        self.cartridge_table.setRowCount(self.data["cartridges"].shape[0] + 1)
        self.cartridge_table.setColumnCount(self.data["cartridges"].shape[1])

        for i in range(self.data["cartridges"].shape[0]):
            for j in range(self.data["cartridges"].shape[1]):
                self.cartridge_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["cartridges"].iloc[i, j]))
                )
                self.cartridge_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.cartridge_table.scrollToBottom()
        self.resins_table.scrollToBottom()

        self.cartridge_id_combo_box.clear()
        self.cartridge_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["resins"]["CartridgeID.1"])))
        )

        self.version_combo_box.clear()
        self.version_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["resins"]["Version.1"])))
        )

        self.resin_combo_box.clear()
        self.resin_combo_box.addItems(set(self.data["resins"]["Resin Cartridge.1"]))

        # self.cartridge_id_resins_combo_box.setStyleSheet("border: 0.5px solid black")
        # self.resin_type_resins_combo_box.setStyleSheet("border: 0.5px solid black")

    # def validate_tanks(self):
    #     valid = True
    #     if self.tanks_id_combo_box.currentText() == "":
    #         self.tanks_id_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False
    #     if self.tanks_resin_combo_box.currentText() == "":
    #         self.tanks_resin_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False
    #     if self.tanks_resin_fill_combo_box.currentText() == "":
    #         self.version_resins_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False
    #     if self.version_tanks_combo_box.currentText() == "":
    #         self.version_tanks_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False
    #     if self.tanks_total_volume_field.text() == "":
    #         self.tanks_total_volume_field.setStyleSheet("border: 1px solid red")
    #         valid = False
    #     if self.tanks_status_combo_box.currentText() == "":
    #         self.tanks_status_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False

    #     if self.tanks_company_combo_box.currentText() == "":
    #         self.tanks_company_combo_box.setStyleSheet("border: 1px solid red")
    #         valid = False

    #     if self.tanks_opened_date_field.text() == "":
    #         self.tanks_opened_date_field.setStyleSheet("border: 1px solid red")
    #         valid = False

    #     if self.tanks_comments_field.text() == "":
    #         comments = "nan"
    #     else:
    #         comments = self.comments_resins_field.text()

    #     try:
    #         self.data["tanks"]["TankID.1"] = self.data["tanks"]["TankID.1"].astype(
    #             float
    #         )
    #         i = self.data["tanks"].loc[
    #             (
    #                 self.data["tanks"]["TankID.1"]
    #                 == float(self.tanks_id_combo_box.currentText())
    #             )
    #             & (
    #                 self.data["tanks"]["Resin Fill"]
    #                 == self.tanks_resin_fill_combo_box.currentText()
    #             )
    #         ]

    #         if i.shape[0] == 0:
    #             raise IndexError

    #         if isinstance(i.index[0], np.int64):
    #             self.tanks_id_combo_box.setStyleSheet("border: 1px solid red")
    #             self.tanks_resin_fill_combo_box.setStyleSheet("border: 1px solid red")
    #             valid = False
    #             id = self.data["cartridges"]["Next Tank ID"].loc[
    #                 self.data["cartridges"]["Cartridge"]
    #                 == self.tanks_resin_fill_combo_box.currentText()
    #             ]

    #             error = QErrorMessage(self)
    #             error.showMessage(
    #                 f"Tank already in use, please choose the next ID available {id[id.index[0]]}"
    #             )
    #             logger.info("User is selecting an already taken Tank ID")
    #     except IndexError:
    #         if valid:
    #             self.tanks_id_combo_box.setStyleSheet("border: 1px solid black")
    #             self.tanks_resin_fill_combo_box.setStyleSheet("border: 1px solid black")
    #             self.append_to_tanks_df(comments)
    #             logger.info("New tank entered, updating Tanks/Labelling tables")

    def prints_edited(self, i, j):
        # if self.prints_table.item(i, j).text() == "":
        try:
            self.data["prints"].iloc[i, j] = self.prints_table.item(i, j).text()
        except:
            self.data["prints"].loc[i, j] = self.prints_table.item(i, j).text()
        if self.prints_table.rowCount() - 1 == i:
            self.prints_table.setRowCount(self.prints_table.rowCount() + 1)
            self.prints_table.scrollToBottom()
        logger.info("saving changes in the prints table")

    def resins_edited(self, i, j):
        try:
            self.data["resins"].iloc[i, j] = self.resins_table.item(i, j).text()
        except:
            self.data["resins"].loc[i, j] = self.resins_table.item(i, j).text()
        if self.resins_table.rowCount() - 1 == i:
            self.resins_table.setRowCount(self.resins_table.rowCount() + 1)
            self.resins_table.scrollToBottom()
        logger.info("saving changes in the resins table")

    def cartridges_edited(self, i, j):
        try:
            self.data["cartridges"].iloc[i, j] = self.cartridge_table.item(i, j).text()
        except:
            self.data["cartridges"].loc[i, j] = self.resins_table.item(i, j).text()
        if self.cartridge_table.rowCount() - 1 == i:
            self.cartridge_table.setRowCount(self.cartridge_table.rowCount() + 1)
            self.cartridge_table.scrollToBottom()
        logger.info("saving changes in the tables table")

    def tanks_edited(self, i, j):
        try:
            self.data["tanks"].iloc[i, j] = self.tanks.item(i, j).text()
        except:
            self.data["tanks"].loc[i, j] = self.tanks.item(i, j).text()
        if self.tanks.rowCount() - 1 == i:
            self.tanks.setRowCount(self.tanks.rowCount() + 1)
            self.tanks.scrollToBottom()
        logger.info("saving changes in the tanks table")

    def maintenance_edited(self, i, j):
        columns = list(self.maintenance.keys())

        self.data["maintenance"].iloc[i, j] = (
            self.maintenance[columns[self.maintenance_tab.currentIndex()]]
            .item(i, j)
            .text()
        )
        logger.info("saving changes in the maintenance table")

    def append_to_tanks_df(self, data, comments):
        df = pd.DataFrame(
            {
                "TankID.1": [data["TankID.1"]],
                "Resin Tank.1": [data["Resin"]],
                "Resin Fill": [data["Resin Fill"]],
                "Version.2": [data["Version"]],
                "Total print volume (mL).1": [data["Total Volume"]],
                "Status.1": [data["Status"]],
                "Opened date": [data["Opened Date"]],
                "Comments.1": [comments],
            }
        )
        self.data["tanks"] = pd.concat(
            [self.data["tanks"], df], axis=0, ignore_index=True
        )

        tank = Consummables("Tank", data["Company"])
        tank.requierment_per_type(df.to_dict(orient="records"))
        self.consummables.append(tank)

        if (
            self.data["cartridges"]["Next Tank ID"]
            .loc[(self.data["cartridges"]["Cartridge"] == data["Resin Fill"])]
            .size
            == 0
        ):
            df = pd.DataFrame(
                {
                    "Cartridge": [data["Resin Fill"]],
                    "Active Count": [1],
                    "Unused count": [0],
                    "Next Cartridge ID": [1.0],
                    "Next Tank ID": [2.0],
                }
            )
            self.data["cartridges"] = pd.concat(
                [self.data["cartridges"], df], axis=0, ignore_index=True
            )

        else:
            self.data["cartridges"]["Next Tank ID"].loc[
                (self.data["cartridges"]["Cartridge"] == data["Resin Fill"])
            ] = (
                list(
                    self.data["tanks"]["TankID.1"]
                    .loc[
                        (self.data["tanks"]["Resin Fill"] == data["Resin Fill"])
                        & (
                            self.data["tanks"]["Total print volume (mL).1"]
                            == data["Total Volume"]
                        )
                    ]
                    .sort_values()
                )[-1]
                + 1
            )

        self.cartridge_table.setRowCount(self.data["cartridges"].shape[0] + 1)
        self.cartridge_table.setColumnCount(self.data["cartridges"].shape[1])

        for i in range(self.data["cartridges"].shape[0]):
            for j in range(self.data["cartridges"].shape[1]):
                self.cartridge_table.setItem(
                    i, j, QTableWidgetItem(str(self.data["cartridges"].iloc[i, j]))
                )
                self.cartridge_table.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.cartridge_table.scrollToBottom()

        self.tanks.setRowCount(self.data["tanks"].shape[0] + 1)
        self.tanks.setColumnCount(self.data["tanks"].shape[1])

        for i in range(self.data["tanks"].shape[0]):
            for j in range(self.data["tanks"].shape[1]):
                self.tanks.setItem(
                    i, j, QTableWidgetItem(str(self.data["tanks"].iloc[i, j]))
                )
                self.tanks.item(i, j).setTextAlignment(
                    Qt.AlignHCenter | Qt.Alignment(Qt.TextWordWrap)
                )

        self.tanks.scrollToBottom()

        # self.tanks_id_combo_box.setStyleSheet("border: 0.5px solid black")
        # self.tanks_resin_fill_combo_box.setStyleSheet("border: 0.5px solid black")

        # self.tanks_id_combo_box.clear()
        self.tank_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["tanks"]["TankID.1"])))
        )

    def delete_print(self):
        try:
            if len(self.prints_table.selectedItems()) == 0:
                raise IndexError

            else:
                ran_row = [
                    (_.row(), _.column()) for _ in self.prints_table.selectedItems()
                ][0][0]

            if ran_row == 0:
                error = QErrorMessage(self)
                error.showMessage("You can't delete column, try rows instead!")
                logger.info("User is trying to delete a column which is not allowed")
            else:
                self.prints_table.removeRow(self.prints_table.currentRow())
                self.data["prints"] = self.data["prints"].drop(index=ran_row)
                self.data["prints"] = self.data["prints"].reset_index(drop=True)

                self.prints_table.showGrid()
                logger.info("Print row deleted successfully!")

        except IndexError:
            pass

    def delete_tank(self):
        try:
            if len(self.tanks.selectedItems()) == 0:
                raise IndexError

            else:
                ran_row = [(_.row(), _.column()) for _ in self.tanks.selectedItems()][
                    0
                ][0]

            if ran_row == 0:
                error = QErrorMessage(self)
                error.showMessage("You can't delete column, try rows instead!")
                logger.info("User is trying to delete a column which is not allowed")
            else:
                self.tanks.removeRow(self.tanks.currentRow())
                self.data["tanks"] = self.data["tanks"].drop(index=ran_row)
                self.data["tanks"] = self.data["tanks"].reset_index(drop=True)

                self.tanks.showGrid()
                logger.info("Tank row deleted successfully!")

        except IndexError:
            pass

    def delete_cartridge(self):
        try:
            if len(self.resins_table.selectedItems()) == 0:
                raise IndexError
            else:
                ran_row = [
                    (_.row(), _.column()) for _ in self.resins_table.selectedItems()
                ][0][0]

            if ran_row == 0:
                logger.info("User is trying to delete a column which is not allowed")
                error = QErrorMessage(self)
                error.showMessage("You fcan't delete column, try rows instead!")
            else:
                self.tanks.removeRow(self.resins_table.currentRow())
                self.data["resins"] = self.data["resins"].drop(index=ran_row)
                self.data["resins"] = self.data["resins"].reset_index(drop=True)

                self.resins_table.showGrid()
                logger.info("Cartridge row deleted successfully!")

        except IndexError:
            pass

    def save_config(self):
        # settings = QSettings(os.getcwd() + "/config.ini", QSettings.IniFormat)
        self.settings.clear()
        self.settings.setValue("data", self.data)
        self.settings.setValue("prints", self.prints)
        self.settings.setValue("consummables", self.consummables)
        self.settings.setValue("printers", self.printers)
        self.settings.sync()

    def load_config(self):
        if self.settings.contains("data"):
            self.data = self.settings.value("data")
            self.prints = self.settings.value("prints")
            self.consummables = self.settings.value("consummables")
            self.printers = self.settings.value("printers")

            logger.info("Data found in settings, loading last config")
        else:
            self.printers = [
                Printer("Form 2", "SLA", "FormLabs"),
                Printer("Form 3", "SLA", "FormLabs"),
                Printer("CadWorks ufluidics", "DLP", "CadWorks"),
            ]
            self.consummables = []
            self.prints = []

            self.data = {
                "printers": [x.name for x in self.printers],
                "tanks": {},
                "resins": {},
                "cartridges": {},
                "maintenance": {},
                "prints": {},
            }

            xls = pd.ExcelFile("SLA Supply Track 2022.xlsx")
            df1 = pd.read_excel(xls, "Tracking sheet")
            df4 = pd.read_excel(xls, "Maintenance")

            counter = 0
            columns = []
            for _ in df1.columns.values:
                if str(_).startswith("Unnamed"):
                    columns.append(_)
                    counter += 1

            df_tracking = df1.loc[:, : columns[0]].drop(columns=[columns[0]])
            df_tracking["Date"] = pd.to_datetime(df_tracking["Date"])
            self.data["prints"] = df_tracking

            df_cartridge = (
                df1.loc[:, columns[0] : columns[1]]
                .drop(columns=[columns[0], columns[1], "Items"])
                .dropna(axis=0, thresh=4)
                .replace(to_replace=r".[?].+", value="", regex=True)
            )

            df_cartridge["Batch date"] = pd.to_datetime(df_cartridge["Batch date"])
            df_cartridge["Batch date"] = pd.to_datetime(df_cartridge["Batch date"])
            self.data["resins"] = df_cartridge

            df_tanks = (
                df1.loc[:, columns[1] : columns[2]]
                .drop(columns=[columns[1], columns[2]])
                .dropna(axis=0, thresh=4)
                .replace("?", "NaT")
            )

            df_tanks["Opened date"] = pd.to_datetime(df_tanks["Opened date"])
            df_tanks["Opened date"] = pd.to_datetime(df_tanks["Opened date"])
            self.data["tanks"] = df_tanks

            for row in self.data["resins"].to_dict(orient="records"):
                consummable = Consummables("Resin Cartridge", "FormLabs")
                consummable.requierment_per_type(row)
                self.consummables.append(consummable)

            for row in self.data["tanks"].to_dict(orient="records"):
                consummable = Consummables("Tank", "FormLabs")
                consummable.requierment_per_type(row)
                self.consummables.append(consummable)

            df_cartridge_count = (
                df1.loc[:, columns[3] :]
                .drop(columns=[columns[3]])
                .dropna(axis=0, thresh=4)
            )
            self.data["cartridges"] = df_cartridge_count

            df4 = df4.dropna(axis="columns")
            df4.columns.values[0] = "Procedure"
            df4["Form 2"] = pd.to_datetime(df4["Form 2"])
            df4["Form 3"] = pd.to_datetime(df4["Form 3"])

            self.data["maintenance"] = df4

            for i in self.data["prints"].index:
                printer = None
                resin = None
                tank = None
                for _ in self.printers:
                    if _.name == self.data["prints"].loc[i, "Printer"]:
                        printer = _

                for _ in self.consummables:
                    if (
                        _.type == "Resin Cartridge"
                        and _.resin_type
                        == self.data["prints"].loc[i, "Resin Cartridge"]
                        and _.id == self.data["prints"].loc[i, "CartridgeID"]
                    ):
                        resin = _

                for _ in self.consummables:
                    if (
                        _.type == "Tank"
                        and _.resin_fill
                        == self.data["prints"].loc[i, "Resin Cartridge"]
                        and _.id == self.data["prints"].loc[i, "TankID"]
                        and _.resin_tank.startswith(
                            self.data["prints"].loc[i, "Printer"]
                        )
                    ):
                        tank = _

                self.prints.append(
                    Prints(
                        printer,
                        resin,
                        tank,
                        self.data["prints"].loc[i, "Date"],
                        float(self.data["prints"].loc[i, "Volume used (mL)"]),
                        self.data["prints"].loc[i, "Tank fill (~260mL)"],
                        self.data["prints"].loc[i, "Fail"],
                        self.data["prints"].loc[i, "Comment"],
                    )
                )

            logger.info("No data found, uploading data from excel sheet")

    def render_printer_section(self) -> QTabWidget:
        printer_tab = QTabWidget()
        printers_tab_content = QWidget()
        printer_tab.addTab(printers_tab_content, "Select a printer:")
        self.printer_button_group = QButtonGroup(exclusive=True)
        grid_prints = QGridLayout()

        current_dir = os.getcwd()
        dir_items = os.listdir(current_dir + "/assets/Printers/")

        counter = 0
        for item in dir_items:
            label = QLabel(item[:-4].replace("_", " "))
            _ = QCheckBox()
            _.setStyleSheet(
                """
                QCheckBox::indicator {
                    image: url(assets/Printers/"""
                + item
                + """);
                }
            """
            )
            _.toggled.connect(self.highlight_selected_printer)
            _.setToolTip(item[:-4])
            _.toggled.connect(self.update_cartridges)

            self.printer_button_group.addButton(_)
            grid_prints.addWidget(_, 0, counter)
            grid_prints.addWidget(label, 1, counter)
            counter += 1

        add_printer_button = QPushButton()
        add_printer_button.setIcon(QIcon("assets/plus-solid.svg"))
        add_printer_button.setFixedSize(QSize(40, 40))
        add_printer_button.setToolTip("Add new printer")
        add_printer_button.clicked.connect(self.save_printer)

        self.printer_button_group.addButton(add_printer_button)
        grid_prints.addWidget(add_printer_button, 0, counter)
        printers_tab_content.setLayout(grid_prints)

        if self.ui_vertical.rowCount() > 0:
            self.ui_vertical.removeRow(0)
        self.ui_vertical.insertRow(0, printer_tab)

    def render_tanks_section(self) -> QTabWidget:
        tanks_tab = QTabWidget()
        tanks_tab_content = QWidget()
        tanks_tab.addTab(tanks_tab_content, "Select a Tank:")
        self.tank_button_group = QButtonGroup(exclusive=True)

        grid_tanks = QGridLayout()

        current_dir = os.getcwd()
        dir_items = os.listdir(current_dir + "/assets/Tanks/")

        counter = 0
        for item in dir_items:
            label = QLabel(item[:-4].replace("_", " "))
            _ = QCheckBox()
            _.setStyleSheet(
                """
                QCheckBox::indicator {
                    image: url(assets/Tanks/"""
                + item
                + """);
                }
            """
            )
            _.setToolTip(item[:-4])
            _.toggled.connect(self.highlight_selected_tank)
            self.tank_button_group.addButton(_)
            grid_tanks.addWidget(label, 1, counter)
            grid_tanks.addWidget(_, 0, counter)
            counter += 1

        add_printer_button = QPushButton()
        add_printer_button.setIcon(QIcon("assets/plus-solid.svg"))
        add_printer_button.setFixedSize(QSize(40, 40))
        add_printer_button.setToolTip("Add new tank")
        add_printer_button.clicked.connect(self.save_tank)

        self.tank_button_group.addButton(add_printer_button)
        grid_tanks.addWidget(add_printer_button, 0, counter)

        self.tank_id_label = QLabel("Tank ID:")
        self.tank_id_field = QLineEdit()
        self.tank_id_combo_box = QComboBox()
        self.tank_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.data["prints"]["TankID"])))
        )
        self.tank_id_label.setBuddy(self.tank_id_combo_box)
        self.tank_id_combo_box.setLineEdit(self.tank_id_field)
        self.tank_id_combo_box.setCurrentIndex(-1)
        self.tank_id_combo_box.currentTextChanged.connect(
            lambda x: self.tank_id_combo_box.setStyleSheet("border: 0.5px solid black")
        )
        self.tank_id_field.setMaximumWidth(220)

        self.volume_used_label = QLabel("Volume used in mL:")
        self.volume_used_field = QLineEdit()
        regex_3 = QRegExp("[0-9999]+")
        validator_3 = QRegExpValidator(regex_3)
        self.volume_used_field.setValidator(validator_3)
        self.volume_used_field.textChanged.connect(
            lambda x: self.volume_used_field.setStyleSheet("border: 0.5px solid black")
        )
        self.volume_used_field.setMaximumWidth(220)

        self.tank_fill_label = QLabel("Tank fill (~260 mL):")
        self.tank_fill_field = QLineEdit()
        regex_4 = QRegExp("^[no]|^[yes]$")
        validator_4 = QRegExpValidator(regex_4)
        self.tank_fill_field.setValidator(validator_4)
        self.tank_fill_combo_box = QComboBox()
        self.tank_fill_combo_box.addItems(["no", "yes"])
        self.tank_fill_label.setBuddy(self.tank_fill_combo_box)
        self.tank_fill_combo_box.setLineEdit(self.tank_fill_field)
        self.tank_fill_combo_box.setCurrentIndex(-1)
        self.tank_fill_combo_box.currentTextChanged.connect(
            lambda x: self.tank_fill_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )
        self.tank_fill_field.setMaximumWidth(220)

        self.fail_label = QLabel("Fail:")
        self.fail_field = QLineEdit()
        self.fail_field.setValidator(validator_4)
        self.fail_combo_box = QComboBox()
        self.fail_combo_box.addItems(["no", "yes"])
        self.fail_label.setBuddy(self.fail_combo_box)
        self.fail_combo_box.setLineEdit(self.fail_field)
        self.fail_combo_box.setCurrentIndex(-1)
        self.fail_field.setMaximumWidth(220)

        self.comments_label = QLabel("Comments:")
        self.comments_field = QLineEdit()
        self.comments_field.setMaximumWidth(220)

        widgets = [
            self.tank_id_label,
            self.tank_id_combo_box,
            self.volume_used_label,
            self.volume_used_field,
            self.tank_fill_label,
            self.tank_fill_combo_box,
            self.fail_label,
            self.fail_combo_box,
            self.comments_label,
            self.comments_field,
        ]

        col = True
        counter = 0
        for widget in widgets:
            if col:
                grid_tanks.addWidget(widget, 2, counter)
                col = False
            else:
                grid_tanks.addWidget(widget, 3, counter)
                counter += 1
                col = True

        tanks_tab_content.setLayout(grid_tanks)
        self.ui_vertical.insertRow(2, tanks_tab)

    def highlight_selected_printer(self):
        printer = self.printer_button_group.button(
            self.printer_button_group.checkedId()
        ).toolTip()
        for button in self.printer_button_group.buttons():
            if button.isChecked():
                if self.preliminary_vbox.itemAtPosition(1, 1) is not None:
                    self.preliminary_vbox.removeWidget(
                        self.preliminary_vbox.itemAtPosition(1, 1).widget()
                    )
                self.preliminary_vbox.addWidget(QLabel(printer.replace("_", " ")), 1, 1)
                # print("here")
                button.setStyleSheet(
                    """QCheckBox::indicator {
                                image: url(assets/Printers/"""
                    + printer
                    + """);
                                border: 1px solid red;}
                        """
                )

            else:
                button.setStyleSheet(
                    """QCheckBox::indicator {
                            image: url(assets/Printers/"""
                    + button.toolTip()
                    + """);
                            border: 0px solid black;}"""
                )

    def save_printer(self):
        self.input_window = Printer_addition()
        self.input_window.input()
        self.input_window.show()
        logger.info("Trying to add new printer")

    def save_resin(self):
        self.input_window = Consummables_addition(self)
        self.input_window.input()
        self.input_window.show()
        logger.info("Trying to add new resin")

    def save_tank(self):
        self.input_window = Tank_addition(self)
        self.input_window.input()
        self.input_window.show()
        logger.info("Trying to add new tank")

    def save_printer_image(self):
        dir = os.getcwd()
        filename = QFileDialog.getOpenFileName(
            self, "Upload configuration", os.getcwd(),
        )

        if filename[0]:
            if filename[0].endswith(".png") or filename[0].endswith(".PNG"):
                image = Image.open(filename[0])

                image.save(
                    "".join(
                        [
                            dir,
                            f"/assets/Printers/",
                            filename[0][filename[0].rfind("/") + 1 :],
                        ]
                    ),
                    format="png",
                )
                os.mkdir(
                    "".join(
                        [
                            dir,
                            "/assets/Resins/",
                            filename[0][filename[0].rfind("/") + 1 :][:-4],
                        ]
                    )
                )
                self.render_printer_section()

            else:
                error = QErrorMessage(self)
                error.showMessage("Please upload a file with .png extension")
                logger.error(
                    f" User is uploading a file with the wrong file extension {filename[0]}"
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle Close event of the Widget."""
        pop_message = QMessageBox()
        reply = pop_message.question(
            self,
            "Confirmation step",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            0,
        )
        if reply == QMessageBox.Yes:
            event.accept()
            logger.info("The program is closed normally, saving the current data")
            self.save_config()
        else:
            event.ignore()


if __name__ == "__main__":
    logger.info("New instanciation!")
    window = QApplication([])
    loop = QEventLoop()
    asyncio.set_event_loop(loop)

    view = Tracker()
    view.show()

    for item in os.listdir(os.getcwd()):
        if "__pycache__" in item:
            shutil.rmtree(item)

    with loop:
        loop.run_forever()
