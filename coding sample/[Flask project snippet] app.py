from flask import Flask, render_template, jsonify, request
import random
import json
import csv
import os
import pymongo
import pandas as pd
import datetime
import numpy as np
import time
from pymongo import MongoClient
from bson.json_util import dumps
from bson.json_util import loads
from util.encoder import MyEncoder
from Calculation import *
from definition4 import *

app = Flask(__name__, static_folder="./dist/static", template_folder="./dist")
client = MongoClient('mongo', 27017, username='root',password='example')
db = client.denryoku_data


# デフォルト
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def index(path):
    return render_template('index.html')

#test用api
@app.route('/test')
def test():
    json_list = []
    os.getcwd()
# CSV ファイルの読み込み
    with open('1year_decision_Tokyo.csv', 'r') as f:
        for row in csv.DictReader(f):
            json_list.append(row)

# JSON ファイルへの書き込み
    with open('1year_decision_Tokyo.json', 'w') as f:
        json.dump(json_list, f)

# JSONファイルのロード
    with open('1year_decision_Tokyo.json', 'r') as f:
        json_output = json.load(f)
        f = open("1year_decision_Tokyo.json", 'r')
        json_data = json.load(f)
    return ("{}".format(json.dumps(json_data,indent=3)))


# '/rand'が叩かれた時、乱数を生成
@app.route('/rand')
def random_test():
    response = {
        'randomNum': random.random()
    }
    return jsonify(response)


# 'swagger_test' が叩かれた時のレスポンスの例
@app.route('/swagger_test')
def swagger_test():
    # 値の取り出しに何かしらの処理が必要な場合はここでおこなう。（mongodbからとってくるときのやつ、なにかしらのcontrollerを挟んで値を取ってくるこ
    # とがほとんどかと）今回はテストなので何もしない。

    # ここのレスポンスの形式がswaggerで定義されたものと一致していることを確認する。これが最低限で、理想は例外処理なども含めて全てswaggerで定義
    # されているとおりであるとよい。ただ、今回はいらないかと。
    response = {
        'id': random.randint(1, 100),
        'name': "this is a test API"
    }
    return jsonify(response)  # json 形式で返す

    # ここでサーバーとのやりとりの処理をおこなう。

#　テスト：mongoDBを読み込んでFlask.appに表示
@app.route('/mongo_test')
def mongo_test():
    cursor =  db.act_data.find({}, {'_id': False})
    response = {'data': loads(dumps(cursor))}
    # return jsonify(str(response))
    return jsonify(response)

#call temperature per month
@app.route('/get_graph_data_month/<graph>/<scenario>/<month>')
def get_graph_data_month(graph, scenario, month):
    Month = int(month)
    drop2 = graph
    SimulardayCSV = pd.read_csv("data/csv/similarday_h.csv", encoding="shift-jis").values.tolist()
    simlist = []
    for i in SimulardayCSV:
        if datetime.datetime.strptime(i[0], '%Y/%m/%d').month == Month:
            simlist.append([i[0],i[1],i[2],i[3],i[4]])
    data1 = pd.read_csv("data/csv/ActData_modified.csv",encoding="utf-8")
    data1["hiduke"] = pd.to_datetime(data1['hiduke'])
    SceMD1 = []
    SceMD2 = []
    SceMD3 = []
    SceMD4 = []
    ActData = []
    Days = []
    cnt = 1
    for i in simlist:
        ActData.append(np.average(data1[data1["hiduke"] == datetime.datetime.strptime(i[0],'%Y/%m/%d')][drop2]))
        SceMD1.append(np.average(data1[data1["hiduke"] == datetime.datetime.strptime(i[1],'%Y/%m/%d')][drop2]))
        SceMD2.append(np.average(data1[data1["hiduke"] == datetime.datetime.strptime(i[2],'%Y/%m/%d')][drop2]))
        SceMD3.append(np.average(data1[data1["hiduke"] == datetime.datetime.strptime(i[3],'%Y/%m/%d')][drop2]))
        SceMD4.append(np.average(data1[data1["hiduke"] == datetime.datetime.strptime(i[4],'%Y/%m/%d')][drop2]))
        Days.append(cnt)
        cnt += 1
    if graph == "power":
        data2 = pd.read_csv("1year_decision_Tokyo.csv",encoding="shift-jis")
    else:
        data2 = pd.read_csv("data/csv/2019ForeData_modified.csv",encoding="shift-jis")
    data2["hiduke"] = pd.to_datetime(data2['hiduke'])
    PredMD = []
    for i in simlist:
        PredMD.append(np.average(data2[data2["hiduke"] == datetime.datetime.strptime(i[0],'%Y/%m/%d')][drop2]))

    if scenario == "2019":
        response = {
            "scenario_or_2019":scenario,
            "month":int(month),
            "graph_type": graph,
            "actData": json.dumps(ActData,cls=MyEncoder),
            "forecast": json.dumps(PredMD,cls=MyEncoder),
            "days": Days
        }
        return jsonify(response)
    elif scenario == "scenario":
        response = {
            "scenario_or_2019":scenario,
            "month":int(month),
            "days": Days,
            "graph_type": graph,
            "scenario_1": json.dumps(SceMD1,cls=MyEncoder),
            "scenario_2": json.dumps(SceMD2,cls=MyEncoder),
            "scenario_3": json.dumps(SceMD3,cls=MyEncoder),
            "scenario_4": json.dumps(SceMD4,cls=MyEncoder),
            "forecast": json.dumps(PredMD,cls=MyEncoder),
        }
        return jsonify(response)
    else:
        error_message ="error"
        return jsonify(error_message)

