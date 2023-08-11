// Code to be used in Intel Galileo Gen 1

#include <Ethernet.h>
#include <EthernetUdp.h>
#include <NTPClient.h>
#include <SPI.h>

// MAC address of the Intel Galileo Board
byte mac[] = {0x98, 0x4F, 0xEE, 0x01, 0x40, 0xBC};

// server where we will connect. It's going to work as a bridge between Intel Galileo and End Webserver
char server[] = "en4rz4xfejl30r8.m.pipedream.net";

// IP Address to be assigned to the galileo board
IPAddress ip(192, 168, 1, 177);
EthernetClient client;

// to synchrinize galileo time with NTP server
EthernetUDP udp;
NTPClient timeClient(udp, "pool.ntp.org");

unsigned long previousMillis = 0;      // Store the previous time
const unsigned long interval = 300000; // Interval in milliseconds (5 minutes)

int SensorPin = A0; // Collect Humidity in A0 of galileo board

float temp;
int SensorPin1 = A1; // Collect Temperature in A1 of Galileo board

void setup()
{
    system("ifup eth0"); // Necessary to initialize the port og intel galileo
    delay(3000);
    Serial.begin(9600);
    while (!Serial)
        ; // wait until the serial communication with the board is established before proceeding further with the setup process.

    // If DHCP configuration fails, it displays an error message and then attempts to configure the Ethernet connection using a
    // static IP address instead.
    if (Ethernet.begin(mac) == 0)
    {
        Serial.println("Failed to configure Ethernet using DHCP");
        Ethernet.begin(mac, ip);
    }

    delay(1000); // give the Ethernet connection some time to stabilize after configuration before proceeding to the next steps.
    Serial.println("connecting...");

    timeClient.begin(); // Start the NTP client.  Initializes the NTP (Network Time Protocol) client.The board will attempt to
                        // retrieve the current time from an NTP server.
    sendPostRequest();  // Send the initial post request. It will be called only once in setup. Afterwards it will be called in the
                        // loop function for consequent post requests.
}

void loop()
{
    // Check if there is incoming data from the server.
    if (client.available())
    {
        // read a single byte of incoming data from the server.
        char c = client.read();
        Serial.print(c);
    }

    unsigned long currentMillis =
        millis(); // Get the current time. represents the time in milliseconds since the Arduino started running.

    // If currentMillis - previousMillis is equal or greater than the interval. (interval is a constant defined above 5 mins). Then
    // it will send a post request.
    if (currentMillis - previousMillis >= interval)
    {
        previousMillis = currentMillis; // Save the current time in variable previousMillis
        sendPostRequest();              // Send the POST request by calling the function every 5 minutes
    }
}

void sendPostRequest()
{
    // Connect to server in port 80 (HTTP)
    if (client.connect(server, 80))
    {
        timeClient.update(); // Queries the NTP server for the current time and updates the Galileo internal time.
        long unixTime = timeClient.getEpochTime(); // Used to retrieve and store the updated epoch time after the NTP client has
                                                   // been updated using timeClient.update().
        Serial.println("connected");
        // Serial.println(unixTime); in case is needed to check epoch time

        // Collect humidity from sensor in pin A0 in Galileo Board
        int humidity = analogRead(SensorPin);
        humidity = map(humidity, 509, 378, 0,
                       100); // The values 509 and 378 were taken by testing the sensor completely dry (509) and by being completely
                             // submerged in water(378) then we map the value from 0% to 100% RH to get humidity

        // Collect Temperature LM35 in pin A1 in Galileo Board
        temp = analogRead(SensorPin1);      //
        temp = (5 * temp * 100.0) / 1024.0; // used to convert the analog read to actual temperature in Celsius. Ref:
                                            // https://devxplained.eu/en/blog/lm35-temperature-sensor 5 is the reference voltage.
                                            // 1024 because that's the resolution of the board

        // Convert the float value to a string with 2 decimal places
        char tempStr[10]; // Array size of 10 elements. HOwever, in this case for 2 elements is required only an array of 6.
                          // Example, 23.46 would be '2' '3' '.' '4' '6' '\0' The size is 6 including null char. HOwever, leave
                          // it as 10 in case more detail is needed
        sprintf(tempStr, "%.2f", temp); // tempStr is the string buffer where the string will be stored, %.2f means the format of
                                        // the string. A float with 2 digits after decimal point, temp is variable we want to store

        // Create a String object from the char array. In summary we take the char array and convert it to string and then assign it
        // tostring tempString
        String tempString = String(tempStr);

        // Join all the data in a string that will be used to past the data via API
        String queryString =
            String("?temperature=") + tempString + String("&humidity=") + String(humidity) + String("&time=") + String(unixTime);

        // Make a POST to pipedream. including the data captured previously

        client.print("POST /apidata" + queryString + " HTTP/1.1\r\n");
        client.print("Host: en4rz4xfejl30r8.m.pipedream.net\r\n");

        // Device name is the one given in the web page
        client.print("devicename: test_apikey\r\n");
        // Api Key is the one created in the web page
        client.print("Api-Key: a2f3bdd3c1d234a1529ff8233b98633e\r\n");
        client.print("Connection: close\r\n");
        client.print("\r\n");

        client.flush(); // Wait for the data to be sent

        client.stop(); // Close the client connection
    }
    else
    {
        // If unable to connect it will give a connection failed
        Serial.println("connection failed");
    }
}