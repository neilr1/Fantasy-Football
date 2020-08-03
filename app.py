from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import pandas as pd
import itertools
import numpy as np
from patsy import dmatrices
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant
from sklearn.linear_model import LinearRegression
import csv


app = Flask(__name__,template_folder='templates')
app.config['MYSQL_USER'] = 'sql3356970'
app.config['MYSQL_PASSWORD'] = 'gAgxITG1pb'
app.config['MYSQL_HOST'] = 'sql3.freemysqlhosting.net'
app.config['MYSQL_DB'] = 'sql3356970'
app.config['MYSQL_CURSURCLASS'] = 'DictCursor'

mysql = MySQL(app)
table1 = ""
verifyAttributes = []


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        details = request.form
        query = details['statement']
        print(details)
        global table1
        table1 = details['table']
        cur = mysql.connection.cursor()
        row = cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        mysql.connection.commit()
        cur.close()
    return render_template('index.html')


@app.route('/scout_home',methods=['GET', 'POST'])
def scout_login():
    return "<h1> Scout Login </h1>"


@app.route('/commissioner_home',methods=['GET', 'POST'])
def commissioner_login():
    return "<h1> Commissioner Login </h1>"


@app.route('/results',methods=['GET', 'POST'])
def script_output():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM " + str(table1))
    rows = cur.fetchall()
    print(rows)
    cur.close()
    return render_template('results.html',output=rows,table=table1)


@app.route('/advanced',methods=['GET', 'POST'])
def advance():
    cur = mysql.connection.cursor()
    cur_two = mysql.connection.cursor()
    # if str(table) == "Players":
    output_one = cur.execute("Select count(p.PlayerID), t.wins From Players p, Teams t Where p.TeamName = t.TeamName AND p.height > 78 Group by t.TeamName")
    output_two = cur_two.execute("Select count(p.PlayerID), t.wins From Players p, Teams t Where p.TeamName = t.TeamName AND p.weight > 200 Group by t.TeamName")
    rows = cur.fetchall()
    row_two = cur_two.fetchall()
    print(rows)
    cur.close()
    cur_two.close()
    return render_template('advanced.html',output_one=rows,output_two=row_two)
if __name__ == 'main':
    app.run(debug=True)


@app.route('/simulation')
def simulation():
    #check to see if toggle button is either vif 
    attr_values = pd.read_csv("vif_model.csv")
    headers = []
    for col_name in attr_values.columns:
        headers.append(col_name)
    print(headers)
    #First change headers into a giant string with AVG(S.[each header in headers])
    #query using all players in nba team without nba players, players on the team
    #predict using that new player
    #store all the predictions
    #get the max prediction
    #get the player name
    data = pd.read_csv("NBARankings.csv")
    rankings = data["rankings"].values
    rankings = np.array(rankings)
   
    #build vif model using csv file and sklearn 
    x_values = attr_values.values.tolist()
    x_values = np.array(x_values)

    vif_lr = LinearRegression().fit(x_values, np.transpose(rankings))

    #add attributes to array 
   

    # attr_names = []
    

    # for i in range()



    


    #check to see if toggle button is either k_cross


