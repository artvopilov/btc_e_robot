from bs4 import BeautifulSoup
import requests
import pylab
from BtceGo import get_proxies


url = "https://btc-e.com/exchange/"
proxies = get_proxies()


def func_data_for_graphics(pairs, url, proxies):
    for pair in pairs:
        url += pair
        html_code = requests.get(url, proxies=proxies).text
        read_html = BeautifulSoup(html_code, "html5lib")
        div_list = read_html.body.findAll("div")
        content_div = 0
        for div in div_list:
            if "id" in div.attrs:
                if div["id"] == "content":
                    content_div = div
        if not content_div:
            yield 0, 0, 0

        div_block = content_div.div.findAll("div")[1]
        script_list = div_block.findAll("script")
        for script in script_list:
            if list(script.attrs.keys()) == ["type"]:
                script_for_graphics = script

        first_partition = script_for_graphics.text.partition("var data = google.visualization.arrayToDataTable(")[2]
        second_partition = str(first_partition.partition(", true)")[0][1:-1])
        second_partition = second_partition.replace("[", "")
        second_partition = second_partition.replace("]", "")
        second_partition = second_partition.split(",")
        # print(second_partition)

        len_sp = len(second_partition) / 6
        i = 0
        toPop = 0
        time_list = []
        while i < len_sp:
            time_list.append(str(second_partition.pop(toPop)))
            toPop += 6 - 1
            i += 1

        x = []
        for i in range(len(time_list)):
            x.append(i)
        y = []
        point = 1
        for i in range(len(second_partition) // 5):
            y.append(second_partition[point])
            point += 5

        yield x, y, pair


def show_graphics(pairs):
    count = 1
    for x, y, pair in func_data_for_graphics(pairs, url, proxies):
        if not pair:
            print("Smth has gone wrong, maybe proxy daesn't work")
        pylab.figure(figsize=(10, 5)).suptitle("График " + str(pair))
        pylab.subplot(1, 1, 1)
        pylab.plot(x, y)
        pylab.grid()
        pylab.xlabel("Последние 50 обновлений курса (обновления производятся каждые полчаса)", color="blue", backgroundcolor="#E6E6FA")
        pylab.ylabel("Курс {}".format(pair), color="blue", backgroundcolor="#E6E6FA")
        count += 1
    pylab.show()


#try:
#    show_graphics(("btc_rur", "btc_usd", "btc_eur"))
#except requests.exceptions.ProxyError:
#    print("Proxy daesn't work")

