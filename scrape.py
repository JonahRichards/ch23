import sqlite3
from fractions import Fraction
import pandas
import requests
import time
import random
from bs4 import BeautifulSoup
import pandas as pd

base_url = "https://www.budgetbytes.com/"


def parse_endpoints(page_num):
    endpoints = []

    r = requests.get(f"{base_url}recipe-catalog/page/{page_num}/")

    if r.status_code == 200:
        r = r.content.decode(r.apparent_encoding)
        r = BeautifulSoup(r, "html.parser")

        arts = r.find_all("article")

        for art in arts:
            if len(art.a.contents[1].contents) == 1:
                pass
            else:
                endpoints.append(art.a.attrs["href"].split(base_url)[1])

    return endpoints


def get_endpoints():
    r = requests.get(f"{base_url}recipe-catalog/")

    if r.status_code == 200:
        r = r.content.decode(r.apparent_encoding)
        r = BeautifulSoup(r, "html.parser")

        uls = r.find_all("ul")

        for ul in uls:
            try:
                if ul.attrs["role"] == "navigation":
                    max = int(ul.find_all("li")[4].a.attrs["href"].split("/")[5])
                    break
            except KeyError:
                pass

        endpoints = []

        for i in range(1, max + 1):
            time.sleep(random.randint(50, 150) / 100)
            print(f"{i}/{max}")
            endpoints += parse_endpoints(i)

    endpoints_df = pd.DataFrame({"endpoints": endpoints})
    endpoints_df.to_csv("csv/endpoints.csv", index=False)


def upload_endpoints():
    connection = sqlite3.connect('database.db')
    cur = connection.cursor()

    endpoints = list(pandas.read_csv("csv/endpoints.csv")["endpoints"])

    values = ""

    for ep in endpoints:
        values += f"('{ep}'), "

    values = values[:-2]

    cur.execute(f"INSERT INTO endpoints (endpoint) VALUES {values}")

    connection.commit()
    connection.close()


def fetch_recipe(endpoint):
    try:
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        r = requests.get(f"{base_url}{endpoint}")

        if r.status_code == 200:
            r = r.content.decode(r.apparent_encoding)
            r = BeautifulSoup(r, "html.parser")

            try:
                servings = int(r.find("span", {"class": "wprm-recipe-servings-with-unit"}).contents[0].contents[0])
            except AttributeError:
                servings = int(r.find("div", {"class": "bb-recipe-card__meta"}).contents[1].contents[3].contents[0])

            ingredients = r.find_all("ul", {"class": "wprm-recipe-ingredients"})

            new_ingredients = []
            for i in range(len(ingredients)):
                for v in ingredients[i].contents:
                    new_ingredients.append(v)

            ingredients = new_ingredients

            price = 0.0

            for ingr in ingredients:
                try:
                    ingr_name = ingr.find("span", {"class": "wprm-recipe-ingredient-name"}).next
                    if len(ingr_name) == 1:
                        ingr_name = ingr_name.next
                    ingr_name = ingr_name.split(",")[0].split("(")[0].lower().strip("*").replace("'", "")
                    ingr_quant = float(sum(Fraction(s) for s in ingr.find("span", {"class": "wprm-recipe-ingredient-amount"}).next.split()))
                    ingr_quant = str(round(ingr_quant / servings, 4))
                    if ingr.find("span", {"class": "wprm-recipe-ingredient-unit"}) is not None:
                        ingr_quant += " " + str(ingr.find("span", {"class": "wprm-recipe-ingredient-unit"}).next).lower().replace("'", "")
                    ingr_price = ingr.find("span", {"class": "wprm-recipe-ingredient-notes"}).next.strip("()$")
                    ingr_price = str(round(float(ingr_price) / servings, 4))

                    price += float(ingr_price)
                except AttributeError:
                    continue

                con.execute(f"insert into ingredients (endpoint, name, quantity, cost)"
                            f"VALUES ('{endpoint}', '{ingr_name}', '{ingr_quant}', {ingr_price})")

            price = round(price, 4)

            try:
                name = r.find("h1", {"class": "entry-title"}).next
            except AttributeError:
                name = endpoint.replace("-", " ").strip("/").title()

            calories = r.find("span", {"class": "wprm-nutrition-label-text-nutrition-container-calories"}).contents[1].next
            protein = r.find("span", {"class": "wprm-nutrition-label-text-nutrition-container-protein"}).contents[1].next
            fat = r.find("span", {"class": "wprm-nutrition-label-text-nutrition-container-fat"}).contents[1].next
            carbs = r.find("span", {"class": "wprm-nutrition-label-text-nutrition-container-carbohydrates"}).contents[1].next

            con.execute(f"insert into recipes (endpoint, name, servings, cost, calories, protein, fat, carbs)"
                        f"VALUES ('{endpoint}', '{name}', {servings}, {price}, {calories}, {protein}, {fat}, {carbs})")

        con.commit()
        con.close()

    except Exception as e:
        print(f"Endpoint {endpoint} failed: {e}")


def fetch_recipes():
    con = sqlite3.connect("database.db")
    cur = con.cursor()
    cur.execute("delete from ingredients")
    cur.execute("delete from recipes")
    con.commit()
    endpoints = list(pandas.read_sql("select * from endpoints", con)["endpoint"])
    con.close()

    for i, endpoint in enumerate(endpoints):
        if i == -1: continue
        time.sleep(random.randint(50, 150) / 100)
        fetch_recipe(endpoint)
        print(f"{i+1}/{len(endpoints)}")


def upload_country_data():
    curr = pandas.read_csv("csv/currencies.csv")
    rate = pandas.read_csv("csv/exchange_rates.csv")
    indx = pandas.read_csv("csv/price_indices.csv")

    curr = {r["Country"]: r["Code"] for i, r in curr.iterrows()}
    rate = {r["Country Name"].strip(", The"): r["2017 [YR2017]"] for i, r in rate.iterrows()}
    countries = list(indx["Country Name"].drop_duplicates())
    indx = {r["Country Name"].strip(", The") + str(r["Series Code"]): r["2017 [YR2017]"] for i, r in indx.iterrows() if r["2017 [YR2017]"] != ".."}

    rows = []

    for c in countries:
        try:
            row = {"country": c,
                   "currency": curr[c],
                   "rate": rate[c],
                   "food_inx":  indx[c + "1101100"],
                   "grain_inx": indx[c + "1101110"],
                   "meat_inx": indx[c + "1101120"],
                   "fish_inx": indx[c + "1101130"],
                   "dairy_inx": indx[c + "1101140"],
                   "oil_inx": indx[c + "1101150"],
                   "fruit_inx": indx[c + "1101160"],
                   "veg_inx": indx[c + "1101170"],
                   "sweets_inx": indx[c + "1101180"],
                   "bev_inx": indx[c + "1101200"],
                   "alcohol_inx": indx[c + "1102100"],}
        except KeyError:
            continue
        rows.append(row)

    con= sqlite3.connect('database.db')
    con.cursor().execute("delete from countries")
    con.commit()

    df = pd.DataFrame(rows)
    df.to_sql("countries", con, if_exists="append", index=False)

    con.commit()
    con.close()