@app.route('/drop')
def checkingToDropVariables():
    cur = mysql.connection.cursor()
    qu = 'SELECT AVG(S.FieldGoalAttempts), AVG(S.FieldGoalPercent), AVG(S.ThreePointAttempts), AVG(S.ThreePointPercent), AVG(S.TwoPointAttempts), AVG(S.TwoPointPercent), AVG(S.EFieldGoal), AVG(S.FreeThrowAttempts), AVG(S.FreeThrowPercent), AVG(S.Rebounds), AVG(S.Assists), AVG(S.Steals), AVG(S.Blocks), AVG(S.Turnovers), AVG(S.PersonalFouls), AVG(S.Points) FROM Teams T NATURAL JOIN Players P JOIN Statistics S ON (P.PlayerID = S.PlayerID) WHERE T.NumGames = 82 GROUP BY T.TeamName'
    output = cur.execute(qu)
    records = cur.fetchall()
    teamStats = {"FieldGoalAttempts": [], "FieldGoalPercent": [], "ThreePointAttempts": [], "ThreePointPercent": [], "TwoPointAttempts": [],
                "TwoPointPercent": [],"EFieldGoal": [],"FreeThrowAttempts": [],"FreeThrowPercent": [], "Rebounds": [],"Assists": [],
                "Steals": [],"Blocks": [], "Turnovers": [],"PersonalFouls": [], "Points": [] }
                
    for row in records:
        teamStats["FieldGoalAttempts"].append(row[0])
        teamStats["FieldGoalPercent"].append(row[1])
        teamStats["ThreePointAttempts"].append(row[2])
        teamStats["ThreePointPercent"].append(row[3])
        teamStats["TwoPointAttempts"].append(row[4])
        teamStats["TwoPointPercent"].append(row[5])
        teamStats["EFieldGoal"].append(row[6])
        teamStats["FreeThrowAttempts"].append(row[7])
        teamStats["FreeThrowPercent"].append(row[8])
        teamStats["Rebounds"].append(row[9])
        teamStats["Assists"].append(row[10])
        teamStats["Steals"].append(row[11])
        teamStats["Blocks"].append(row[12])
        teamStats["Turnovers"].append(row[13])
        teamStats["PersonalFouls"].append(row[14])
        teamStats["Points"].append(row[15])

    dataF = pd.DataFrame(teamStats, columns = ["FieldGoalAttempts", "FieldGoalPercent", "ThreePointAttempts", "ThreePointPercent", "TwoPointAttempts",
                "TwoPointPercent","EFieldGoal","FreeThrowAttempts","FreeThrowPercent", "Rebounds","Assists",
                "Steals","Blocks", "Turnovers","PersonalFouls", "Points"])
    
    fields = list(dataF.columns)
    correlationMatrix = dataF.corr()
    rows,cols = correlationMatrix.shape
    global verifyAttributes

    #Figure out which variables are under the suspicion of mulitcollinearity using correlation matrix
    for i in range(cols):
        for j in range(i, cols):
            if ((correlationMatrix[fields[i]][j] > 0.7 and correlationMatrix[fields[i]][j] < 1.0)
                or (correlationMatrix[fields[i]][j] < -0.7 and correlationMatrix[fields[i]][j] > -1.0)):
                verifyAttributes.append([fields[i], fields[j]])

    # Getting rid of duplicates from verifyAttributes
    temp = []
    for elem in verifyAttributes:
        if elem not in temp:
            temp.append(elem)
    verifyAttributes = temp
    cur.close()

    # Calculate which attributes have a high variance inflamation factor (VIF) value
    vifDrops = []
    if (len(verifyAttributes) > 0):
        while True:
            X = add_constant(dataF)
            vif = pd.Series([variance_inflation_factor(X.values, i) 
               for i in range(X.shape[1])], 
                index=X.columns)
            vif.drop('const', axis = 0, inplace=True)
            if (vif.max() > 5):
                theMax = vif.idxmax()
                vifDrops.append(theMax)
                dataF.drop(theMax, axis=1, inplace=True)
            else:
                break

    #csv file processing and write model to csv 
    for cur_drop in vifDrops:
        del teamStats[cur_drop]

    csv_labels = []
    csv_arr = []
    for i in teamStats:
        csv_arr.append(teamStats[i])
        csv_labels.append(i)

    csv_arr = np.array(csv_arr)
    csv_arr = np.transpose(csv_arr)

    with open('vif_model.csv', 'w', newline='') as file: 
        writer = csv.writer(file)   
        writer.writerows(csv_arr)

    df = pd.read_csv("vif_model.csv", header=None)
    attr_values = df.to_csv("vif_model.csv", header=csv_labels, index=False)

    r_values()
    return

