import sys
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QAction, QToolTip, QMessageBox, QCheckBox, \
                            QButtonGroup, QGroupBox, QGridLayout, QLabel, QTableWidget, QTableWidgetItem, QInputDialog, \
                            QComboBox, QLineEdit,QStyle
from PyQt5.QtGui import QIcon, QFont, QPen, QPainter, QPaintDevice
from PyQt5.QtCore import pyqtSlot, QCoreApplication, Qt
from BtceGo import *
import time


class NewApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()


    def initUI(self):
        self.left = 200
        self.top = 100
        self.width = 530
        self.height = 830
        self.ChosenPairs = {}
        self.setWindowTitle('Robot')
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowIcon(QIcon('im.png'))
        self.PA = make_PAclass()

        self.TA = make_TAclass()

        QToolTip.setFont(QFont('SansSerif', 8))
        self.make_coinPairs()
        self.make_PAmethods()

        tradeLabel = QLabel(self)
        tradeLabel.setText("Мои торги")
        tradeLabel.setGeometry(120, 155, 150, 30)
        tradeLabel.setFont(QFont("Calibri", 12))

        btnKey = QPushButton("Ввести Api key",self)
        btnKey.setGeometry(115, 190, 200, 30)
        btnKey.clicked.connect(self.btn_toChooseKye)
        btnKey = QPushButton("Ввести Secret", self)
        btnKey.setGeometry(315, 190, 200, 30)
        btnKey.clicked.connect(self.btn_toChooseSecret)

        btnAcc = QPushButton("Состояние аккаунта", self)
        btnAcc.setGeometry(115, 225, 200, 30)
        btnAcc.clicked.connect(self.btn_MyAcc)
        btnAcc.setToolTip("Информация о балансе каждой валюты и об открытых ордерах")
        self.authLabel = QLabel(self)
        self.authLabel.setGeometry(320, 225, 180, 30)
        self.authLabel.setFont(QFont("Calibri", 9))
        self.FlagAuth = 1
        logBtn = QPushButton("Login", self)
        logBtn.setGeometry(420, 160, 95, 30)
        logBtn.clicked.connect(self.CheckAuth)
        if self.CheckAuth():
            print(11)
            self.tradeHistoryShow()

        self.tradeMethod = "buy"
        self.amount = 0
        self.tradePair = list(self.ChosenPairs.keys())[0]
        self.price = 0
        comboBS = QComboBox(self)
        comboBS.addItems(["buy", "sell"])
        comboBS.setGeometry(115, 260, 95, 30)
        comboBS.activated[str].connect(self.comboBtn)
        comboCoinPairs = QComboBox(self)
        comboCoinPairs.addItems([cp for cp in self.ChosenPairs.keys()])
        comboCoinPairs.setGeometry(219, 260, 95, 30)
        comboCoinPairs.activated[str].connect(self.comboCoinPairsbtn)

        bestBuyOrder = QPushButton("Лучший ордер на покупку", self)
        bestBuyOrder.setGeometry(115, 330, 200, 30)
        bestBuyOrder.setToolTip("Ордер на покупку с ценой на 0.0001 больше, чем у активного ордера с наивысшей ценой")
        bestBuyOrder.clicked.connect(self.makeBestOrder)
        self.UpOrd = -1
        bestBuyOrderUp = QCheckBox("Обновлять ордер", self)
        bestBuyOrderUp.setGeometry(325, 330, 200, 30)
        bestBuyOrderUp.clicked.connect(self.CheckUp)

        btn_trade = QPushButton("Торговать", self)
        btn_trade.setGeometry(316, 260, 200, 30)
        btn_trade.setToolTip("Создать ордер на продажу/покупку")
        btn_trade.setFont(QFont("Calibri", 10))
        btn_trade.clicked.connect(self.GoTrading)
        amntLabel = QLabel(self)
        amntLabel.setText("Количесвто:")
        amntLabel.setGeometry(115, 295, 95, 30)
        #amntLabel.setFont(QFont("Calibri", 10))
        qleAmount = QLineEdit(self)
        qleAmount.setGeometry(219, 295, 95, 30)
        qleAmount.textChanged[str].connect(self.amntChanged)
        prcLabel = QLabel(self)
        prcLabel.setText("Цена:")
        prcLabel.setGeometry(325, 295, 95, 30)
        qlePrice = QLineEdit(self)
        qlePrice.setGeometry(420, 295, 95, 30)
        qlePrice.textChanged[str].connect(self.prcChanged)

        self.orderCncl = 0
        btnCancel = QPushButton("Отменить ордер", self)
        btnCancel.setGeometry(316, 400, 200, 30)
        btnCancel.clicked.connect(self.cancelOrder)
        btnMyActiveOrders = QPushButton("Мои активные ордера", self)
        btnMyActiveOrders.setGeometry(316, 370, 200, 30)
        btnMyActiveOrders.clicked.connect(self.getMyOrders)
        self.idOrderLabel = QLabel(self)
        self.idOrderLabel.setText("Введите id ордера:")
        self.idOrderLabel.setGeometry(115, 370, 200, 30)
        qleCancel = QLineEdit(self)
        qleCancel.setGeometry(115, 400, 199, 30)
        qleCancel.textChanged[str].connect(self.orderCnclChanged)

        sOrders = QLabel(self)
        sOrders.setText("Последние сделки аккаунта")
        sOrders.setGeometry(120, 470, 250, 30)
        sOrders.setFont(QFont("Calibri", 10))

        """self.ordersDict = [0, 0, 0, 0, 0, 0, 0, 0]
        self.ordersId = [0, 0, 0, 0, 0, 0, 0, 0]
        self.ordersPos = [120, 505, 55, 30]
        self.OrderNum = 0"""

        self.show()


    def closeEvent(self, event):
        reply1 = QMessageBox.question(self, 'Message', "Are you sure to quit?",
                 QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply1 == QMessageBox.Yes:
            self.TA.wbNonce()
            event.accept()
        else:
            event.ignore()


    def make_coinPairs(self):
        l = 20
        t = 15
        w = 80
        h = 30
        for pair in self.PA.get_Info()["pairs"].keys():
            btn = QCheckBox(pair, self)
            btn.setGeometry(l, t, w, h)
            btn.clicked.connect(self.pair_clicked)

            t += h
            self.ChosenPairs[pair] = -1


    def pair_clicked(self):
        sender = self.sender().text()
        print(sender)
        self.ChosenPairs[sender] *= -1


    def btn_toChooseKye(self):
        text, ok = QInputDialog.getText(self, "ApiKey", "EnterApiKey:")
        if ok:
            self.TA.change_key(text)
    def btn_toChooseSecret(self):
        text, ok = QInputDialog.getText(self, "Secret", "EnterSecret:")
        if ok:
            self.TA.change_secret(text)
    def comboBtn(self, text):
        self.tradeMethod = text
    def amntChanged(self, amnt):
        self.amount = amnt
    def comboCoinPairsbtn(self, text):
        self.tradePair = text
    def prcChanged(self, prc):
        self.price =prc
    def orderCnclChanged(self, order):
        self.ordrCncl = order


    def make_PAmethods(self):
        l = 115
        t = 15
        w = 200
        h = 30
        btn1 = QPushButton("Инфо", self)
        btn1.setGeometry(l, t, w, h)
        btn1.clicked.connect(self.get_MainInf)
        btn1.setToolTip("Максимально возможная цена, минимально возможно цена, минимальное количество "
                        "валюты для выставления ордера")
        t += h
        btn1 = QPushButton("Торги по выбранным паре(ам)", self)
        btn1.setGeometry(l, t, w, h)
        btn1.clicked.connect(self.get_Ticker)
        btn1.setToolTip("Объем торгов, цена покупки, продажи, средня цена за 24 часа")
        t += h
        btn1 = QPushButton("Актвные ордера пар(ы)", self)
        btn1.setGeometry(l, t, w, h)
        btn1.clicked.connect(self.getDepth)
        btn1.setToolTip("10 активных ордеров паре(ам) (продажи и покупки)")
        t += h
        btn1 = QPushButton("Последние сделки пар(ы)", self)
        btn1.setGeometry(l, t, w, h)
        t += h


    def getDepth(self):
        pairsForDepth = []
        for pair in self.ChosenPairs.keys():
            if self.ChosenPairs[pair] == 1:
                pairsForDepth.append(pair)
        limit = 10
        if pairsForDepth:
            respJson = self.PA.get_Depth(pairsForDepth, limit)
            asks = []
            bids = []
            for pair in pairsForDepth:
                for ask in respJson[pair]["asks"]:
                    asks.append((pair, ask[0], ask[1]))
                    print(ask[0])
                for bid in respJson[pair]["bids"]:
                    bids.append((pair,bid[0], bid[1]))

            self.mod = QWidget()
            self.mod.resize(920, 500)
            self.mod.setWindowTitle('Depth')
            askLabel = QLabel(self.mod)
            askLabel.setText("Продажи")
            askLabel.setFont(QFont("Calibri", 10))
            askLabel.setGeometry(15, 15, 440, 30)
            bidLabel = QLabel(self.mod)
            bidLabel.setText("Покупки")
            bidLabel.setGeometry(465, 15, 440, 30)
            bidLabel.setFont(QFont("Calibri", 10))

            tablaAsk = QTableWidget(self.mod)
            tablaAsk.setRowCount(len(pairsForDepth) * 10 + 1)
            tablaAsk.setColumnCount(3)
            tablaAsk.setGeometry(15, 45, 440, 450)
            tablaAsk.setItem(0, 0, QTableWidgetItem("Пара"))
            tablaAsk.setItem(0, 1, QTableWidgetItem("Цена"))
            tablaAsk.setItem(0, 2, QTableWidgetItem("Количество"))

            for i in range(1, len(pairsForDepth) * 10 + 1):
                for j in range(3):
                    print(asks[i - 1][j])
                    tablaAsk.setItem(i, j, QTableWidgetItem(str(asks[i - 1][j])))

            tablaBid = QTableWidget(self.mod)
            tablaBid.setRowCount(len(pairsForDepth) * 10 + 1)
            tablaBid.setColumnCount(3)
            tablaBid.setGeometry(465, 45, 440, 450)
            tablaBid.setItem(0, 0, QTableWidgetItem("Пара"))
            tablaBid.setItem(0, 1, QTableWidgetItem("Цена"))
            tablaBid.setItem(0, 2, QTableWidgetItem("Количество"))

            for i in range(1, len(pairsForDepth) * 10 + 1):
                for j in range(3):
                    tablaBid.setItem(i, j, QTableWidgetItem(str(bids[i - 1][j])))

            self.mod.show()



    def makeBestOrder(self):
        self.FlagAuth = 0
        if self.CheckAuth() == 0:
            return 0
        self.FlagAuth = 1
        resp = float(self.PA.get_Depth([self.tradePair], 10)[self.tradePair]["bids"][0][0])
        print(resp)
        minPrice = float(self.PA.get_Info()["pairs"][self.tradePair]["min_price"])
        resp += minPrice
        response = self.TA.make_Money(self.tradePair, "buy", resp, float(self.amount))
        print(response, 111)
        if response["success"] == 1:
            orderId = response["return"]["order_id"]
            while orderId != 0 and self.UpOrd:
                orderId, resp = self.UpdateOrder(orderId, resp, minPrice * 400)
                print(1111)
                time.sleep(2)


    def UpdateOrder(self, order_id, lastResp, maxPrice):
        response = self.TA.get_OrderInfo(order_id)["success"]
        if response:
            bstOrder = float(self.PA.get_Depth([self.tradePair], 10)[self.tradePair]["bids"][0][0])
            if bstOrder > maxPrice:
                return (0, 0)
            elif bstOrder > lastResp:
                bstOrder += float(self.PA.get_Info()["pairs"][self.tradePair]["min_amount"])
                rsp = self.TA.make_Money(self.tradePair, "buy", bstOrder, float(self.amount))
                return (rsp["return"]["order_id"], bstOrder)
            else:
                return (order_id, lastResp)
        else:
            return (0, 0)


    def CheckUp(self):
        self.UpOrd *= -1


    def btn_MyAcc(self):
        self.FlagAuth = 0
        if self.CheckAuth() == 0:
            return 0
        self.FlagAuth = 1
        resp = self.TA.getAccInfo()
        print(resp)
        funds = resp["return"]["funds"]
        self.modal = QWidget()
        self.modal.resize(400, 600)
        self.modal.setWindowTitle('Acc info')
        print(funds)
        print(resp["return"]["open_orders"])
        l = 45
        t = 15
        w = 160
        h = 30
        for coin in funds.keys():
            lbl1 = QLabel(self.modal)
            lbl1.setText(coin + ":")
            lbl1.setGeometry(l, t, w, h)
            lbl2 = QLabel(self.modal)
            lbl2.setText(str(funds[coin]))
            lbl2.setGeometry(l + w + 10, t, w, h)
            t += h + 5
        lbl1 = QLabel(self.modal)
        lbl1.setText("Активных ордеров:")
        lbl1.setGeometry(l, t, w, h)
        lbl2 = QLabel(self.modal)
        lbl2.setText(str(resp["return"]["open_orders"]))
        lbl2.setGeometry(l + w + 10, t, w, h)

        print(funds)
        print(resp["return"]["open_orders"])

        self.modal.show()


    def getMyOrders(self):
        self.FlagAuth = 0
        if self.CheckAuth() == 0:
            return 0
        self.FlagAuth = 1
        response = self.TA.get_ActiveOrders(self.tradePair)
        self.modalW = QWidget()
        self.modalW.resize(550, 500)
        self.modalW.setWindowTitle('My active orders')
        if response["success"] == 0:
            ordLab = QLabel(self.modalW)
            ordLab.setText("У вас нет активных ордеров")
            ordLab.setFont(QFont("Calibri", 12))
            ordLab.setGeometry(30, 30, 400, 30)
        else:
            tableOrd = QTableWidget()
            ordersInf = []
            retOrders = response["return"]
            for order in retOrders.keys():
                ordersInf.append((order, retOrders["pair"], retOrders["type"], retOrders["amount"], retOrders["rate"]))
            tableOrd.setColumnCount(5)
            tableOrd.setRowCount(len(retOrders.keys()))
            for i in range(len(retOrders.keys())):
                for j in range(5):
                    tableOrd.setItem(i, j, QTableWidgetItem(ordersInf[i][j]))
            tableOrd.setGeometry(15, 15, 500, 400)
        self.modalW.show()


    def get_MainInf(self):
        infjs = self.PA.get_Info()["pairs"]
        inf = []
        for pair in infjs.keys():
            if self.ChosenPairs[pair] == 1:
                inf.append((pair, str(infjs[pair]["max_price"]), str(infjs[pair]["min_price"]), str(infjs[pair]["min_amount"])))

        self.modal = QWidget()
        self.modal.resize(600, 400)
        self.modal.setWindowTitle('Main info')
        l = 115
        t = 15
        w = 160
        h = 30
        ql = QLabel(self.modal)
        ql.setText("Максимальная цена")
        ql.setGeometry(l, t, w, h)
        l += w
        ql = QLabel(self.modal)
        ql.setText("Минимальная цена")
        ql.setGeometry(l, t, w, h)
        l += w
        ql = QLabel(self.modal)
        ql.setText("Минимальное количество")
        ql.setGeometry(l, t, w, h)
        l += w
        l = 30
        t = 45
        w = 70
        h = 30
        for p in inf:
            c = 0
            while c < 4:
                ql = QLabel(self.modal)
                ql.setText(p[c])
                ql.setGeometry(l, t, w, h)
                l += 160
                c += 1
            t += 30
            l = 30

        self.modal.show()


    def get_Ticker(self):
        pairsForTicker = []
        for pair in self.ChosenPairs.keys():
            if self.ChosenPairs[pair] == 1:
                pairsForTicker.append(pair)
        if pairsForTicker:
            infjs = self.PA.get_Ticker(pairsForTicker)
            inf = []
            for pair in infjs.keys():
                inf.append(pair)
                inf.append(str(infjs[pair]["vol"]))
                inf.append(str(infjs[pair]["buy"]))
                inf.append(str(infjs[pair]["sell"]))
                inf.append(str(infjs[pair]["avg"]))

            self.modal = QWidget()
            self.modal.resize(750, 480)
            self.modal.setWindowTitle('Ticker')
            self.tableWidget = QTableWidget(self.modal)
            self.tableWidget.setRowCount(len(infjs.keys()) + 1)
            self.tableWidget.setColumnCount(5)

            self.tableWidget.setItem(0, 0, QTableWidgetItem("Валюты"))
            self.tableWidget.setItem(0, 1, QTableWidgetItem("Объем торгов"))
            self.tableWidget.setItem(0, 2, QTableWidgetItem("Цена покупки"))
            self.tableWidget.setItem(0, 3, QTableWidgetItem("Цена продажи"))
            self.tableWidget.setItem(0, 4, QTableWidgetItem("Средняя цена за 24 часа"))
            positions = [(i, j) for i in range(1, len(infjs.keys()) + 1) for j in range(5)]
            for it, position in zip(inf, positions):
                print(position)
                self.tableWidget.setItem(position[0], position[1], QTableWidgetItem(it))

            self.tableWidget.move(15, 15)
            self.tableWidget.resize(5 * 133, (len(infjs.keys()) + 2) * 50)
            self.modal.show()


    def GoTrading(self):
        self.FlagAuth = 0
        if self.CheckAuth() == 0:
            return 0
        self.FlagAuth = 1
        response = self.TA.make_Money(self.tradePair, self.tradeMethod, float(self.price), float(self.amount))
        print(response)


    def cancelOrder(self):
        self.FlagAuth = 0
        if self.CheckAuth() == 0:
            return 0
        self.FlagAuth = 1
        try:
            order_id = int(self.ordrCncl)
            response = self.TA.cancelOrder(order_id)
            if response["success"] == 1:
                self.idOrderLabel.setText("Введите id ордера")
                print(response)
            else:
                self.idOrderLabel.setText("Введите корректный id ордера")
        except:
            self.idOrderLabel.setText("Введите корректный id ордера")


    def makeRecentOrders(self, data):
        if data["success"] == 0:
            pass
        else:
            pass


    def CheckAuth(self):
        if self.TA.get_Key() == "" or self.TA.get_Secret() == "":
            self.authLabel.setText("Not Authenticated")
            return 0
        elif len(self.TA.get_Secret()) != 64 or len(self.TA.get_Key()) != 44 or ("-" not in self.TA.get_Key()):
            self.authLabel.setText("Not Authenticated")
            return 0
        else:
            if self.FlagAuth:
                self.tradeHistoryShow()
            self.authLabel.setText("Authenticated")
            return 1


    def tradeHistoryShow(self):
        left, top = 120, 505
        tLabel = QLabel(self)
        tLabel.setGeometry(left, top, 400, 30)
        tLabel.setText("{}  {}   {}   {}   {}".format("id ордера  ", "Тип  ", "Пара    ", "Цена       ", "Количество"))
        tLabel.setFont(QFont("Calibri", 9))
        tLabel.setVisible(1)
        top += 40
        response = self.TA.get_TradeHistory(count=8)
        if response["success"]:
            trades = response["return"]
            for trade in trades.keys():
                tLabel = QLabel(self)
                tLabel.setGeometry(left, top, 400, 30)
                tLabel.setText("{}  {}   {}   {}   {}".format(trades[trade]["order_id"], trades[trade]["type"], \
                                                              trades[trade]["pair"], trades[trade]["rate"], \
                                                              trades[trade]["amount"],))
                tLabel.setVisible(1)
                top += 35


    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawLines(qp)
        qp.end()


    def drawLines(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)

        qp.setPen(pen)
        qp.drawLine(115, 145, 515, 145)
        qp.drawLine(115, 460, 515, 460)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    ex = NewApp()
    sys.exit(app.exec_())

