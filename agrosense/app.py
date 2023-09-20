# This program is not considering race conditions !
# To understand what it does please refer to the README.md file
#
#
# IMPORTANT!!!
# 1. In order to use the code please register with Twilio - sendgrid https://signup.sendgrid.com/ create an account, register a domain, add DNS records and CREATE AN API KEY
# 2. Add the API KEY like this: export SENDGRID_API_KEY=<YOUR_API_KEY> in the app.py file
# If API KEY is not added the code will not run!
# 3. Navigate to the folder that contains the app.py file and run "flask run" ---> to run the web app!
# 4. Please notice you must make the port public and protocol HTTP. Check the image in the INTEL GALILEO section, step 3.
# 5. A sample code in the intel galileo board (Ardunio based board) please review the folder "Galileo"

import os
import time
import re
import io
import base64
import matplotlib.figure as mpl_fig

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
import secrets
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, emailwelcome, emailalarm, verify_api_key

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")

# Make sure Sendgrid API key is set
if not os.environ.get("SENDGRID_API_KEY"):
    raise RuntimeError("SENDGRID_API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show Summary and Graphs of temperature and humidity vs time for the last 7 days"""

    # emailwelcome('jdsuta@gmail.com')

    # get current timestamp in unix time
    now = int(time.time())
    # print(now)

    # convert unix timestamp to current timestamp. Human redable
    currentTime = datetime.fromtimestamp(now)
    # print( currentTime )

    # 1 week is equal to 604800 seconds. This value is going to be used to substract
    week = 604800

    Sevendays = now - week
    # print( Sevendays )

    weekaAgo = datetime.fromtimestamp(Sevendays)
    # print( weekaAgo )

    # Filter the DB by checking only the last 7 days.
    # Informationout of that range will be not sahred.
    # Additionally, the DB calculates the Average of temperature and humidity in the last 7 days

    device_summary = db.execute(
        "SELECT user_id, AVG(humidity) AS avghumidity, AVG(temperature) AS avgtemperature, device_name FROM device_history JOIN devices ON devices.id = device_history.device_id JOIN users ON users.id = device_history.user_id WHERE epoch_time BETWEEN ? AND ? AND users.id = ? GROUP BY device_name;",
        Sevendays,
        now,
        session["user_id"],
    )

    ##### CREATING GRAPHS ########

    # We collect the info for device_name, temperature, humidity and epoch_time. This data will be organized by device_name and then will be graph.

    data = db.execute(
        "SELECT device_name, temperature, humidity, epoch_time FROM device_history JOIN devices ON devices.id = device_history.device_id JOIN users ON users.id = device_history.user_id WHERE epoch_time BETWEEN ? AND ? AND users.id = ?;",
        Sevendays,
        now,
        session["user_id"],
    )

    # print(data)

    # Empty dictionary to allocate data for each device in the last 7 days. Data will be used to create graph
    dict_data = {}

    # Iterate over each entry in the data collected of the DB
    for element in data:
        device_name = element["device_name"]
        temperature = element["temperature"]
        humidity = element["humidity"]
        epoch_time = element["epoch_time"]

        # Convert epoch time to timestamp Human redable
        timestamp = datetime.fromtimestamp(epoch_time)

        # %b represents the abbreviated month name. For example, "Jul" represents July.
        # %d represents the day of the month. For example, "08" represents the 8th day of the month.
        timestamp = timestamp.strftime("%b-%d %H:%M:%S")

        # Check if the device name exists in the dictionary
        if device_name in dict_data:
            # If the device name exists, append the values to the existing list
            dict_data[device_name]["temperature"].append(temperature)
            dict_data[device_name]["humidity"].append(humidity)
            dict_data[device_name]["timestamp"].append(timestamp)

        else:
            # If the device name doesn't exist, create a new element in the dictionary
            dict_data[device_name] = {
                "temperature": [temperature],
                "humidity": [humidity],
                "timestamp": [timestamp],
            }

    print(dict_data)


    # CREATING GRAPHS
    # list to store graphs
    graphs = []

    # list to store device names
    devices_names = []

    for device_name, values in dict_data.items():
        devices_names.append(device_name)
        fig = mpl_fig.Figure()
        # It is not necessary in this case. However, "fig.add_subplot" helps to allocate the position of the graph and define the grid.
        ax = fig.add_subplot(111)
        ax.plot(values["timestamp"], values["temperature"], ".", label="Temperature")
        ax.plot(values["timestamp"], values["humidity"], ".", label="Humidity")
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Value")
        # Legen adds little square in the graph
        ax.legend()

        # Rotate x-axis labels vertically. So the graph doesn't look crowded in the X axis
        ax.set_xticklabels(ax.get_xticks(), rotation=90)

        # Set tick positions and labels explicitly. (The graph was cutting the values reason why I have to use this)
        x_ticks = range(len(values["timestamp"]))
        x_labels = [str(ts) for ts in values["timestamp"]]
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)

        # automatically adjusts the subplots and spacing of the figure to optimize the layout and ensure that all elements are properly visible.
        fig.tight_layout()

        # Save the figure to temporary space "buffer" in PNG.
        # The buffer.seek(0) like a pointer moves the file pointer to the beginning of the buffer
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)

        # Convert the figure to a base64-encoded string
        # The .decode('utf-8') part of the line converts the Base64-encoded data from bytes to a UTF-8 encoded string.
        # the resulting Base64 string is in bytes format.
        # if you want to use it in a context that expects a string, such as embedding it in HTML or displaying it, you need to decode it to a string using the appropriate character encoding, which is UTF-8 in this case.
        graph_base64 = base64.b64encode(buffer.read()).decode("utf-8")

        # Append the base64 string to the list of graphs
        graphs.append(graph_base64)

    # pass Device Summary and graph (last 7 days) to be iterated using JINJA
    return render_template(
        "index.html",
        device_summaryp=device_summary,
        current_timep=currentTime,
        weeka_agop=weekaAgo,
        device_graphs=graphs,
        device_namesp=devices_names,
    )


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Epoch time is used in the sql database. Therefore, the data is manipulated so it can be human readable in UTC
    # The datetime function in SQLite expects the input to be in seconds. For 10 digits you don't need to divide. However, for 13 digits epoch time you should divide epoch_time by 1000

    device_summary = db.execute(
        "SELECT user_id,  humidity, temperature, datetime(epoch_time, 'unixepoch', 'utc') AS time_utc, device_name FROM device_history JOIN devices ON devices.id = device_history.device_id JOIN users ON users.id = device_history.user_id WHERE users.id = ? ORDER BY epoch_time DESC LIMIT 50;",
        session["user_id"],
    )

    #print(device_summary)

    return render_template("history.html", device_summaryp=device_summary)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":
        # Ensure username was submitted not blank
        if not request.form.get("username"):
            return apology("must provide username", 400)
        usernameemail = request.form.get("username")

        # Ensure email was submitted not blank
        if not request.form.get("email"):
            return apology("must provide an email", 400)

        # Validates email follows a pattern
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._%+-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, request.form.get("email")):
            return apology(
                "Email must contain and @ symbol, a . and a top domain com, org, co.uk",
                400,
            )

        # Ensure email confrimation submitted not blank
        if not request.form.get("emailconfirmation"):
            return apology("must provide an email confirmation", 400)

        # Ensure email and confirmation email match
        elif request.form.get("email") != request.form.get("emailconfirmation"):
            return apology("Email and Email confirmation don't match", 400)

        # saves email as global to sent email afterwards
        global to_mail
        to_mail = request.form.get("email")

        # Ensure password was submitted not blank
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted not blank
        if not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        # Ensure password has minimum 8 characters including a number and a special character
        elif len(request.form.get("password")) <= 7:
            return apology("passwords must contain minimum 8 characters", 400)

        # Ensure password has a special character, lower case, capital letter and a number

        if (
            not re.search("[A-Z]", request.form.get("password"))
            or not re.search("[a-z]", request.form.get("password"))
            or not re.search("[!@#$%^&*()]", request.form.get("password"))
            or not re.search("[0-9]", request.form.get("password"))
        ):
            return apology(
                "password must contain at least one number and one uppercase and lowercase letter, a special char and at least 8 or more characters",
                400,
            )

        # Query database for username. To check if already exists
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # If result of the previous query is different than 0 it means the username already exists
        if len(rows) != 0:
            return apology("username is already taken", 400)

        else:
            # Hash the password to avoid store plain text passwords in the DB
            passworddb = generate_password_hash(request.form.get("password"))

            # Insert into the db the username, password hashed and the email. In summary, the username, password and email are created in the db
            db.execute(
                "INSERT INTO users (username, hash, email) VALUES (?,?,?);",
                request.form.get("username"),
                passworddb,
                to_mail,
            )

            # Recovers the data for the user that just registered from the DB
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )

            # Log the user in.
            # From that recovered data the ID is extracted to be stored in the session.
            session["user_id"] = rows[0]["id"]

        # sends welcome Email after registration
        emailwelcome(to_mail, usernameemail)

        # Redirect user to home page
        return redirect("/")

    # If the request is a GET
    else:
        return render_template("registration.html")


