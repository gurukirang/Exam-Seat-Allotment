from flask import Flask, render_template, url_for, request, Response
import pandas as pd
import itertools
import random
import sqlite3
connection = sqlite3.connect('DataBase.db')
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(roll TEXT, password TEXT, mobile TEXT, email TEXT)"""
cursor.execute(command)

import pandas as pd
import os

# Function to search for the roll number in multiple CSV files
def search_roll_no(roll_no, csv_folder):
    results = []
    # Loop through all files in the folder
    for file_name in os.listdir(csv_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(csv_folder, file_name)
            # Read the CSV file into a DataFrame
            df = pd.read_csv(file_path)
            
            # Search for the roll number in the DataFrame
            matched_rows = df[df['Roll_num'] == roll_no]
            
            # If there are matching rows, store them along with the file name
            if not matched_rows.empty:
                results.append(file_name)
                results.append(matched_rows.values[0])
                break
    
    return results
    
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    if request.method == 'POST':

        name = request.form['name']
        password = request.form['password']

        if name == 'admin' and password == 'admin':
            return render_template('adminlog.html', msg='Successfully login')
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')
    return render_template('index.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':

        connection = sqlite3.connect('DataBase.db')
        cursor = connection.cursor()

        roll = request.form['roll']
        password = request.form['password']

        query = "SELECT * FROM user WHERE roll = '"+roll+"' AND password= '"+password+"'"
        cursor.execute(query)

        result = cursor.fetchall()

        if result:
            # Specify the folder containing your CSV files and the roll number to search
            csv_folder = 'csv'
            roll_no_to_search = roll

            # Search for the roll number
            matched_results = search_roll_no(roll_no_to_search, csv_folder)

            # Display the results
            if matched_results:
                file_name = matched_results[0].replace('_', ' ')
                file_name=file_name.replace('.csv', '')
                return render_template('userlog.html', rows=matched_results[1], result=result[0], file_name=file_name)
            else:
                print("Roll number not found in any file.")
                return render_template('userlog.html', msg="Roll number not found in any file.")
        else:
            return render_template('index.html', msg='Sorry, Incorrect Credentials Provided,  Try Again')

    return render_template('index.html')


@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':

        connection = sqlite3.connect('DataBase.db')
        cursor = connection.cursor()

        roll = request.form['roll']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        cursor.execute("INSERT INTO user VALUES ('"+roll+"', '"+password+"', '"+mobile+"', '"+email+"')")
        connection.commit()


        return render_template('index.html', msg='Successfully Registered')
    
    return render_template('index.html')

@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if request.method == 'POST':

        file1 = request.form['file1']
        file2 = request.form['file2']
        file3 = request.form['file3']
        file4 = request.form['file4']
        file5 = request.form['file5']

        cs = pd.read_csv(file1)
        ee = pd.read_csv(file2)
        cv = pd.read_csv(file3)
        mc = pd.read_csv(file4)
        tl = pd.read_csv(file5)

        nm = tl['Lecturer_name']
        List = []
        for n in nm:
            List.append(n)
        LecturerList = random.sample(List, 16)
        csn = cs['Student_name']
        csr = cs['Roll_num']

        een = ee['Student_name']
        eer = ee['Roll_num']

        cvn = cv['Student_name']
        cvr = cv['Roll_num']

        mcn = mc['Student_name']
        mcr = mc['Roll_num']

        names = []
        roll = []
        bench = []

        total = int(len(een)+len(csn)+len(cvn)+len(mcn))
        for i in range(1, total+1):
            bench.append('BN{:04}'.format(i))

        for  i in range(int(len(csn)/5)):
            st = 5*i
            sp = 5*(i+1)
            
            for i in csn[st:sp]:
                names.append(i)

            for i in een[st:sp]:
                names.append(i)
            
            for i in cvn[st:sp]:
                names.append(i)

            for i in mcn[st:sp]:
                names.append(i)

            for i in csr[st:sp]:
                roll.append(i)

            for i in eer[st:sp]:
                roll.append(i)
            
            for i in cvr[st:sp]:
                roll.append(i)

            for i in mcr[st:sp]:
                roll.append(i)
                
        col1=[]
        col2=[]
        col3=[]

        print(len(names), len(roll), len(bench))
        
        for i in range(int(len(bench)/25)):
            st = 25*i
            sp = 25*(i+1)
            for a, b , c in zip(bench[st:sp], roll[st:sp], names[st:sp]):
                col1.append(a)
                col2.append(b)
                col3.append(c)
            
            dict = {'Invigilator':LecturerList[i],'Bench_num':col1,'Roll_num': col2, 'Student_name':col3}
            df = pd.DataFrame(dict)
            df.to_csv('csv/Room_{}.csv'.format(i+1))
            num = int(len(bench))
      
        return render_template('adminlog.html',  Bench_num=bench, Roll_num=roll, Student_name=names, Num=num, LecturerList=LecturerList)

    return render_template('adminlog.html')

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
