from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QComboBox,
)
from datetime import datetime
from PyQt5.QtGui import QIcon


class Printer_addition(QMainWindow):
    def __init__(self):
        super().__init__()
        # self.parent = main

    def input(self):
        self.setWindowTitle("Addition of new printer")
        main_layout = QWidget()
        # tab = QWidget()
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

        # main_layout.addTab(tab, "test")
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
        # self.cartridge_id_resins_field.setValidator(validator_2)
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
        # self.version_resins_field.setValidator(validator_1)
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
        # self.batch_date_resins_field.setValidator(validator)
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
        main_layout.setLayout(grid_resins)

        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 350)
        self.move(600, 350)


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
        # self.tanks_id_field.setValidator(validator_2)
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
        # self.version_tanks_field.setValidator(validator_1)
        self.version_tanks_combo_box.setLineEdit(self.version_tanks_field)
        self.version_tanks_label.setBuddy(self.version_tanks_combo_box)
        self.version_tanks_field.setMaximumWidth(220)

        self.tanks_total_volume_label = QLabel("Total print volume (mL):")
        self.tanks_total_volume_field = QLineEdit()
        self.tanks_total_volume_field.setMaximumWidth(220)
        # self.tanks_total_volume_field.setValidator(validator_3)

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
        # self.tanks_opened_date_field.setValidator(validator)
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
        grid_tanks.addWidget(printers_add, 10, 0)
        main_layout.setLayout(grid_tanks)

        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 350)
        self.move(600, 350)


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

        self.resin_tank = tank.resin_tank
        self.tank_id = tank.id
        self.volume = volume
        self.tank_fill = tank_fill
        self.fail = fail
        self.comments = comments

    def can_consume(self, resin: Consummables, tank: Consummables):
        if resin.resin_type != tank.resin_fill:
            return False

        else:
            return True