def r_values():

    data = pd.read_csv('NBARankings.csv')
    rankings = data['rankings'].values
    matrix = []
    allAtributes = ["FieldGoalAttempts", "FieldGoalPercent", "ThreePointAttempts", "ThreePointPercent", "TwoPointAttempts",
                "TwoPointPercent","EFieldGoal","FreeThrowAttempts","FreeThrowPercent", "Rebounds","Assists",
                "Steals","Blocks", "Turnovers","PersonalFouls", "Points"]

    for elem in verifyAttributes:
        # CSV File matches with the results of this query based on alphabetical order
        cur = mysql.connection.cursor()
        output_one = cur.execute("SELECT AVG(S.%s) FROM Teams T NATURAL JOIN Players P JOIN Statistics S ON (P.PlayerID = S.PlayerID) WHERE T.NumGames = 82 GROUP BY T.TeamName ORDER BY T.TeamName" %elem[0])
        results_one = cur.fetchall()

        firstXValues = [x for [x] in results_one]
        firstCorrMatrix = np.corrcoef(firstXValues, rankings)
        firstRValue = firstCorrMatrix[0,1]
        print(elem[0], firstRValue)

        cur2 = mysql.connection.cursor()
        output_two = cur2.execute("SELECT AVG(S.%s) FROM Teams T NATURAL JOIN Players P JOIN Statistics S ON (P.PlayerID = S.PlayerID) WHERE T.NumGames = 82 GROUP BY T.TeamName ORDER BY T.TeamName" %elem[1])
        results_two = cur2.fetchall()

        secondXValues = [x for [x] in results_two]
        secondCorrMatrix = np.corrcoef(secondXValues, rankings)
        secondRValue = secondCorrMatrix[0,1]
        print(elem[1], secondRValue)

    return

