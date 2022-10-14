from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QGridLayout,
    QErrorMessage,
    QComboBox,
)
from datetime import datetime, timedelta
from PyQt5.QtGui import QIcon, QRegExpValidator
from PyQt5.QtCore import QRegExp

import numpy as np

regex = QRegExp(
    "^([0-9][0-9]|19[0-9][0-9]|20[0-9][0-9])(\/|/)([1-9]|0[1-9]|1[0-2])(\:|/)([1-9]|0[1-9]|1[0-9]|2[0-9]|3[0-1])$"
)
validator = QRegExpValidator(regex)

regex_1 = QRegExp("[0-9]+")
validator_1 = QRegExpValidator(regex_1)

regex_2 = QRegExp("[0-999]+")
validator_2 = QRegExpValidator(regex_2)

regex_3 = QRegExp("[0-9999]+")
validator_3 = QRegExpValidator(regex_3)


class Printer_addition(QMainWindow):
    def __init__(self):
        super().__init__()

    def input(self):
        self.setWindowTitle("Addition of new printer")
        main_layout = QWidget()

        vbox = QVBoxLayout()
        self.printer_name = QLabel("Printer's name:")
        self.printer_field = QLineEdit()

        self.printer_resin_label = QLabel("Printer's type:")
        self.printer_resin_field = QLineEdit()

        self.printer_tank_label = QLabel("Printer's company:")
        self.printer_tank_field = QLineEdit()

        vbox.addWidget(self.printer_name)
        vbox.addWidget(self.printer_field)
        vbox.addWidget(self.printer_resin_label)
        vbox.addWidget(self.printer_resin_field)
        vbox.addWidget(self.printer_tank_label)
        vbox.addWidget(self.printer_tank_field)

        printers_add = QPushButton()
        printers_add.setIcon(QIcon("assets/plus-solid.svg"))
        printers_add.setToolTip("Append printer to configuration")
        vbox.addWidget(printers_add)
        main_layout.setLayout(vbox)

        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 350)
        self.move(600, 350)


