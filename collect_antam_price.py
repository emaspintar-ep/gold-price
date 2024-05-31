import json
import copy
import requests

req = requests.get(
    "https://www.logammulia.com/id/harga-emas-hari-ini",
    headers={
        'User-Agent': (
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/50.0.2661.102 Safari/537.36'
        )
    }
)
content = req.content.decode()


def extract_current_date(page):
    page = page.split('<h2 class="ngc-title">Harga Emas Hari Ini', 1)[1]
    page = page.split('</h2>', 1)[0]
    page = page.strip(", ")

    month_map = {
        "January": "Januari",
        "February": "Februari",
        "March": "Maret",
        "April": "April",
        "May": "Mei",
        "June": "Juni",
        "July": "Juli",
        "August": "Agustus",
        "September": "September",
        "October": "Oktober",
        "November": "November",
        "December": "Desember",
    }
    for eng, ind in month_map.items():
        if eng in page:
            page = page.replace(eng, ind)
            break
    return page


curret_date_str = extract_current_date(content)
print(curret_date_str)


filename = "antam_today_price.json"
data = json.load(open(filename))
# print(data)

today = data["today"]
if today["date"] == curret_date_str:
    print("DATA SAME, NO NEED PROCESS", today["date"])
    exit()


data["yesterday"] = copy.deepcopy(today)
yesterday = data["yesterday"]


def format_price_change(current_price_str, yesterday_price_str):
    current_price = int(current_price_str.replace(".", ""))
    yesterday_price = int(yesterday_price_str.replace(".", ""))
    change_price = current_price - yesterday_price
    change_str = '{:,}'.format(change_price).replace(",", ".")
    if change_price >= 0:
        change_str = "+" + change_str
    return change_str


def extract_table_price(page):
    page = page.split('<th colspan="4" style="text-align:center;">Emas Batangan</th>', 1)[1]
    page = page.split('<th colspan="4" style="text-align:center;">Emas Batangan Gift Series</th>', 1)[0]

    page = page.replace('<td style="text-align:right;">', "")
    page = page.replace('<td>', "")
    page = page.replace('</td>', "")
    page = page.replace('<tr>', "")
    page = page.replace('</tr>', "")
    page = page.strip()

    results = []
    item_price = []
    for item in page.split("\n"):
        item = item.strip()
        if not item:
            continue
        item_price.append(item)
        if len(item_price) >= 3:
            results.append({
                "gram": item_price[0].replace(".", ","),
                "price": item_price[1].replace(",", "."),
            })
            item_price = []

    for index, item in enumerate(results):
        item["price_change"] = format_price_change(
            item["price"],
            yesterday["prices"][index]["price"],
        )
        print(item["price"], yesterday["prices"][index]["price"],  item["price_change"])
    return results


prices = extract_table_price(content)
# print(table)


def fetch_buyback():
    req = requests.get(
        "https://www.logammulia.com/id/sell/gold",
        headers={
            'User-Agent': (
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/50.0.2661.102 Safari/537.36'
            )
        }
    )
    content = req.content.decode()
    price = content.split('<span class="title">Harga Buyback:</span>', 1)[1]
    price = price.split('<span class="text">Rp', 1)[1]
    price = price.split('</span>', 1)[0]
    price = price.replace(",", ".")
    price = price.strip(", ")
    print("buyback price", price)
    return {
        "price": price,
        "price_change": format_price_change(
            price,
            yesterday["buyback"]["price"],
        )
    }

today["date"] = curret_date_str
today["prices"] = prices
today["buyback"] = fetch_buyback()


print("=" * 100)
print(data)

with open(filename, "w") as file:
    json.dump(data, file)
