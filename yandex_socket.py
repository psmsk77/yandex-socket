"""Программа для работы с API Яндекс IOT (Яндекс Розетка) на основе класса"""
import os
import sys
import json
import requests
from time import time
import threading
from PyQt5 import QtWidgets, uic

yandex_oauth = os.getenv('YANDEX_OAUTH')
yandex_device_id = os.getenv('SOCKET_ID')
head = json.loads('{"Authorization": "Bearer ' + yandex_oauth + '", "Content-Type": "application/json"}')


class MainWindow(QtWidgets.QMainWindow):
    """Главное окно программы"""

    def __init__(self, design, title):
        super(MainWindow, self).__init__()
        uic.loadUi(design, self)
        self.setWindowTitle(title)
        self.onButton.clicked.connect(self.on_socket)
        self.offButton.clicked.connect(self.off_socket)
        # self.show()

    def on_socket(self):
        """Включить розетку"""
        data_json = json.loads(
            '{"devices": [{"id": "' + yandex_device_id + '", '
            '"actions": [{"type": "devices.capabilities.on_off","state": {"instance": "on","value": true}}]}]}')
        response = requests.post("https://api.iot.yandex.net/v1.0/devices/actions", headers=head, json=data_json).json()

        # print(response["devices"][0]["capabilities"][0]["state"]["action_result"]["status"])
        # print(response["devices"][0]["capabilities"][0]["state"]["action_result"]["error_code"])
        # print(response["devices"][0]["capabilities"][0]["state"]["action_result"]["error_message"])

        if response["devices"][0]["capabilities"][0]["state"]["action_result"]["status"] == "DONE":
            self.statusLabel.setText('Розетка успешно включена')
            print("Розетка успешно включена")
        elif response["devices"][0]["capabilities"][0]["state"]["action_result"]["error_code"] == "DEVICE_UNREACHABLE":
            self.statusLabel.setText('Розетка недоступна')
            print("Розетка недоступна")
            print(response["devices"][0]["capabilities"][0]["state"]["action_result"])
        else:
            print("Неизвестная ошибка")
            print(response["devices"][0]["capabilities"][0]["state"]["action_result"])

    def off_socket(self):
        """Выключить розетку"""
        data_json = json.loads(
            '{"devices": [{"id": "' + yandex_device_id + '",'
            '"actions": [{"type": "devices.capabilities.on_off", "state": {"instance": "on","value": false}}]}]}')
        response = requests.post("https://api.iot.yandex.net/v1.0/devices/actions", headers=head, json=data_json).json()

        if response["devices"][0]["capabilities"][0]["state"]["action_result"]["status"] == "DONE":
            self.statusLabel.setText('Розетка выключена')
            print("Розетка выключена")
        elif response["devices"][0]["capabilities"][0]["state"]["action_result"]["error_code"] == "DEVICE_UNREACHABLE":
            self.statusLabel.setText('Розетка недоступна')
            print("Розетка недоступна")
            print(response["devices"][0]["capabilities"][0]["state"]["action_result"])
        else:
            print("Неизвестная ошибка")
            print(response["devices"][0]["capabilities"][0]["state"]["action_result"])

    def get_data(self):
        """Обновить данные (свойства)"""
        data = requests.get(f"https://api.iot.yandex.net/v1.0/devices/{yandex_device_id}", headers=head).json()
        voltage = int(data['properties'][0]['state']['value'])
        power = data['properties'][1]['state']['value']
        amperage = data['properties'][2]['state']['value']

        print(data)
        print(f'Device_Status: {data["state"]}, Voltage: {voltage} V, Power: {power} W, Amperage: {amperage} A')

        # Отображение значений на дисплеях
        if data["state"] == "online":
            self.lcdVoltage.display(voltage)
            self.lcdPower.display(power)
            self.lcdAmperage.display(amperage)
            self.statusLabel.setText('Статус: ONLINE')
        elif data["state"] == "offline":
            self.lcdVoltage.display(0)
            self.lcdPower.display(0)
            self.lcdAmperage.display(0)
            self.statusLabel.setText('Статус: OFFLINE')
        else:
            print("Неизвестная ошибка!")

    def checking(self, last_check=0, period=10):
        """Периодичность обновления данных"""
        while True:
            if last_check + period < time():
                self.get_data()
                last_check = time()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow('design.ui', 'Яндекс Розетка')
    window.show()
    threading.Thread(target=window.checking, daemon=True).start()
    sys.exit(app.exec_())