class Consummables_addition(QMainWindow):
    def __init__(self, main):
        super().__init__()
        self.parent = main

    def input(self):
        self.setWindowTitle("Addition of new resin")
        main_layout = QWidget()
        grid_resins = QGridLayout()

        self.cartridge_id_resins_label = QLabel("Cartridge ID:")
        self.cartridge_id_resins_field = QLineEdit()
        self.cartridge_id_resins_field.setValidator(validator_2)
        self.cartridge_id_resins_combo_box = QComboBox()
        self.cartridge_id_resins_combo_box.addItems(
            list(
                map(lambda x: str(x), set(self.parent.data["resins"]["CartridgeID.1"]))
            )
        )
        self.cartridge_id_resins_combo_box.setCurrentIndex(-1)
        self.cartridge_id_resins_label.setBuddy(self.cartridge_id_resins_combo_box)
        self.cartridge_id_resins_combo_box.setLineEdit(self.cartridge_id_resins_field)
        self.cartridge_id_resins_combo_box.currentTextChanged.connect(
            lambda x: self.cartridge_id_resins_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )

        self.resin_type_resins_label = QLabel("Resin type:")
        self.resin_type_resins_field = QLineEdit()
        self.resin_type_resins_combo_box = QComboBox()
        self.resin_type_resins_combo_box.addItems(
            list(
                map(
                    lambda x: str(x),
                    set(self.parent.data["resins"]["Resin Cartridge.1"]),
                )
            )
        )
        self.resin_type_resins_combo_box.setCurrentIndex(-1)
        self.resin_type_resins_label.setBuddy(self.resin_type_resins_combo_box)
        self.resin_type_resins_combo_box.setLineEdit(self.resin_type_resins_field)
        self.resin_type_resins_combo_box.currentTextChanged.connect(
            lambda x: self.resin_type_resins_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )

        self.version_resins_label = QLabel("Version:")
        self.version_resins_combo_box = QComboBox()
        self.version_resins_combo_box.addItems(
            list(map(lambda x: str(x), set(self.parent.data["resins"]["Version.1"])))
        )
        self.version_resins_combo_box.setCurrentIndex(-1)
        self.version_resins_field = QLineEdit()
        self.version_resins_field.setValidator(validator_1)
        self.version_resins_combo_box.setLineEdit(self.version_resins_field)
        self.version_resins_label.setBuddy(self.version_resins_combo_box)
        self.version_resins_combo_box.currentTextChanged.connect(
            lambda x: self.version_resins_combo_box.setStyleSheet(
                "border: 0.5px solid black"
            )
        )

        self.batch_date_resins_label = QLabel("Batch date (YYYY/MM/DD):")
        self.batch_date_resins_field = QLineEdit()
        self.batch_date_resins_field.setText(datetime.now().strftime("%Y/%m/%d"))
        self.batch_date_resins_field.setValidator(validator)
        self.batch_date_resins_field.textChanged.connect(
            lambda x: self.batch_date_resins_field.setStyleSheet(
                "border: 0.5px solid black"
            )
        )

        self.resins_company_label = QLabel("Company:")
        self.resins_company_field = QLineEdit()
        self.resins_company_combo_box = QComboBox()
        self.resins_company_combo_box.addItems(["FormLabs", "CadWorks"])
        self.resins_company_combo_box.setCurrentIndex(-1)
        self.resins_company_label.setBuddy(self.resins_company_combo_box)
        self.resins_company_combo_box.setLineEdit(self.resins_company_field)

        self.comments_resins_label = QLabel("Comments:")
        self.comments_resins_field = QLineEdit()

        self.printer_name = QLabel("Resin's name:")
        self.printer_field = QLineEdit()

        self.printer_resin_label = QLabel("Resin's type:")
        self.printer_resin_field = QLineEdit()

        self.printer_tank_label = QLabel("Resin's company:")
        self.printer_tank_field = QLineEdit()

        grid_resins.addWidget(self.cartridge_id_resins_label, 0, 0)
        grid_resins.addWidget(self.cartridge_id_resins_combo_box, 1, 0)
        grid_resins.addWidget(self.resin_type_resins_label, 0, 1)
        grid_resins.addWidget(self.resin_type_resins_combo_box, 1, 1)
        grid_resins.addWidget(self.version_resins_label, 2, 0)
        grid_resins.addWidget(self.version_resins_combo_box, 3, 0)
        grid_resins.addWidget(self.batch_date_resins_label, 2, 1)
        grid_resins.addWidget(self.batch_date_resins_field, 3, 1)
        grid_resins.addWidget(self.comments_resins_label, 4, 0)
        grid_resins.addWidget(self.comments_resins_field, 5, 0)
        grid_resins.addWidget(self.resins_company_label, 4, 1)
        grid_resins.addWidget(self.resins_company_combo_box, 5, 1)

        printers_add = QPushButton()
        printers_add.setIcon(QIcon("assets/plus-solid.svg"))
        printers_add.setToolTip("Append resin to configuration")
        grid_resins.addWidget(printers_add)
        printers_add.clicked.connect(self.append_resin)
        main_layout.setLayout(grid_resins)

        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 350)
        self.move(600, 350)

    def append_resin(self):
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

        if valid:
            try:
                self.parent.data["resins"]["CartridgeID.1"] = self.parent.data[
                    "resins"
                ]["CartridgeID.1"].astype(float)
                i = self.parent.data["resins"].loc[
                    (
                        self.parent.data["resins"]["CartridgeID.1"]
                        == float(self.cartridge_id_resins_combo_box.currentText())
                    )
                    & (
                        self.parent.data["resins"]["Resin Cartridge.1"]
                        == self.resin_type_resins_combo_box.currentText()
                    )
                ]

                if isinstance(i.index[0], np.int64):
                    self.cartridge_id_resins_combo_box.setStyleSheet(
                        "border: 1px solid red"
                    )
                    self.resin_type_resins_combo_box.setStyleSheet(
                        "border: 1px solid red"
                    )
                    valid = False
                    id = self.parent.data["cartridges"]["Next Cartridge ID"].loc[
                        self.parent.data["cartridges"]["Cartridge"]
                        == self.resin_type_resins_combo_box.currentText()
                    ]

                    error = QErrorMessage(self)
                    error.showMessage(
                        f"Cartridge already in use, please choose the next ID available {id[id.index[0]]}"
                    )
            except:
                if valid:
                    data = {}
                    data["CartridgeID.1"] = float(
                        self.cartridge_id_resins_combo_box.currentText()
                    )
                    data[
                        "Resin Cartridge.1"
                    ] = self.resin_type_resins_combo_box.currentText()
                    data["Version"] = self.version_resins_combo_box.currentText()
                    data["Batch Date"] = self.batch_date_resins_field.text()
                    data["Company"] = self.resins_company_combo_box.currentText()
                    self.parent.append_to_resins_df(data, comments)
                    self.close()