@app.route("/changepassword", methods=["GET", "POST"])
@login_required
def changepassword():
    """Change password user"""

    if request.method == "POST":
        # Username is not asked because user is already logged in
        # Ensure password was submitted not blank
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password confirmation was submitted not blank
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation password", 400)

        # Ensure password and password confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("password and confirmation don't match", 400)

        # Ensure password has minimum 8 characters including a number and a special character
        elif len(request.form.get("password")) <= 7:
            return apology("passwords must contain minimum 8 characters", 400)

        # Ensure password has a special character, lower case, capital letter and a number
        if (
            not re.search("[A-Z]", request.form.get("password"))
            or not re.search("[a-z]", request.form.get("password"))
            or not re.search("[!@#$%^&*()]", request.form.get("password"))
            or not re.search("[0-9]", request.form.get("password"))
        ):
            return apology(
                "password must contain at least one number and one uppercase and lowercase letter, a special char and at least 8 or more characters",
                400,
            )

        # hash the new password
        passworddb = generate_password_hash(request.form.get("password"))

        # updates the password in the DB using the session["user_id"]
        db.execute(
            "UPDATE users SET hash = ? WHERE id = ?;", passworddb, session["user_id"]
        )

        # Logs out the user so it can login again
        session.clear()

        # Redirect user to home page so it can login again
        return redirect("/")

    # If the request is a GET
    else:
        return render_template("changepassword.html")


