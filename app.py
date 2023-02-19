import sqlite3
import pandas as pd
from flask import Flask, render_template, request, url_for, flash, redirect
import pycountry

app = Flask(__name__)


def get_type(name):
    return "food_inx"


def recipe_logic(country):
    con = sqlite3.connect('database.db')

    df = pd.read_sql(f"select * from countries where country = '{country}'", con)
    indx = df.iloc[0].to_dict()
    df = pd.read_sql(f"select * from countries where country = 'United States'", con)
    us_indx = df.iloc[0].to_dict()
    r_df = pd.read_sql("select * from recipes", con)

    descs = []

    for row in r_df.iterrows():
        df = pd.read_sql(f"select * from ingredients where endpoint = '{row[1].endpoint}'", con)
        names = list(df["name"])
        costs = list(df["cost"])

        for i, v in enumerate(names):
            ix = get_type(v)
            costs[i] = costs[i] * indx[ix] / us_indx[ix]

        cost = round(sum(costs) * indx["rate"], 2)

        info = []
        info.append(row[1]["name"])
        info.append(f"{cost} {indx['currency']}")
        info.append(f"{row[1].calories} kcal")
        info.append(f"{row[1].protein} g")
        info.append(f"{row[1].fat} g")
        info.append(f"{row[1].carbs} g")
        info.append(f"{row[1].endpoint}")

        descs.append(info)

    return descs


@app.route('/Welcome', methods=('GET', 'POST'))
def welcome():
    if request.method == 'POST':
        return redirect(url_for('select_country'), code=303)
    return render_template('welcome.html')


@app.route('/SelectCountry', methods=('GET', 'POST'))
def select_country():
    if request.method == 'POST':
        return redirect(url_for('recipes', country=request.form["but"]))
    con = sqlite3.connect('database.db')
    df = pd.read_sql("select country, code from countries order by country", con)
    countries = list(df["country"])
    codes = list(df["code"])
    return render_template("select_country.html", len=len(countries), countries=countries, codes=codes)


@app.route('/Recipes/<country>', methods=('GET', 'POST'))
def recipes(country):
    if request.method == 'POST':
        # return redirect(url_for('recipe', country=country, recipe=request.form["but"]))
        return redirect(f"https://www.google.com/search?q={request.form['but'].strip('/').replace('-', '+')}+recipe")
    descs = recipe_logic(country)
    return render_template("recipes.html", len=len(descs), descs=descs)


@app.route('/Recipe/<country>', methods=('GET', 'POST'))
def recipe(country, recipe):
    descs = recipe_logic(country)
    return render_template("recipes.html", len=len(descs), descs=descs)





app.run()