@app.route('/kCross')
def machineLearning():

    allAtributes = ["FieldGoalAttempts", "FieldGoalPercent", "ThreePointAttempts", "ThreePointPercent", "TwoPointAttempts",
            "TwoPointPercent","EFieldGoal","FreeThrowAttempts","FreeThrowPercent", "Rebounds","Assists",
              "Steals","Blocks", "Turnovers","PersonalFouls", "Points"]
    allCombinations = []
    cur = mysql.connection.cursor()
    qu = 'SELECT AVG(S.FieldGoalAttempts), AVG(S.FieldGoalPercent), AVG(S.ThreePointAttempts), AVG(S.ThreePointPercent), AVG(S.TwoPointAttempts), AVG(S.TwoPointPercent), AVG(S.EFieldGoal), AVG(S.FreeThrowAttempts), AVG(S.FreeThrowPercent), AVG(S.Rebounds), AVG(S.Assists), AVG(S.Steals), AVG(S.Blocks), AVG(S.Turnovers), AVG(S.PersonalFouls), AVG(S.Points) FROM Teams T NATURAL JOIN Players P JOIN Statistics S ON (P.PlayerID = S.PlayerID) WHERE T.NumGames = 82 GROUP BY T.TeamName'
    output = cur.execute(qu)
    records = cur.fetchall()
    teamStats = {"FieldGoalAttempts": [], "FieldGoalPercent": [], "ThreePointAttempts": [], "ThreePointPercent": [], "TwoPointAttempts": [],
                "TwoPointPercent": [],"EFieldGoal": [],"FreeThrowAttempts": [],"FreeThrowPercent": [], "Rebounds": [],"Assists": [],
                "Steals": [],"Blocks": [], "Turnovers": [],"PersonalFouls": [], "Points": [] }
    
    #populuate attributes with data from database
    for row in records:
        teamStats["FieldGoalAttempts"].append(row[0])
        teamStats["FieldGoalPercent"].append(row[1])
        teamStats["ThreePointAttempts"].append(row[2])
        teamStats["ThreePointPercent"].append(row[3])
        teamStats["TwoPointAttempts"].append(row[4])
        teamStats["TwoPointPercent"].append(row[5])
        teamStats["EFieldGoal"].append(row[6])
        teamStats["FreeThrowAttempts"].append(row[7])
        teamStats["FreeThrowPercent"].append(row[8])
        teamStats["Rebounds"].append(row[9])
        teamStats["Assists"].append(row[10])
        teamStats["Steals"].append(row[11])
        teamStats["Blocks"].append(row[12])
        teamStats["Turnovers"].append(row[13])
        teamStats["PersonalFouls"].append(row[14])
        teamStats["Points"].append(row[15])
    data = pd.read_csv('NBARankings.csv')
    y = data['rankings'].values
    y = np.array(y)

    #Find all the combinations of different lengths of all attributes to create various models to insert into k-cross-validation
    for x in range(1, len(allAtributes) + 1):
        allCombinations.append(list(itertools.combinations(allAtributes, x)))

    #create array that will store model and associated score
    # [([model 1], score1), ([model 2], score2), ([model 3], score3)]
    model_scores = []
    for elem in allCombinations:  
        for combination in elem:

            x_vals_first_split_train = []  #10-30
            first_split_test = []  #0-10

            x_vals_second_split_train = [] #0-10 + 20-30
            second_split_test = []  #10-20

            x_vals_third_split_train = []  #0-20
            third_split_test = []  #20-30

            #extract data for all the combinations
            for attribute in combination:
                x_vals_first_split_train.append((teamStats[attribute])[10:30])
                first_split_test.append((teamStats[attribute])[0:10])

                temp_0_10 = teamStats[attribute][0:10]
                temp_20_30 = teamStats[attribute][10:20]
                temp_combined = []
                for i in range(10):
                    temp_combined.append(temp_0_10[i])
                for j in range(10):
                    temp_combined.append(temp_20_30[i])
                x_vals_second_split_train.append(temp_combined)
                second_split_test.append((teamStats[attribute])[10:20])

                x_vals_third_split_train.append((teamStats[attribute])[0:20])
                third_split_test.append((teamStats[attribute])[20:30])
            
            #make all y combinations
            y_1 = y[10:30]
            temp_1 = y[0:10]
            temp_2 = y[20:30]
            y_2 = np.concatenate((temp_1 , temp_2))
            y_3 = y[0:20]

            #make dataset compatable with numpy
            x_vals_first_split_train = np.array(x_vals_first_split_train)
            x_vals_second_split_train = np.array(x_vals_second_split_train)
            x_vals_third_split_train = np.array(x_vals_third_split_train)

            first_split_test = np.array(first_split_test)
            second_split_test = np.array(second_split_test)
            third_split_test = np.array(third_split_test)

            #make linear regression with train data
            lr_first_split_train = LinearRegression().fit(np.transpose(x_vals_first_split_train), np.transpose(y_1))
            lr_second_split_train = LinearRegression().fit(np.transpose(x_vals_second_split_train), np.transpose(y_2))
            lr_third_split_train = LinearRegression().fit(np.transpose(x_vals_third_split_train), np.transpose(y_3))

            sse_1 = 0
            #for every test point...
            for data_point_num in range(10):
                single_point = []
                for attrArr in first_split_test:
                    single_point_attribute = []
                    single_point_attribute.append(attrArr[data_point_num])
                    single_point.append(single_point_attribute)
                #once we have a point we want to predict, predict point
                single_point = np.array(single_point)
                # single_point = np.transpose(single_point)
                predicted_val = lr_first_split_train.predict(np.transpose(single_point))
                #find Squared Error of point and to sse
                actual_val = y[data_point_num] #0-10
                sse_1 += pow((actual_val - predicted_val), 2)
            
            #plot all predict points and find sse for second split
            sse_2 = 0
            for data_point_num in range(10): 
                single_point = []
                for attrArr in second_split_test:
                    single_point_attribute = []
                    single_point_attribute.append(attrArr[data_point_num])
                    single_point.append(single_point_attribute)
                single_point = np.array(single_point)
                predicted_val = lr_second_split_train.predict(np.transpose(single_point))
                idx = 10 + data_point_num
                actual_val = y[idx] #10-20
                sse_2 += pow((actual_val - predicted_val), 2)

            #plot all predict points and find sse for third split
            sse_3 = 0
            for data_point_num in range(10): 
                single_point = []
                for attrArr in third_split_test:
                    single_point_attribute = []
                    single_point_attribute.append(attrArr[data_point_num])
                    single_point.append(single_point_attribute)
                single_point = np.array(single_point)
                predicted_val = lr_third_split_train.predict(np.transpose(single_point))
                idx = 20 + data_point_num
                actual_val = y[idx] #20-30
                sse_3 += pow((actual_val - predicted_val), 2)

            avg_sse = (sse_1 + sse_2 + sse_3)/3
            model_scores.append([combination, avg_sse])
        
    #print at the end
    # [[[model 1], score1], [[model 2], score2], [[model 3], score3]]
    min = model_scores[0][1]
    min_arr = []
    myLen = len(model_scores)
    for cur_sse in range(myLen):
        if (model_scores[cur_sse][1] < min):
            min = model_scores[cur_sse][1]
            min_arr = model_scores[cur_sse][0]

    #csv file processing and write model to csv 
    drop_arr = []
    for i in allAtributes:
        if (i not in min_arr):
            drop_arr.append(i)

    for cur_drop in drop_arr:
        del teamStats[cur_drop]

    csv_arr = []
    for x in teamStats:
        csv_arr.append(teamStats[x])
    
    with open('kcross_model.csv', 'w', newline='') as file: 
        writer = csv.writer(file)   
        writer.writerows(csv_arr)

    return