@app.route("/changeemail", methods=["GET", "POST"])
@login_required
def changeemail():
    """Change email user"""

    if request.method == "POST":
        # Username is not asked because user is already logged in
        # Ensure password was submitted not blank
        if not request.form.get("email"):
            return apology("must provide email", 400)

        # Ensure password confirmation was submitted not blank
        elif not request.form.get("emailconfirmation"):
            return apology("must provide confirmation email", 400)

        # Validates email follows a pattern
        pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9._%+-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, request.form.get("email")):
            return apology(
                "Email must contain and @ symbol, a . and a top domain com, org, co.uk",
                400,
            )

        # Ensure email and email confirmation match
        elif request.form.get("email") != request.form.get("emailconfirmation"):
            return apology("email and email confirmation don't match", 400)

        newemail = request.form.get("email")

        # Updates the email in the DB using the session["user_id"]
        db.execute(
            "UPDATE users SET email = ? WHERE id = ?;", newemail, session["user_id"]
        )

        # Redirect user to home page so it can login again

        TextConfirmation = "Email was updated !"

        return render_template(
            "changeemail.html",TextConfirmationp = TextConfirmation
        )

    # If the request is a GET
    else:
        return render_template("changeemail.html")


@app.route("/create_apikey", methods=["GET", "POST"])
@login_required
def create_api_key():
    """Creates API KEY and devicename"""

    if request.method == "POST":
        # Ensure device name was submitted not blank
        devicename = request.form.get("devicename")
        if not devicename:
            return apology("must provide a Device Name", 400)

        # Consult the device_name along with the corresponding device_apikey in the devices table
        rows = db.execute("SELECT * FROM devices WHERE device_name = ?;", devicename)

        # if we got a dictionary in rows it means that devicename exists. Therefore it should give an error
        if len(rows) >= 1:
            devicenamedb = rows[0]["device_name"]
            # Ensure username exists and password is correct
            if devicename == devicenamedb:
                return apology(
                    "Invalid devicename. It should be unique try a different one", 403
                )

        api_key = secrets.token_hex(16)  # Generate a 16-character random string
        # print({"api_key": api_key})

        # hash the new api key before inserting it in the database
        apikeydb = generate_password_hash(api_key)
        # print(apikeydb)

        # insert the device_name along with the corresponding device_apikey in the devices table
        db.execute(
            "INSERT INTO devices (device_name, device_apikey) VALUES (?,?);",
            devicename,
            apikeydb,
        )

        # Grab the ID of the previously inserted device_name
        rows = db.execute("SELECT id FROM devices WHERE device_name = ?;", devicename)
        deviceId = int(rows[0]["id"])
        # print(deviceId)

        # Insert the userd_ID, along with the device_id in the DB device_assignments.
        # This table builds the relation between users and devices.

        db.execute(
            "INSERT INTO device_assignments (user_id, device_id) VALUES (?, ?);",
            session["user_id"],
            deviceId,
        )

        Text2 = '<span class="badge bg-success">Please store your <strong>DEVICE NAME</strong> and <strong>API KEY</strong> in a safe place. The API KEY will be shown *just* this time</span>'

        # Text2 = "Please store your 'DEVICE NAME' and 'API KEY' in a safety place. The API KEY will be shown *just* this time"
        Text = "Device Name:"
        Text3 = "API KEY:"

        return render_template(
            "apikey.html", devicenamep = devicename,  api_keyp=api_key, textp=Text, text2p=Text2, text3p = Text3
        )

    # If the request is a GET
    else:
        return render_template("apikey.html")


