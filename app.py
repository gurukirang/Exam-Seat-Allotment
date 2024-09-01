from flask import Flask, render_template, request, flash, redirect
import pandas as pd
import os
import random
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with your actual secret key for flash messages

# Initialize the database
connection = sqlite3.connect('DataBase.db', check_same_thread=False)
cursor = connection.cursor()

command = """CREATE TABLE IF NOT EXISTS user(
                roll TEXT, 
                password TEXT, 
                mobile TEXT, 
                email TEXT)"""
cursor.execute(command)
connection.commit()

# Function to search for the roll number in multiple CSV files
def search_roll_no(roll_no, csv_folder):
    results = []
    for file_name in os.listdir(csv_folder):
        if file_name.endswith('.csv'):
            file_path = os.path.join(csv_folder, file_name)
            df = pd.read_csv(file_path)
            matched_rows = df[df['Roll_num'] == roll_no]
            if not matched_rows.empty:
                results.append(file_name)
                results.append(matched_rows.values[0])
                break
    return results

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']

        if name == 'admin' and password == 'admin':
            return render_template('adminlog.html', msg='Successfully logged in')
        else:
            flash('Incorrect Credentials. Try Again', 'error')
            return render_template('index.html')
    return render_template('index.html')

@app.route('/userlog', methods=['GET', 'POST'])
def userlog():
    if request.method == 'POST':
        roll = request.form['roll']
        password = request.form['password']

        query = "SELECT * FROM user WHERE roll = ? AND password= ?"
        cursor.execute(query, (roll, password))
        result = cursor.fetchall()

        if result:
            csv_folder = 'csv'
            matched_results = search_roll_no(roll, csv_folder)

            if matched_results:
                file_name = matched_results[0].replace('_', ' ').replace('.csv', '')
                return render_template('userlog.html', rows=matched_results[1], result=result[0], file_name=file_name)
            else:
                flash("Roll number not found in any file.", 'error')
                return render_template('userlog.html')
        else:
            flash('Incorrect roll number or password.', 'error')
            return render_template('index.html')
    return render_template('index.html')

@app.route('/userreg', methods=['GET', 'POST'])
def userreg():
    if request.method == 'POST':
        roll = request.form['roll']
        password = request.form['password']
        mobile = request.form['phone']
        email = request.form['email']

        cursor.execute("INSERT INTO user VALUES (?, ?, ?, ?)", (roll, password, mobile, email))
        connection.commit()

        flash('Successfully Registered', 'success')
        return render_template('index.html')
    return render_template('index.html')

@app.route('/allocate', methods=['GET', 'POST'])
def allocate():
    if request.method == 'POST':
        try:
            # Get the uploaded files
            file1 = request.files.get('file1')
            file2 = request.files.get('file2')
            file3 = request.files.get('file3')
            file4 = request.files.get('file4')
            file5 = request.files.get('file5')

            # Check if all files are provided
            if not all([file1, file2, file3, file4, file5]):
                flash('All five files are required for allocation.', 'error')
                return redirect(request.url)

            # Save the uploaded files to a temporary directory
            file_paths = []
            for file in [file1, file2, file3, file4, file5]:
                file_path = os.path.join('temp_uploads', file.filename)
                file.save(file_path)
                file_paths.append(file_path)

            # Process the CSV files
            cs = pd.read_csv(file_paths[0])
            ee = pd.read_csv(file_paths[1])
            cv = pd.read_csv(file_paths[2])
            mc = pd.read_csv(file_paths[3])
            tl = pd.read_csv(file_paths[4])

            # Lecturer assignment and seat allocation logic
            nm = tl['Lecturer_name']
            List = [n for n in nm]
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

            total = int(len(een) + len(csn) + len(cvn) + len(mcn))
            for i in range(1, total + 1):
                bench.append('BN{:04}'.format(i))

            for i in range(int(len(csn) / 5)):
                st = 5 * i
                sp = 5 * (i + 1)
                names.extend(csn[st:sp])
                names.extend(een[st:sp])
                names.extend(cvn[st:sp])
                names.extend(mcn[st:sp])
                roll.extend(csr[st:sp])
                roll.extend(eer[st:sp])
                roll.extend(cvr[st:sp])
                roll.extend(mcr[st:sp])

            col1 = []
            col2 = []
            col3 = []

            for i in range(int(len(bench) / 25)):
                st = 25 * i
                sp = 25 * (i + 1)
                for a, b, c in zip(bench[st:sp], roll[st:sp], names[st:sp]):
                    col1.append(a)
                    col2.append(b)
                    col3.append(c)

                data = {'Invigilator': LecturerList[i], 'Bench_num': col1, 'Roll_num': col2, 'Student_name': col3}
                df = pd.DataFrame(data)
                df.to_csv(f'csv/Room_{i + 1}.csv', index=False)

            flash('Seat allocation successful!', 'success')
            return render_template('userlog.html')

        except Exception as e:
            # Handle errors and provide feedback to the user
            flash(f'An error occurred: {str(e)}', 'error')
            return redirect(request.url)

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('temp_uploads'):
        os.makedirs('temp_uploads')
    app.run(debug=True)