# call temperature per day
# graph = temperature/power/spot_price/rain_humidity/snow_wind_speed
# scenario = 2019/scenario
@app.route('/get_graph_data_day/<graph>/<scenario>/<month>/<day>')
def get_graph_data_day(graph, scenario, month, day):
    Month = int(month)
    Day = int(day)
    #drop2=graph: "temperature" or "power"
    drop2 = graph
    SimulardayCSV = pd.read_csv("data/csv/similarday_h.csv",encoding="shift-jis").values.tolist()
    for i in SimulardayCSV:
        if datetime.datetime.strptime(i[0], '%Y/%m/%d').month == Month:
            if datetime.datetime.strptime(i[0], '%Y/%m/%d').day == Day:
                Daylist = [i[0],i[1],i[2],i[3],i[4]]
    data1 = pd.read_csv("data/csv/ActData_modified.csv",encoding="utf-8")
    data1["hiduke"] = pd.to_datetime(data1['hiduke'])
    SceDD1 = []
    SceDD2 = []
    SceDD3 = []
    SceDD4 = []
    hours = []
    ActData = []
    for i in range(48):
        ActData.append(np.average(data1[(data1["hiduke"] == datetime.datetime.strptime(Daylist[0],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))
        SceDD1.append(np.average(data1[(data1["hiduke"] == datetime.datetime.strptime(Daylist[1],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))
        SceDD2.append(np.average(data1[(data1["hiduke"] == datetime.datetime.strptime(Daylist[2],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))
        SceDD3.append(np.average(data1[(data1["hiduke"] == datetime.datetime.strptime(Daylist[3],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))
        SceDD4.append(np.average(data1[(data1["hiduke"] == datetime.datetime.strptime(Daylist[4],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))
        hours.append(i+1)
    if graph == "power":
        data2 = pd.read_csv("1year_decision_Tokyo.csv",encoding="shift-jis")
    else:
        data2 = pd.read_csv("data/csv/2019ForeData_modified.csv",encoding="shift-jis")
    data2["hiduke"] = pd.to_datetime(data2['hiduke'])
    PredDD = []
    for i in range(48):
        PredDD.append(np.average(data2[(data2["hiduke"] == datetime.datetime.strptime(Daylist[0],'%Y/%m/%d'))&(data1["jikoku_code"] == i+1)][drop2]))

    if scenario == "2019":
        response = {
            "scenario":scenario,
            "month":int(month),
            "day":int(day),
            "hours": hours,
            "graph_type": graph,
            "actData": json.dumps(ActData,cls=MyEncoder),
            "forecast": json.dumps(PredDD,cls=MyEncoder),
        }
        return jsonify(response)
    elif scenario == "scenario":
        response = {
            "scenario_or_2019":scenario,
            "month":int(month),
            "day":int(day),
            "hours": hours,
            "graph_type": graph,
            "scenario_1": json.dumps(SceDD1,cls=MyEncoder),
            "scenario_2": json.dumps(SceDD2,cls=MyEncoder),
            "scenario_3": json.dumps(SceDD3,cls=MyEncoder),
            "scenario_4": json.dumps(SceDD4,cls=MyEncoder),
            "forecast": json.dumps(PredDD,cls=MyEncoder),
        }
        return jsonify(response)
    else:
        error_message ="error"
        return jsonify(error_message)

# テスト用
@app.route('/temperature_m_test')
def temperature_m_test():
    days_list = list(range(1,31))
    temperature_list = [random.uniform(10,30) for i in range(len(days_list))]
    response = {
        "scenario": "scenario1",
        "month": 1,
        "temperatures": temperature_list,
        "days": days_list,
    }
    return jsonify(response)
# テスト用
@app.route('/temperature_d_test')
def temperature_d_test():
    times_list = list(range(1,49))
    temperature_list = [random.uniform(10,30) for i in range(len(times_list))]
    response = {
        "scenario": "scenario1",
        "month": 1,
        "temperatures": temperature_list,
        "days": times_list,
    }
    return jsonify(response)
# 年間コスト比較
@app.route('/compare_cost_co2_ideal')
def compare_cost_co2_ideal():
    response = {
        "id": [
            0,
            1,
            2
        ],
        "cost": [
            "10.41",
            "10.88",
            "11.25"
        ],
        "co2": [
            "50.96",
            "45.07",
            "40.34"
        ]
    }
    return jsonify(response)

@app.route('/output_daily_co2_scenario/<month>/<day>',methods=["post"])
def output_daily_co2_scenario(month,day):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    hours,Scenario_Daily_Co2 = OutputDailyCo2("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month,day)
    response = {
        "month":int(month),
        "day":int(day),
        "scenario1":Scenario_Daily_Co2[0],
        "scenario2":Scenario_Daily_Co2[1],
        "scenario3":Scenario_Daily_Co2[2],
        "scenario4":Scenario_Daily_Co2[3],
        "times":hours
    }
    return jsonify(response)

@app.route('/output_daily_co2/<month>/<day>',methods=["post"])
def output_daily_co2(month,day):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    hours,Aitai_Daily_Co2 = OutputDailyCo2("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month,day)
    response = {
        "month":int(month),
        "day":int(day),
        "aitai1":Aitai_Daily_Co2[0],
        "aitai2":Aitai_Daily_Co2[1],
        "aitai3":Aitai_Daily_Co2[2],
        "aitai4":Aitai_Daily_Co2[3],
        "times":hours
    }
    return jsonify(response)

@app.route('/daily_procure/<month>/<day>',methods=["post"])
def output_daily_procure(month,day):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    hours,Aitai_Daily_Procure = DailyProcure_1("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month,day)
    response = {
        "month":int(month),
        "day":int(day),
        "aitai1":Aitai_Daily_Procure[0],
        "aitai2":Aitai_Daily_Procure[1],
        "aitai3":Aitai_Daily_Procure[2],
        "aitai4":Aitai_Daily_Procure[3],
        "jepx_imbalance":Aitai_Daily_Procure[4],
        "times":hours
    }
    return jsonify(response)

@app.route('/output_daily_cost_scenario/<month>/<day>',methods=["post"])
def output_daily_cost_scenario(month,day):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    hours,Scenario_Daily_Cost = OutputDailyCost("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month,day)
    response = {
        "month":int(month),
        "day":int(day),
        "scenario1":Scenario_Daily_Cost[0],
        "scenario2":Scenario_Daily_Cost[1],
        "scenario3":Scenario_Daily_Cost[2],
        "scenario4":Scenario_Daily_Cost[3],
        "times":hours
    }
    return jsonify(response)

@app.route('/output_daily_cost/<month>/<day>',methods=["post"])
def output_daily_cost(month,day):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    hours,Aitai_Daily_Cost = OutputDailyCost_1("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month,day)
    response = {
        "month":int(month),
        "day":int(day),
        "aitai1":Aitai_Daily_Cost[0],
        "aitai2":Aitai_Daily_Cost[1],
        "aitai3":Aitai_Daily_Cost[2],
        "aitai4":Aitai_Daily_Cost[3],
        "jepx_imbalance":Aitai_Daily_Cost[4],
        "times":hours
    }
    return jsonify(response)

@app.route('/output_monthly_co2_scenario/<month>',methods=["post"])
def output_monthly_co2_scenario(month):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    Days,Scenario_Monthly_Co2 = OutputMonthlyCo2("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month)
    response = {
        "month":int(month),
        "scenario1":Scenario_Monthly_Co2[0],
        "scenario2":Scenario_Monthly_Co2[1],
        "scenario3":Scenario_Monthly_Co2[2],
        "scenario4":Scenario_Monthly_Co2[3],
        "days":Days
    }
    return jsonify(response)

@app.route('/output_monthly_co2/<month>',methods=["post"])
def output_monthly_co2(month):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    Days,Aitai_Monthly_Co2 = OutputMonthlyCo2_1("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month)
    response = {
        "month":int(month),
        "aitai1":Aitai_Monthly_Co2[0],
        "aitai2":Aitai_Monthly_Co2[1],
        "aitai3":Aitai_Monthly_Co2[2],
        "aitai4":Aitai_Monthly_Co2[3],
        "jepx_imbalance":Aitai_Monthly_Co2[4],
        "days":Days
    }
    return jsonify(response)



@app.route('/monthly_procure/<month>',methods=["post"])
def monthly_procure(month):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    Days,Aitai_Monthly_Procure = MonthlyProcure_1("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month)
    response = {
        "month":int(month),
        "aitai1":Aitai_Monthly_Procure[0],
        "aitai2":Aitai_Monthly_Procure[1],
        "aitai3":Aitai_Monthly_Procure[2],
        "aitai4":Aitai_Monthly_Procure[3],
        "jepx_imbalance":Aitai_Monthly_Procure[4],
        "days":Days
    }
    return jsonify(response)

@app.route('/output_monthly_cost_scenario/<month>',methods=["post"])
def output_monthly_cost_scenario(month):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    Days,Scenario_Monthly_Cost = OutputMonthlyCost("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month)
    response = {
        "month":int(month),
        "scenario1":Scenario_Monthly_Cost[0],
        "scenario2":Scenario_Monthly_Cost[1],
        "scenario3":Scenario_Monthly_Cost[2],
        "scenario4":Scenario_Monthly_Cost[3],
        "days":Days
    }
    return jsonify(response)

@app.route('/output_monthly_cost/<month>',methods=["post"])
def output_monthly_cost(month):
    data = request.get_json()
    Aitai = data["aitai_0"]
    Aitai2 = data["aitai_1"]
    Aitai3 = data["aitai_2"]
    Aitai4 = data["aitai_3"]
    AitaiM = Aitai["valuesDay"]
    AitaiN = Aitai["valuesNight"]
    Aitai2M = Aitai2["valuesDay"]
    Aitai2N = Aitai2["valuesNight"]
    Aitai3M = Aitai3["valuesDay"]
    Aitai3N = Aitai3["valuesNight"]
    Aitai4M = Aitai4["valuesDay"]
    Aitai4N = Aitai4["valuesNight"]
    Days,Aitai_Monthly_Cost = OutputMonthlyCost_1("decision","1year",AitaiM,AitaiN,Aitai2M,Aitai2N,Aitai3M,Aitai3N,Aitai4M,Aitai4N,month)
    response = {
        "month":int(month),
        "aitai1":Aitai_Monthly_Cost[0],
        "aitai2":Aitai_Monthly_Cost[1],
        "aitai3":Aitai_Monthly_Cost[2],
        "aitai4":Aitai_Monthly_Cost[3],
        "jepx_imbalance":Aitai_Monthly_Cost[4],
        "days":Days
    }
    return jsonify(response)

@app.route('/simulate_aitai_data',methods=["POST"])
def simulate_aitai_data():
    data=request.get_json()
    print("response")
    print(data)
    ave,co2=update_cost3(data)
    response = {
        "ave": ave,
        "co2": co2,
    }
    print(response)
    return jsonify(response)

@app.route('/multi_simulate_aitai_data',methods=["POST"])
def multi_simulate_aitai_data():
    data=request.get_json()
    print(data)
    response = {}
    for i in range(len(data)):
        ave,co2=update_cost3(data[i])
        response[i] = {
            "ave": ave,
            "co2": co2,
        }
    print(response)
    return jsonify(response)

@app.route('/get_aitai_data/<id>')
def get_aitai_data(id):
    id = int(id)
    Inputs = [["Input1","Input2","Input3"],[10.41126, 10.88141, 11.25195],[50965475.96, 45027889.15, 40345343.6],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[4000,4000,4000],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[13000,17000,20000],[11000,15000,19000],[5000,9000,17000],[0,0,0],[13000,17000,17000],[0,0,0],[16000,20000,20000],[9000,9000,9000],[13000,17000,20000],[11000,15000,20000],[13000,17000,20000],[0,0,0],[0,0,0],[0,1000,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[1000,0,0],[6000,7000,7000],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
    aitai_data_dict = {}
    aitai_data_length = len(Inputs) - 3
    aitai_company_id = 0
    while aitai_company_id < aitai_data_length // 24:
        values_dict = {}
        valuesDay = [x[id] for x in Inputs[3+aitai_company_id*24:3+aitai_company_id*24+12]]
        valuesNight= [x[id] for x in Inputs[3+aitai_company_id*24+12:3+aitai_company_id*24+24]]
        values_dict["valuesDay"] = valuesDay
        values_dict["valuesNight"] = valuesNight
        aitai_data_dict["aitai_" + str(aitai_company_id)] = values_dict
        aitai_company_id +=1
    return jsonify(aitai_data_dict)

@app.route('/get_csv')
def get_csv():
    csv_list = os.listdir(path='./data/csv/scenarios3')
    return jsonify(csv_list)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
