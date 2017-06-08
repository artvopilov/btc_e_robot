import requests
import hmac
import http.client
import json
import urllib.parse
import hashlib
import requests


url = "https://btc-e.com/api/3"
proxies = {
    "http": "http://163.172.59.4:8080",
    "https": 'https://187.44.14.19:8080',
}
proxy_HTTPS = proxies["https"].split(":")[1][2:]
proxy_HTTPS_port = proxies["https"].split(":")[2]

BTC_key = ""
BTC_secret = ""

http_timeout = 15
filer = open("nonce.txt", 'r')
nonce = int(filer.read())
filer.close()


class Trade_Api():
    def __init__(self, key, secret, nonce, proxy_https, proxy_https_port):
        self.__btcKey = key
        self.__btcSecret = secret
        self.__nonce = nonce
        self.__proxy = proxy_https
        self.__port = proxy_https_port


    def get_Key(self):
        return self.__btcKey


    def get_Secret(self):
        return self.__btcSecret


    def signiture(self, params):
        sign = hmac.new(self.__btcSecret.encode(), params.encode(), hashlib.sha512)
        return sign.hexdigest()


    def _call_to_api(self, method, params):
        try:
            params["method"] = method
            params["nonce"] = self.__nonce
            params = urllib.parse.urlencode(params)
            headers = {'Content-type': 'application/x-www-form-urlencoded', 'Key': self.__btcKey,
                       'Sign': self.signiture(params)}
            conn = http.client.HTTPSConnection(self.__proxy, int(self.__port), timeout=http_timeout)
            conn.set_tunnel('btc-e.com')
            conn.request('POST', '/tapi', params, headers)
            response = conn.getresponse().read().decode()
            data = json.loads(response)
            conn.close()

            self.__nonce += 1
            return data
        except ConnectionError:
            print("Connection error")


    """Возвращает информацию о текущем балансе пользователя, привилегиях API-ключа, количество открытых ордеров
     и время сервера."""
    def getAccInfo(self):
        return self._call_to_api("getInfo", {})


    """Основной метод используя который можно создавать ордера и торговать на бирже."""
    def make_Money(self, tpair, ttype, trate, tamount):
        params = {"nonce": self.__nonce,
                  "pair": tpair,
                  "type": ttype,
                  "rate": trate,
                  "amount": tamount}
        return self._call_to_api("Trade", params)


    """Возвращает историю сделок."""
    def get_TradeHistory(self, **kwargs):
        if kwargs:
            params = dict(kwargs)
        else:
            params = {}
        return self._call_to_api("TradeHistory", params)


    """Возвращает историю транзакций."""
    def get_TransHistory(self, **kwargs):
        if kwargs:
            params = dict(kwargs)
        else:
            params = {}
        return self._call_to_api("TransHistory", params)


    """Возращает список ваших активных ордеров."""
    def get_ActiveOrders(self, tpair=None):
        if tpair:
            params = {"pair": tpair}
        else:
            params = {}
        return self._call_to_api("CancelOrder", params)


    """Метод предназначен для отмены ордера."""
    def cancelOrder(self, id_order):
        params = {'order_id': id_order}
        return self._call_to_api("ActiveOrders", params)


    """Возращает информацию о конкретном ордере."""
    def get_OrderInfo(self, id_order):
        params = {'order_id': id_order}
        return self._call_to_api("OrderInfo", params)


    """Метод предназначен для получения депозитного адреса криптовалюты."""
    def get_CoinDepositAdress(self, coinName):
        params = {'coinName': coinName}
        return self._call_to_api('CoinDepositAddress', params)


    """Метод предназначен для вывода криптовалюты."""
    def want_myManey(self, coinName, amount, address):
        params = {'coinName': coinName, 'amount': amount, 'address': address}
        return self._call_to_api('WithdrawCoin', params)


    def wbNonce(self):
        filew = open("nonce.txt", 'w')
        filew.write(str(self.__nonce))
        filew.close()


    def change_key(self, key):
        self.__btcKey = key


    def change_secret(self, secret):
        self.__btcSecret = secret


class Public_Api():
    def __init__(self, url, proxies):
        self.__url = url
        self.__proxies = proxies


    """Данный метод предоставляет всю информацию о текущих активных парах, такую как: максимальное количество знаков 
    после запятой при торгах, минимальную цену, максимальную цену, минимальное количество при покупке/продаже, 
    скрыта ли пара и комиссию по паре."""
    def get_Info(self):
        cur_url = self.__url + "/info"
        response = requests.get(cur_url, proxies=self.__proxies).json()
        #print(response)
        return response


    """Данный метод предоставляет всю информацию о торгах по паре, такую как: максимальная цена, минимальная цена, 
    средняя цена, объем торгов, объем торгов в валюте, последняя сделка, цена покупки и продажи."""
    def get_Ticker(self, pairs):
        cur_url = self.__url + "/ticker/"
        for pair in pairs:
            cur_url += "{}-".format(pair)
        cur_url = cur_url[:-1]
        response = requests.get(cur_url, proxies=self.__proxies).json()
        return response


    """Данный метод предоставляет информацию о активных ордерах пары."""
    def get_Depth(self, pairs, limit=None):
        cur_url = self.__url + "/depth/"
        for pair in pairs:
            cur_url += "{}-".format(pair)
        cur_url = cur_url[:-1]
        if limit:
            cur_url += "?limit={}".format(limit)
        response = requests.get(cur_url, proxies=self.__proxies).json()
        return response


    """Данный метод предоставляет информацию о последних сделках."""
    def get_Trades(self, pairs, limit=None):
        cur_url = self.__url + "/trades/"
        for pair in pairs:
            cur_url += "{}-".format(pair)
        cur_url = cur_url[:-1]
        if limit:
            cur_url += "?limit={}".format(limit)
        response = requests.get(cur_url, proxies=self.__proxies).json()
        return response


def make_PAclass():
    return Public_Api(url, proxies)
def make_TAclass():
    return Trade_Api("", "", nonce, proxy_HTTPS, proxy_HTTPS_port)


#tt = Trade_Api(BTC_key, BTC_secret, nonce, proxy_HTTPS, proxy_HTTPS_port)
#print(tt.getAccInfo())
#print(tt.get_TradeHistory(count=2))
#print(tt.get_ActiveOrders())
#print(tt.make_Money("btc_usd", "buy", 2000, 1))
#tt.wbNonce()

#tp = make_PAclass()
#print(tp.get_Info())
#print(tp.get_Ticker(("eth_rur", "btc_usd")))
#print(tp.get_Depth(("ltc_usd", "ltc_eur"), limit=5))
#print(tp.get_Trades("eth_rur", limit=3))
