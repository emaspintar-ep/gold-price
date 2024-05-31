import json
import copy
import requests

req = requests.get(
    "https://www.galeri24.co.id/harga-emas",
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
    page = page.split('Diperbarui', 1)[1]
    page = page.split('</div>', 1)[0]
    page = page.split(',', 1)[1]
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


filename = "pegadaian_today_price.json"
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
    page = page.split('Harga Buyback', 1)[1]
    page = page.split('<div id="UBS">', 1)[0]
    page = page.replace('<div>', "")
    page = page.replace('</div>', "\n")
    page = page.replace('<div class="grid grid-cols-5 divide-x lg:hover:bg-neutral-50 transition-all">', "")
    page = page.replace('<div class="p-3 col-span-1 whitespace-nowrap w-fit">', "")
    page = page.replace('<div class="p-3 col-span-2 whitespace-nowrap w-fit">', "")
    page = page.replace('<!--[-->', "")
    page = page.replace('<!--]-->', "")
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
                "gram": item_price[0].replace(".", ",") + " gr",
                "price": item_price[1].replace(",", ".").replace("Rp", ""),
                "buyback": item_price[2].replace(",", ".").replace("Rp", ""),
            })
            item_price = []

    for index, item in enumerate(results):
        item["price_change"] = format_price_change(
            item["price"],
            yesterday["prices"][index]["price"],
        )
        print(
            item["price"],
            yesterday["prices"][index]["price"],
            item["price_change"],
        )

        item["buyback_change"] = format_price_change(
            item["buyback"],
            yesterday["prices"][index]["buyback"],
        )
        print(
            item["buyback_change"],
            yesterday["prices"][index]["buyback"],
            item["buyback_change"],
        )
    return results


prices = extract_table_price(content)
print(prices)

today["date"] = curret_date_str
today["prices"] = prices


print("=" * 100)
print(data)

with open(filename, "w") as file:
    json.dump(data, file)