class Tank_addition(QMainWindow):
    def __init__(self, main):
        super().__init__()
        self.parent = main

    def input(self):
        self.setWindowTitle("Addition of new tank")
        main_layout = QWidget()
        grid_tanks = QGridLayout()

        self.tanks_id_label = QLabel("Tank ID:")
        self.tanks_id_combo_box = QComboBox()
        self.tanks_id_combo_box.addItems(
            list(map(lambda x: str(x), set(self.parent.data["tanks"]["TankID.1"])))
        )
        self.tanks_id_combo_box.setCurrentIndex(-1)
        self.tanks_id_field = QLineEdit()
        self.tanks_id_field.setValidator(validator_2)
        self.tanks_id_label.setBuddy(self.tanks_id_combo_box)
        self.tanks_id_combo_box.setLineEdit(self.tanks_id_field)
        self.tanks_id_field.setMaximumWidth(220)

        self.tanks_resin_label = QLabel("Resin Tank:")
        self.tanks_resin_field = QLineEdit()
        self.tanks_resin_combo_box = QComboBox()
        self.tanks_resin_combo_box.addItems(
            list(map(lambda x: str(x), set(self.parent.data["tanks"]["Resin Tank.1"])))
        )
        self.tanks_resin_combo_box.setCurrentIndex(-1)
        self.tanks_resin_label.setBuddy(self.tanks_resin_combo_box)
        self.tanks_resin_combo_box.setLineEdit(self.tanks_resin_field)
        self.tanks_resin_field.setMaximumWidth(220)

        self.tanks_resin_fill_label = QLabel("Resin fill:")
        self.tanks_resin_fill_field = QLineEdit()
        self.tanks_resin_fill_combo_box = QComboBox()
        self.tanks_resin_fill_combo_box.addItems(
            list(map(lambda x: str(x), set(self.parent.data["tanks"]["Resin Fill"])))
        )
        self.tanks_resin_fill_combo_box.setCurrentIndex(-1)
        self.tanks_resin_fill_label.setBuddy(self.tanks_resin_fill_combo_box)
        self.tanks_resin_fill_combo_box.setLineEdit(self.tanks_resin_fill_field)
        self.tanks_resin_fill_field.setMaximumWidth(220)

        self.version_tanks_label = QLabel("Version:")
        self.version_tanks_combo_box = QComboBox()
        self.version_tanks_combo_box.addItems(
            list(map(lambda x: str(x), set(self.parent.data["tanks"]["Version.2"])))
        )
        self.version_tanks_combo_box.setCurrentIndex(-1)
        self.version_tanks_field = QLineEdit()
        self.version_tanks_field.setValidator(validator_1)
        self.version_tanks_combo_box.setLineEdit(self.version_tanks_field)
        self.version_tanks_label.setBuddy(self.version_tanks_combo_box)
        self.version_tanks_field.setMaximumWidth(220)

        self.tanks_total_volume_label = QLabel("Total print volume (mL):")
        self.tanks_total_volume_field = QLineEdit()
        self.tanks_total_volume_field.setMaximumWidth(220)
        self.tanks_total_volume_field.setValidator(validator_3)

        self.tanks_status_label = QLabel("Status:")
        self.tanks_status_field = QLineEdit()
        self.tanks_status_combo_box = QComboBox()
        self.tanks_status_combo_box.addItems(set(self.parent.data["tanks"]["Status.1"]))
        self.tanks_status_combo_box.setCurrentIndex(-1)
        self.tanks_status_label.setBuddy(self.tanks_status_combo_box)
        self.tanks_status_combo_box.setLineEdit(self.tanks_status_field)
        self.tanks_status_field.setMaximumWidth(220)

        self.tanks_company_label = QLabel("Company:")
        self.tanks_company_field = QLineEdit()
        self.tanks_company_combo_box = QComboBox()
        self.tanks_company_combo_box.addItems(["FormLabs", "CadWorks"])
        self.tanks_company_combo_box.setCurrentIndex(-1)
        self.tanks_company_label.setBuddy(self.tanks_company_combo_box)
        self.tanks_company_combo_box.setLineEdit(self.tanks_company_field)
        self.tanks_company_field.setMaximumWidth(220)

        self.tanks_opened_date_label = QLabel("Opened date:")
        self.tanks_opened_date_field = QLineEdit()
        self.tanks_opened_date_field.setText(datetime.now().strftime("%Y/%m/%d"))
        self.tanks_opened_date_field.setValidator(validator)
        self.tanks_opened_date_field.setMaximumWidth(220)

        self.tanks_comments_label = QLabel("Comments:")
        self.tanks_comments_field = QLineEdit()
        self.tanks_comments_field.setMaximumWidth(220)

        grid_tanks.addWidget(self.tanks_id_label, 0, 0)
        grid_tanks.addWidget(self.tanks_id_combo_box, 1, 0)
        grid_tanks.addWidget(self.tanks_resin_label, 0, 1)
        grid_tanks.addWidget(self.tanks_resin_combo_box, 1, 1)
        grid_tanks.addWidget(self.tanks_resin_fill_label, 2, 0)
        grid_tanks.addWidget(self.tanks_resin_fill_combo_box, 3, 0)
        grid_tanks.addWidget(self.version_tanks_label, 2, 1)
        grid_tanks.addWidget(self.version_tanks_combo_box, 3, 1)
        grid_tanks.addWidget(self.tanks_total_volume_label, 4, 0)
        grid_tanks.addWidget(self.tanks_total_volume_field, 5, 0)
        grid_tanks.addWidget(self.tanks_status_label, 4, 1)
        grid_tanks.addWidget(self.tanks_status_combo_box, 5, 1)
        grid_tanks.addWidget(self.tanks_opened_date_label, 6, 0)
        grid_tanks.addWidget(self.tanks_opened_date_field, 7, 0)
        grid_tanks.addWidget(self.tanks_company_label, 6, 1)
        grid_tanks.addWidget(self.tanks_company_combo_box, 7, 1)
        grid_tanks.addWidget(self.tanks_comments_label, 8, 0)
        grid_tanks.addWidget(self.tanks_comments_field, 9, 0)

        printers_add = QPushButton()
        printers_add.setIcon(QIcon("assets/plus-solid.svg"))
        printers_add.setToolTip("Append tank to configuration")
        printers_add.clicked.connect(self.add_tank)
        grid_tanks.addWidget(printers_add, 10, 0)
        main_layout.setLayout(grid_tanks)

        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 350)
        self.move(600, 350)

    def add_tank(self):
        valid = True
        if self.tanks_id_combo_box.currentText() == "":
            self.tanks_id_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.tanks_resin_combo_box.currentText() == "":
            self.tanks_resin_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.tanks_resin_fill_combo_box.currentText() == "":
            self.version_resins_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.version_tanks_combo_box.currentText() == "":
            self.version_tanks_combo_box.setStyleSheet("border: 1px solid red")
            valid = False
        if self.tanks_total_volume_field.text() == "":
            self.tanks_total_volume_field.setStyleSheet("border: 1px solid red")
            valid = False
        if self.tanks_status_combo_box.currentText() == "":
            self.tanks_status_combo_box.setStyleSheet("border: 1px solid red")
            valid = False

        if self.tanks_company_combo_box.currentText() == "":
            self.tanks_company_combo_box.setStyleSheet("border: 1px solid red")
            valid = False

        if self.tanks_opened_date_field.text() == "":
            self.tanks_opened_date_field.setStyleSheet("border: 1px solid red")
            valid = False

        if self.tanks_comments_field.text() == "":
            comments = "nan"
        else:
            comments = self.comments_resins_field.text()

        try:
            self.parent.data["tanks"]["TankID.1"] = self.parent.data["tanks"][
                "TankID.1"
            ].astype(float)
            i = self.parent.data["tanks"].loc[
                (
                    self.parent.data["tanks"]["TankID.1"]
                    == float(self.tanks_id_combo_box.currentText())
                )
                & (
                    self.parent.data["tanks"]["Resin Fill"]
                    == self.tanks_resin_fill_combo_box.currentText()
                )
            ]

            if i.shape[0] == 0:
                raise IndexError

            if isinstance(i.index[0], np.int64):
                self.tanks_id_combo_box.setStyleSheet("border: 1px solid red")
                self.tanks_resin_fill_combo_box.setStyleSheet("border: 1px solid red")
                valid = False
                id = self.parent.data["cartridges"]["Next Tank ID"].loc[
                    self.parent.data["cartridges"]["Cartridge"]
                    == self.tanks_resin_fill_combo_box.currentText()
                ]

                error = QErrorMessage(self)
                error.showMessage(
                    f"Tank already in use, please choose the next ID available {id[id.index[0]]}"
                )
                # logger.info("User is selecting an already taken Tank ID")
        except IndexError:
            if valid:
                data = {}
                data["TankID.1"] = float(self.tanks_id_combo_box.currentText())
                data["Resin"] = self.tanks_resin_combo_box.currentText()
                data["Resin Fill"] = self.tanks_resin_fill_combo_box.currentText()
                data["Version"] = self.version_tanks_combo_box.currentText()
                data["Total Volume"] = float(self.tanks_total_volume_field.text())
                data["Status"] = self.tanks_status_combo_box.currentText()
                data["Opened Date"] = self.tanks_opened_date_field.text()
                data["Company"] = self.tanks_company_combo_box.currentText()

                self.tanks_id_combo_box.setStyleSheet("border: 1px solid black")
                self.tanks_resin_fill_combo_box.setStyleSheet("border: 1px solid black")
                self.parent.append_to_tanks_df(data, comments)
                # logger.info("New tank entered, updating Tanks/Labelling tables")
                self.close()


