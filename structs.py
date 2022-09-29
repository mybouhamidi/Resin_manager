from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QLineEdit,
    QPushButton,
    QWidget,
    QVBoxLayout,
    QLabel,
    QGridLayout,
)

from PyQt5.QtGui import QIcon


class Printer_addition(QMainWindow):
    def __init__(self, main):
        super().__init__()
        self.parent = main

    def input(self):
        self.setWindowTitle("Addition of new printer")
        main_layout = QTabWidget()
        tab = QWidget()
        tab.layout = QVBoxLayout()
        self.printer_name = QLabel("Printer's name:")
        self.printer_field = QLineEdit()

        self.printer_resin_label = QLabel("Printer's type:")
        self.printer_resin_field = QLineEdit()

        self.printer_tank_label = QLabel("Printer's company:")
        self.printer_tank_field = QLineEdit()

        tab.layout.addWidget(self.printer_name)
        tab.layout.addWidget(self.printer_field)
        tab.layout.addWidget(self.printer_resin_label)
        tab.layout.addWidget(self.printer_resin_field)
        tab.layout.addWidget(self.printer_tank_label)
        tab.layout.addWidget(self.printer_tank_field)

        printers_add = QPushButton()
        printers_add.setIcon(QIcon("assets/plus-solid.svg"))
        printers_add.setToolTip("Append printer to configuration")
        tab.layout.addWidget(printers_add)
        tab.setLayout(tab.layout)

        # printers_add.clicked.connect(self.closing)
        # tab.setLayout(grid_printers)
        # self.main_layout.addTab(tab, "Test")
        # vbox.addLayout(grid_printers)
        main_layout.addTab(tab, "test")
        self.setCentralWidget(main_layout)
        self.setFixedSize(600, 220)
        self.move(600, 350)
        self.show()

    # def closing(self):
    #     self.close()
    #     self.parent().save_printer_image()


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
