# IoT + Web App - Monitor of Temperature and Moisture of plants

#### Video Demo:  <URL HERE>

#### Technology used:

1. *Back End (BE)*: Python with Flask, Sendgrid API for email communication.
2. *Front End (FE)*: HTML, JavaScript, Bootstrap.
3. *Device*: Intel Galileo, an Arduino-certified development board based on Intel x86
architecture. It is programmed using the Arduino interface to collect and send data
to the web server.


#### Description:

AgroSense is an Internet of Things (IoT) application designed to collect and monitor data such as temperature, humidity, and time from plants. It utilizes an Arduino-based board (Intel Galileo) to gather this data and transmit it to a web application for processing.

In a nutshell, the workflow of AgroSense is as follows:

1. Users register on the AgroSense web app. Upon registration, a welcome email is sent to the user.

2. Users can create a unique "device name" and an API key for identification.

3. The Intel Galileo board captures temperature, moisture, and time data, sending it as a POST request to the web server.

4. The POST request headers include the "device name," API key, and the relevant endpoint.

5. The web server receives and processes the data.

The web application displays a summary of the last 7 days, presenting the average temperature and humidity in a table format. Additionally, it generates graphs that depict the variation of temperature and humidity over time for each device.

Data is collected by the Intel Galileo board and transmitted to the web server every 5 minutes. If the recorded temperature or humidity falls outside a predefined range, an alert email is automatically sent to the email address associated with the device. This feature acts as an "alarm email."

AgroSense also offers the capability for individuals to create and send data to the web server via API. Users can then access and review the results by logging into the web application.

---

##### Route: **/register**

##### Template: `registration.html`

The register page requests users to input a _username, email, email confirmation, password, and password confirmation_ in a form. These inputs are evaluated in HTML, JavaScript, and the backend. If all conditions are met, the database is updated.

__Conditions for the Page:__

1. If it's a GET request, the 'register.html' page will load.

2. All requested fields must not be empty, making them mandatory. These conditions are evaluated in the backend (__app.py__). In the HTML template, all fields are marked as required.

3. The username field should be unique. If another user has registered with the same username, an error will be returned.

4. The email field should meet specific conditions to be valid, such as containing an '@' symbol between two words, followed by a '.' and a top-level domain like '.com' or '.org'. This validation is performed in both the backend[^1] and HTML[^2] template.The email and email confirmation must match; otherwise, an error will be displayed.

5. The password field must meet the following criteria:

    - Contains an uppercase letter
    - Contains a lowercase letter
    - Contains a number
    - Contains a special character (excluding space)
    - Minimum length of 8 characters

    JavaScript[^3] is utilized to provide visual guidance to users as they fill in the password field. As the user starts typing, the page displays indicators in red to show missing criteria. For instance, if an uppercase letter is missing, the page will indicate so until it's provided. This approach helps guide users effectively.

    The password and password confirmation must match; otherwise, an error will be shown. Backend validation (app.py) handles this, and both password and confirmation are masked.

6.  Once the user has completed all required fields, they can click the "Register" button. This action sends a POST request to the backend (__`app.py`__) at the __`/register`__ route. All fields are evaluated as outlined in previous points.

    If conditions are met, the web server hashes the password to enhance security against potential data breaches. The hashed password, along with the username and email, are stored in the 'users' table. Additionally, the user's ID is stored in the session, indicating successful login.

7. All database queries employ "?" placeholders to prevent SQL injection attacks.