class Consummables:
    def __init__(self, type: str, company: str) -> None:
        self.company = company
        self.type = type

    def requierment_per_type(self, requierments: dict) -> None:
        if isinstance(requierments, list):
            requierments = requierments[0]

        if self.type == "Resin Cartridge":
            self.resin_type = requierments["Resin Cartridge.1"]
            self.id = requierments["CartridgeID.1"]
            self.status = requierments["Status"]
            self.total_print = requierments["Total print volume (mL)"]
            self.version = requierments["Version.1"]
            self.batch_date = requierments["Batch date"]
            self.comments = requierments["Comments"]

        elif self.type == "Tank":
            self.id = requierments["TankID.1"]
            self.resin_tank = requierments["Resin Tank.1"]
            self.resin_fill = requierments["Resin Fill"]
            self.version = requierments["Version.2"]
            self.total_print = requierments["Total print volume (mL).1"]
            self.status = requierments["Status.1"]
            self.opened_date = requierments["Opened date"]
            self.comments = requierments["Comments.1"]


class Printer:
    def __init__(self, name: str, type: str, company: str) -> None:
        self.name = name
        self.type = type
        self.company = company

    def can_consume(self, consummable: Consummables) -> bool:
        # print("here 1")
        if consummable.company == self.company:
            return True
        else:
            return False


class Prints:
    def __init__(
        self,
        printer: Printer,
        cartridge: Consummables,
        tank: Consummables,
        date: str,
        volume: float,
        tank_fill,
        fail,
        comments: str,
    ) -> None:
        self.printer = printer.name
        self.date = date
        self.resin_type = cartridge.resin_type
        self.resin_version = cartridge.version
        self.cartridge_id = cartridge.id

        # print(date)
        self.resin_tank = tank.resin_tank
        self.tank_id = tank.id
        self.volume = volume
        self.tank_fill = tank_fill
        self.fail = fail
        self.comments = comments

    def can_consume(self, resin: Consummables, tank: Consummables):
        # print("here 2")
        # print(resin.resin_type, tank.resin_fill)
        if resin.resin_type != tank.resin_fill:
            return False

        else:
            return True