@app.route("/apidata", methods=["POST"])
def receive_data():
    """Receives API DATA from Intel Galileo"""
    # It should authenticate with devicename and API KEY created in the portal
    # I need to create a button when a user logs in to create an API KEY
    # That API key should be hashed and should be hashed and match with a user ID
    # reference https://blog.teclado.com/api-key-authentication-with-flask/

    if request.method == "POST":
        # 400 if the devicename is not provided in the headers
        if not request.headers.get("devicename"):
            return {"message": "must provide devicename"}, 400

        devicename = request.headers.get("devicename")

        # 400 if the API KEY is not provided in the headers
        if not request.headers.get("API-Key"):
            return {"message": "must provide API-KEY"}, 400

        api_key = request.headers.get("API-Key")
        # print(api_key)

        # API KEY and device name verification. Using verify_api_key function in the helpers library
        if not verify_api_key(api_key, devicename):
            return {"message": "Invalid devicename and/or API key"}, 401

        # Store the values of the variables captured by arduino.
        humidity = float(request.args.get("humidity"))
        temperature = float(request.args.get("temperature"))
        epoch_time = int(request.args.get("time"))

        # Prints the values
        print("Temperature:", temperature)
        print("Humidity:", humidity)
        print("time:", epoch_time)

        # Grab the device_ID using the devicename
        rows = db.execute("SELECT id FROM devices WHERE device_name = ?;", devicename)
        deviceId = int(rows[0]["id"])
        # print(deviceId)

        # Grab the user_ID using the deviceId
        rows = db.execute(
            "SELECT user_id FROM device_assignments WHERE device_id = ?;", deviceId
        )
        user_id = int(rows[0]["user_id"])
        print(user_id)

        rows = db.execute(
            "SELECT username FROM users WHERE id = ?;", user_id
        )
        username = rows[0]["username"]

        # insert the user_id, device_id, temperature, humidity and time
        db.execute(
            "INSERT INTO device_history (user_id, device_id, humidity, temperature, epoch_time) VALUES (?, ?, ? ,? ,?);",
            user_id,
            deviceId,
            humidity,
            temperature,
            epoch_time,
        )

        if temperature >= 35 or temperature <= 10 or humidity >= 70 or humidity <= 30:
            rows = db.execute("SELECT email FROM users WHERE id = ?;", user_id)
            emailaddress = rows[0]["email"]
            #Send email alarming a value is out of range
            emailalarm(emailaddress, username, devicename, temperature, humidity)

        return "Data received"
