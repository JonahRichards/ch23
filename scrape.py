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


get_endpoints()