8.  A welcome email is dispatched to the registered email address. The `emailwelcome`
    function in the `helpers.py` library is used for this purpose. The welcome email includes
    the 'username' and 'email address' registered during the sign-up process.

    Below is a sample of the welcome email:

    ![Welcome Email](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Welcome_email.png)

    For more details on how emails work, refer to the [email](https://github.com/code50/76489568/tree/main/week10/project#email) section below.

9. Subsequently, the user is redirected to the home page ('/').

[^1]: https://stackoverflow.com/questions/37091415/python-regular-expression-re-searchra-za-z0-9-password
[^2]: https://www.w3schools.com/tags/att_input_pattern.asp
[^3]: https://www.w3schools.com/JSREF/prop_html_innerhtml.asp

---

##### Route: **/login**

##### Template: `login.html`

The login page requests users to input a _username_ and _password_ in a form. Users should have registered previously on the page to use the login section. Both username and password fields are required in the 'login.html' form and are sent to the backend via a 'POST' request.

__Conditions for the Page:__

1. The web server ensures that both _username_ and _password_ fields are not empty. These fields are mandatory for login.

2. After the form is submitted to the backend, the web server queries the users database using the provided _username_. It validates that the username exists in the database. It then compares the provided password with the stored password using the `check_password_hash` function.

    If the username doesn't exist or the provided password doesn't match the stored password, an error is returned.

3. If both conditions are successfully met, the user's ID is stored in the session, indicating that the user is now logged in. Subsequently, the page is redirected to the home page ('/').

---

##### Route: **/**

##### Template: `index.html`

The index page showcases a summary by calculating the average values of temperature and humidity over the last 7 days for each registered device. Furthermore, it generates graphs illustrating the relationship between temperature and humidity against time for the data collected within the past 7 days. In the event that a user has multiple devices registered, a graph is created for each one.

__Conditions for the Page:__

1.  To compute a period of seven days, a function retrieves the current time [^4] in Unix time format. The current time in seconds is obtained, and a 7-day period (1 week) is converted into seconds. This value remains constant. To determine the precise date 7 days ago, the constant value representing 7 days is subtracted from the current time.

    Subsequently, the database containing temperature and humidity values is queried using Unix timestamps (current time and time 7 days ago) along with the user ID obtained during login.

    The query calculates average humidity and temperature values while also fetching the corresponding device names. These values are displayed in a compact table on the webpage:

    ![Table average temperature and humidity](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Summary7days.png)



2.  Graphs are generated using humidity, temperature, and Unix time data
    within a week-long timeframe. This data is retrieved through database
    queries. The data is structured in a nested dictionary. The outer
    dictionary employs the device name as the key, while the inner
    dictionaries store values for temperature, humidity, and timestamps. Unix time is converted into a human-readable time format. Each inner dictionary comprises lists of corresponding values.

    Example:

    ```
    {'test_apikey': {'temperature': [25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 25.5, 21.0, 20.02, 17.09, 17.58, 18.55, 19.04, 19.04, 20.51, 21.0, 21.0, 21.0, 21.0, 21.0, 21.0, 21.48, 21.97, 21.48, 21.97, 21.48, 21.97], 'humidity': [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.0, 54.0, 54.0, 55.0, 54.0, 54.0, 54.0, 54.0, 53.0, 6.0, 64.0, 63.0, 64.0, 64.0, 63.0, 64.0, 67.0, 67.0, 67.0, 67.0, 67.0, 67.0, 72.0, 9.0, 54.0, 55.0, 54.0, 12.0, 6.0], 'timestamp': ['Aug-02 10:01:14', 'Aug-02 10:01:59', 'Aug-02 10:01:33', 'Aug-02 10:02:00', 'Aug-02 10:02:30', 'Aug-02 10:03:00', 'Aug-02 10:03:08', 'Aug-02 10:03:54', 'Aug-02 10:08:49', 'Aug-02 10:13:49', 'Aug-02 10:18:49', 'Aug-02 10:23:49', 'Aug-02 10:28:49', 'Aug-02 10:33:49', 'Aug-02 10:38:49', 'Aug-02 10:43:49', 'Aug-03 15:04:30', 'Aug-03 15:09:25', 'Aug-03 15:14:25', 'Aug-03 15:19:25', 'Aug-03 15:24:25', 'Aug-03 15:29:25', 'Aug-03 15:34:25', 'Aug-03 15:39:25', 'Aug-03 15:44:25', 'Aug-03 15:49:25', 'Aug-03 15:59:25', 'Aug-03 16:04:25', 'Aug-03 16:09:25', 'Aug-03 16:14:25', 'Aug-03 16:15:42', 'Aug-04 14:10:48', 'Aug-04 14:18:34', 'Aug-04 14:23:29', 'Aug-04 14:27:41', 'Aug-04 14:32:36']}}
    ```


    The X-axis represents time, while the Y-axis uses humidity values in %RH (displayed as orange data points) and temperature in °C (displayed as blue data points) within a single graph. These graphs are generated using the Python Matplotlib library. [^5]

    Here an example:
    ![Temperature/Humidity VS Time](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-TempHum_vs_time.png)

3. The graph is then passed to the HTML and rendered using Jinja templating, creating a dynamic visual representation of the temperature and humidity trends over the past 7 days.


[^4]: https://www.javatpoint.com/python-epoch-to-datetime and https://www.tutorialspoint.com/python/time_time.htm

[^5]: https://matplotlib.org/stable/gallery/user_interfaces/web_application_server_sgskip.html

---

##### Route: **/create_apikey**

##### Template: `apikey.html`

The 'apikey' page enables users to create a unique API Key for their devices, such as Galileo and Arduino boards. The device name and API Key are crucial for identifying devices and facilitating data posting to the web server. In essence, the _device name_ and _API Key_ act as a username and password combined, used by devices whenever they make requests to the server's endpoints to transmit data such as time, temperature and humidity readings.

__Conditions for the Page:__

1. The HTML page necessitates input for the 'Device Name' field. Both the HTML form and the web server ensure that this field is not left empty. If the 'Device Name' field is submitted empty, an error message is displayed to the user.

2. The 'device name' entered by the user is used to query the 'devices' table for existing entries with the same device name. If results are found, it indicates that the device name is already in use. Given that device names are expected to be unique, the web server returns an error message to prevent duplication.

3. In the case where the device name does not already exist, the system proceeds to create an API Key consisting of 16 alphanumeric characters. This API Key is generated using the Python secrets library.[^6]

4. Following the API Key creation, it is hashed before being stored in the 'devices' table. This hashing process enhances security, particularly in the event of a potential data breach. In essence, the 'devices' table stores both the 'device name' and its corresponding hashed API Key.

5. Subsequently, the system captures the ID of the newly inserted device. This step is crucial for establishing a relationship between the 'device name', the 'API Key', and the users. This relationship serves to associate devices like Galileo boards with their respective owners. The 'device_assignments' table is employed for this purpose.


6. Finally, the system displays the 'Device Name' and the generated API Key to the user. The user is advised to store this information securely, as it will be required for device authentication. The presentation resembles the following:


    ![Device name and Api Key being shown](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Device_apikey.png)


[^6]: https://docs.python.org/3/library/secrets.html


---

##### Route: **/apidata**

The 'apidata' __endpoint__ serves as the gateway through which Galileo or Arduino boards can transmit data (such as Temperature, Humidity, and Epoch time) to the web server. This data is sent via a POST request, and it requires inclusion of the 'Device Name' and 'API Key' in the headers of the request. The web server then processes the data, provided that the API Key and device name authentication are valid.

__Conditions for the Route:__

1. The headers of the API call must include the 'device name' and 'API Key'. Failure to provide this information results in the generation of an error response.

2. The 'device name' and 'API Key' are subsequently validated using the 'verify_api_key' function from the helpers library. The function carries out a query on the 'devices' table to verify the existence of the specified 'device name'. Additionally, it checks whether the provided API Key matches the corresponding 'hashed apikey' using the 'check_password_hash' function. Should the 'device name' not exist or the API Key be invalid, an error message is returned.

3. Upon successful verification, the received data—comprising temperature, humidity, and epoch time—is stored in the system. This is achieved by first retrieving the 'deviceId' from the 'devices' table. Subsequently, the 'user_ID' is obtained using the 'deviceId' from the 'device_assignments' table. The collected values, including 'userId', 'deviceId', 'temperature', 'humidity', and 'epoch_time', are stored in the 'device_history' table.

4. The 'apidata' endpoint incorporates data evaluation as part of its functionality. Should the temperature value fall outside the specified range, an Alarm Email is automatically dispatched. This email includes the _username, device name, along with the temperature and humidity values_.

    Specifically, an email will be sent if the temperature is either greater than or equal to 35°C, or less than or equal to 10°C.

    Similarly, if humidity exceeds 70% or falls below 30% RH, an alarm email will be triggered to notify the user.

    This alarming mechanism aims to ensure that users are promptly informed of any critical variations in the monitored conditions.

    Here is a sample of the email:

    ![Alarm Email](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Alarm_email.png)

5. Concluding its operations, the 'apidata' endpoint responds with a message indicating "Data Received" once all the necessary validations and processes have been successfully completed.

---

##### Route: **/history**

##### Template: `history.html`


The 'history' page provides an overview of the 50 most recent data requests submitted by various devices. This information is acquired through a query that employs the user's userId, who is currently logged in. Utilizing the 'device_history', 'devices', and 'users' tables, the query arranges the data in ascending order based on epoch time. Furthermore, it applies a conversion to render the time in human-readable format, presented in Coordinated Universal Time (UTC).

Upon retrieval, the data is transmitted to the 'history.html' HTML template. Within this template, the JINJA 'for loop' syntax is employed, enabling seamless iteration through the collected data. Consequently, the webpage furnishes an organized representation of the data, as depicted below:

![History page](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-History.png)


---

##### Route: **/changeemail**

##### Template: `changeemail.html`


The 'changeemail' page offers users the capability to modify their registered email address and save the updated information within the database. This feature requires users to input their desired email address along with a confirmation of the new email.

__Conditions for the Route:__

1. The web server enforces a validation check to ensure that the 'email' and 'email confirmation' fields are not submitted empty. This precautionary step is imperative, as even though the HTML fields are mandated, it's vital to reinforce this validation on the server-side to prevent any possible circumvention.

2. The system then employs a validation mechanism that enforces adherence to the accepted email format, which entails the presence of an '@' symbol sandwiched between two terms, followed by a '.' symbol and a top-level domain suffix (e.g., '.com', '.org', etc.). This validation process is done in both the backend and the HTML template. Additionally, it mandates that the input provided for 'email' and 'email confirmation' must match precisely. Otherwise, the web server will issue an error response.

3. After successfully passing these stages of validation, the web server executes the email update operation. This includes modifying the email entry within the SQL 'users' table to reflect the newly provided email address.

    A visual representation of the page can be observed below:

    Sample of the page:

    ![Update email](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-ChangeEmail.png)


---

##### Route: **/changepassword**

##### Template: `changepassword.html`

The 'changepassword' page empowers users to modify their account password and subsequently save the updated password within the database. To execute this operation, users are required to provide both their new password and a confirmation of the new password.

__Conditions for the Route:__

1.  The web server confirms that the 'password' and 'password confirmation' fields have not been submitted as empty. Although these fields are obligatory within the HTML form, it remains imperative to check the validation process on the server side to counteract any potential attempts at circumvention.

2.  Following this, the system enforces a comparison between the 'password' and 'password confirmation' fields to ensure that they match. Any discrepancy between these fields triggers an error response.

3.  Password criteria are strictly enforced and must comply these conditions:

    - Minimum length of 8 characters
    - Inclusion of at least one capital letter
    - Inclusion of at least one lowercase letter
    - Inclusion of at least one special character (excluding spaces)
    - Inclusion of at least one numerical digit

    These password conditions are evaluated on the HTML side and supported by JavaScript to provide user guidance. However, even if these conditions are bypassed, the backend confirms their fulfillment. Failure to meet these requirements will generate an error message, indicating that the user must follow the criteria

3. Once the user's new password adheres to the conditions, the new password is hashed, and the web server updates the password entry within the SQL 'users' table.

4.  Subsequent to the successful password update, the user is logged out automatically and redirected to the login page. This step ensures that the user is required to log in again using their updated password.

    Sample of the page:

    ![Update password](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-ChangePassword.png)


---

##### Route: **/logout**

The 'logout' route serves the purpose of clearing the stored user ID and redirecting the user to the home page, where they can initiate the login process once again.

---

### EMAIL

The web application seamlessly integrates with the Twilio SendGrid API to facilitate email communication via an API. This integration serves two primary functions:

1. __Welcome Email:__ When users register for the web application for the first time, a personalized 'welcome email' is sent using the SendGrid API. This email is designed to provide a warm introduction to the platform.

2. __Alarm Email:__ The application is equipped to send 'alarm emails' when temperature and humidity values fall outside the predefined acceptable range. This functionality aims to promptly notify users of anomalous conditions.

To utilize SendGrid, the following steps are required:

1. __Account Creation__: Set up an account with Twilio SendGrid[^7].
2. __API Key Generation:__ Create an API key [^8] that will be integrated into the application.
3. __Dynamic Templates:__ Develop dynamic email templates [^9] for both the welcome and alarm emails. These templates support personalized content using Handlebars expressions (e.g., `{{username}}`, `{{temperature}}`, `{{humidity}}`) [^10].

    Here is an example of the dynamic template configuration in SendGrid:

    ![Handlebars](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Handlebars.png)

To build emails, the Python documentation [^11] was consulted. The helper library uses these concepts to construct and send emails, incorporating dynamic data:

```
...
    message.dynamic_template_data = {
        'username' : username,
        'devicename': devicename,
        'temperature': temperature,
        'humidity': humidity
    }
...
```

Before utilizing these features, ensure that you install the required SendGrid packages and dependencies[^12] within your Flask environment.

__Note:__ If you plan to implement this web application, it is crucial to add your SendGrid API key before use in the web server. Otherwise an error will be raised.

[^7]: https://signup.sendgrid.com/
[^8]: https://docs.sendgrid.com/ui/account-and-settings/api-keys#creating-an-api-key
[^9]: https://docs.sendgrid.com/ui/sending-email/how-to-send-an-email-with-dynamic-templates#design-a-dynamic-template
[^10]: https://docs.sendgrid.com/for-developers/sending-email/using-handlebars#substitution
[^11]: https://docs.sendgrid.com/api-reference/mail-send/mail-send
[^12]: https://github.com/sendgrid/sendgrid-python

---

### INTEL GALILEO

Intel Galileo, an Arduino-certified development board based on Intel x86 architecture, is utilized to capture temperature and humidity data. This data is then sent to the web server via a POST request. Here is a concise breakdown of the integration process and logic:

1. __Platform Overview:__ Intel Galileo boards are programmed using the Arduino interface and rely on Ethernet connectivity. To enable communication between Galileo and the web server, an intermediary service (Pipedream) is used to relay data from Galileo to the server.

2. __Workflow:__

    - Galileo captures time, temperature and humidity data using connected sensors (LM35 for temperature and moisture sensor for humidity).
    - Data is sent via a POST request to Pipedream, including the 'device name' and 'API Key' in headers for authentication.
    - Pipedream forwards the data to the web server's specified endpoint (/apidata).
    - Web server processes the received data, storing it in the database.

3. To make this communication possible, port forwarding is configured in GitHub Codespaces to allow external devices to communicate with the web server. Detailed guidance is provided here: [Access APIs in Github codespaces vis Postman or cURL](https://www.returngis.net/2023/03/acceder-a-apis-ejecutandose-en-github-codespaces-a-traves-de-rest-client-postman-o-curl/)

    You can see an image here on how to make public the port of github codespaces:

    ![Port forwarding](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-PortForwarding.png)

4. __Galileo/Arduino Logic__:

    The logic governing Intel Galileo integration is written in the Arduino programming language, a variant of C++. To connect sensors and gather data, the following steps are involved:

    1. __Library and Variable Setup:__ Begin by importing necessary libraries and defining variables such as MAC address, IP address of the Galileo, server details (Pipedream), NTP server, and pin numbers for temperature and humidity sensors. Variables to manage data collection intervals and time tracking are also initialized.

    2. `void setup()`: In this section:

        - Initialize the Ethernet port and establish a connection using DHCP or a static IP.
        - Begin serial communication.
        - Configure NTP client and fetch initial timestamp from "pool.ntp.org".
        - Perform an initial POST request by calling sendPostRequest() to start data transmission.

    3. `sendPostRequest()`: This function initiates a connection between the Galileo (client) and the server (Pipedream) on port 80, using HTTP for communication. While HTTPS is a more secure choice, its implementation on the Galileo was challenging due to library constraints. Connecting to the server involves the following steps:

        - Obtain the current Unix time from the NTP server and store it for timestamping.
        - Collect data from sensors:
            - Moisture Sensor (Pin A0): Calibrate by capturing analog readings when submerged (100% RH) and dry (0% RH). Use the mapped values to calculate and store humidity data.
            - Temperature Sensor (Pin A1): Use an LM35 sensor to capture temperature data. Convert this data to Celsius and then to a string for inclusion in the POST request.
        - Construct the POST request query containing temperature, humidity, and timestamp data (Unix time).
        - Include 'device name' and 'API Key' in the headers for authentication.
        - Transmit the POST request to the Pipedream server.

        The query might look like this:

            ```
            ?temperature=15&humidity=60&time=1691608997
            ```

    To perform the POST request we use as reference the following article: [Arduino- HTTP Request](https://arduinogetstarted.com/tutorials/arduino-http-request)

    4. `loop()`: This function continuously monitors incoming data from the server. If data is received, it is displayed in the serial monitor. The loop function also initiates a new POST request every 5 minutes by calling sendPostRequest(), with the time interval defined in milliseconds.


5. __Pinout and Sensors:__

    While the provided image depicts an Arduino board, the Intel Galileo connections remain similar due to their comparable layouts. Here's how the sensors are connected:

    ![Connection Galileo - Sensors](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-PinoutGalileo.png)


6. __Considerations:__

    - HTTPS vs HTTP: For simplicity, the connection between Galileo and Pipedream uses HTTP.
     Please note that for enhanced security, it is advisable to use HTTPS for communication whenever possible. However, due to specific development environment constraints, HTTP was chosen for this integration.
    - Device Identification: The 'device name' and 'API Key' are essential for authenticating the device with the web server.
    - Error Handling: The logic includes error handling for connection failures.

7. __Temperature and Humidity Calculation:__

    For calibration details on the moisture sensor and temperature sensor technical information, you can refer to the provided footnotes[^13][^14]

    The LM35 temperature sensor provides analog data, which is converted into Celsius using a mathematical formula.

 [^13]: https://www.automatizacionparatodos.com/sensor-de-humedad-de-suelo-con-arduino/
 [^14]: https://devxplained.eu/en/blog/lm35-temperature-sensor

---

### SQLITE Database


It's important to note that this application __does not__ address race conditions. The web server employs an SQLite database, featuring the following tables:

1. __users Table:__

    - __id:__ Primary Key (auto-increment)
    - __username:__ Unique username for user identification
    - __hash:__ Hashed password
    - __email:__ User's email address

    This table enables user login, session management, and email communication.


2. __devices Table:__

    - __id:__ Primary Key (auto-increment)
    - __device_name:__ Name of the device
    - __device_apikey__ (hashed): API key (password) for device access

    This table stores device information and their respective API keys.

3. __device_assignments Table:__

    __user_id:__ Foreign Key referencing the primary key of the users table
    __device_id:__ Foreign Key referencing the primary key of the devices table

    This table establishes the relationship between users and devices, facilitating ownership mapping and management.

4. __device_history Table:__

    - user_id
    - device_id
    - humidity
    - temperature
    - epoch_time

    This table stores data sent by the Intel Galileo board to the __/apidata__ endpoint. It provides data for each user's display on the __/history__ page.

5. __sqlite_sequence Table:__

    - name
    - seq

    This table maintains track of the next available value for id columns during row insertion in the devices or users table.

__Database Diagram:__ [^15]

![Database Diagram](https://github.com/jdsuta/jdsuta/blob/main/images_agrosense/AS-Schemadb.png)

The database design intends to organize user authentication, device management, and historical data storage.

[^15]: https://dbdiagram.io/d

------

### Project Outcome Goals

1. **Good Outcome**:
   - Successful capture and presentation of signals on a web page.

2. **Better Outcome**:
   - Achieving the ability to not only capture and present signals but also send emails, such as welcome emails and alarm notifications. (Currently done here)

3. **Best Outcome**:
   - Accomplishing the capture of information, processing it effectively, sending relevant emails, and utilizing the Arduino to take actions for mitigating variable concerns. This outcome would involve executing specific actions based on data received from devices and sending confirmation emails about the applied solutions. Please note that this advanced functionality is not currently implemented in the existing program.

__Final Notes:__

Please notice the syntax and coherence and some questions regarding code were review using chatgpt as reference. <https://chat.openai.com/>