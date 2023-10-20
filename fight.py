from flask import Flask, request, jsonify, render_template
import yahoo_fin.stock_info
import datetime
import json
import requests
import time
# notes
# If you have the debugger disabled or trust the users on your network, you can make the server publicly available simply by adding --host=0.0.0.0 to the command line:
#  $ flask run --host=0.0.0.0

# y finn olny works for tickers what if tou want to caonpare vs s&p or down  (seekingalpah watchlist??)
today = datetime.date.today()
pastDate = datetime.timedelta(days=25)
pastDate = today - pastDate


url = "https://seekingalpha.com/api/v3/historical_prices"
payload = ""
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "cookie": "_pxhd=6d70a2b6f78b1cfd2110e137d19cfa4d06ebdd1d6688314ec21c9d85b8a4d293%3Ad02fc780-65bc-11e9-b971-bb43e5539738; machine_cookie=2303971194805; machine_cookie_ts=1697547548"}


def fetcher(tickers, start , end):
    returnDict = {}
    try:    # all
        for ticker in tickers:
            querystring = {f"portfolioId": "61926338", "filter[ticker][slug]": {ticker},
                           "filter[as_of_date][gte]": {start}, "filter[as_of_date][lte]": {end},  # used to have day (ex Tue Oct 20 2023)
                           "sort": "as_of_date"}
            raw = requests.request("GET", url, data=payload, headers=headers, params=querystring)
            rawJSON = json.loads(raw.text)
            # print(raw.text)
            # print("")
            # print(rawJSON)

            ticker = rawJSON['included'][0]['attributes']['slug'] # ticker

            closes = []
            dates = []
            for iter in range(str(rawJSON).count("close")):
                # print(iter)
                close = rawJSON["data"][iter]["attributes"]["close"]      # can easily scale to make candlestick charts
                closes.append(close)
                date = rawJSON["data"][iter]["attributes"]["as_of_date"]
                dates.append(date)

            print(closes, ticker, dates)
            returnDict[ticker] = {"dates" : dates, "prices" : closes}
        print("")
        print(json.dumps(returnDict))
        return json.dumps(returnDict)
    except:
        return f"ERROR CODE 500. Fetch data error fecher({tickers, start, end}. most likly connection error"

nummonth = { 1 : "Jan",  2 : "Feb", 3 : "Mar", 4 : "Apr", 5 : "May", 6 : "Jun", 7 : "Jul", 8 : "Aug", 9 : "Sep",
             10 : "Oct", 11 : "Nov", 12 : "Dec"}    # check if its Set or Sept


def parseClean(params):
    # print(params, "par")
    s = " "
    try:
        tickers = []
        raw = params.split("*")
        # print(raw)

        ticks = raw[0].split("%")                    # tickers
        for t in ticks:                         # EX aapl % msft % cost *
            tickers.append(t)

        start = raw[1].split("+")                    # Ex 10 % 8 % 2023
        m = nummonth[int(start[0])]
        d = start[1]
        y = start[2]
        start = str(m + s + d + s + y)

        if raw[2] == "end":
            end = datetime.date.today()                 #  FIX
            end = str(end)
        else :
            end = raw[2].split("+")
            m = nummonth[int(end[0])]
            d = end[1]
            y = end[2]
            end = str(m + s + d + s + y)
        return [tickers, start, end]
    except: return params, "ERROR CODE 500. Wrong vaules entered"




app = Flask(__name__)

@app.route("/")
def home():
    py_var = "hello - python "                      # passing a varible intp the html (see html too)
    return render_template("please_graph.html", variable=py_var)            # loading pages / ^^^

@app.route("/fetch/")
def fetch():                                                            #http://127.0.0.1:4000/fetch
    return "this will be the json data"        # in the end it will be https://base_or_domain/fetch


@app.route("/fetch/<params>", methods=["GET"])  # http://127.0.0.1:4000/fetch/aapl%msft%cost*10+8+2023*10+18+2023
def response(params):                       # [ [ tickers, tickers], start,  end=today]
    params = parseClean(params=params)
    data = fetcher(tickers=params[0],start=params[1], end=params[2])

    return data


if __name__ == "__main__":
    app.run(debug=True, port=4000)  #



