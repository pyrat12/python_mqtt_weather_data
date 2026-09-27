"""Flask/Socket.IO web app that relays MQTT weather readings to the browser."""  #Beschreibt den Zweck der Web-App

import warnings                                         #Warnmeldungen steuern

from flask import Flask, render_template                #Flask-Web-App erstellen und HTML-Templates laden
from flask_socketio import SocketIO                     #Echtzeit-Kommunikation zwischen Server und Browser ermöglichen
import paho.mqtt.client as mqtt                         #MQTT-Clientbibliothek zum Empfangen von Nachrichten laden

# Ignore warnings
warnings.filterwarnings("ignore")                       #Warnmeldungen ausblenden

# Create a Flask web app
app = Flask(__name__)                                   #Flask-Anwendung erstellen
app.config['SECRET_KEY'] = 'geheim'                     #Secret Key für die Flask-Anwendung festlegen
socketio = SocketIO(app, cors_allowed_origins="*")      #Socket.IO aktivieren und Verbindungen von allen Origins erlauben

# IP-Address of broker
MQTT_SERVER = "localhost"                               #Adresse des MQTT-Brokers festlegen

# Topics
MQTT_TEMP = "sensor/temp"                               #MQTT-Topic für Lufttemperatur
MQTT_WATER_TEMP = "sensor/water_temp"                   #NEU: MQTT-Topic für Wassertemperatur
MQTT_WIND_SPEED = "sensor/wind_speed"                   #NEU: MQTT-Topic für Windgeschwindigkeit

# The callback for when the client receives a CONNACK response from the server.
def on_connect(mqtt_client, _userdata, _flags, rc):                      #Funktion wird nach erfolgreicher Verbindung mit dem MQTT-Broker aufgerufen
    """Subscribe to the weather topics once connected to the broker."""  #Beschreibt den Zweck der Callback-Funktion
    print("Connected with result code " + str(rc))                       #Verbindungsstatus im Terminal ausgeben
    mqtt_client.subscribe(MQTT_TEMP)                                     #Topic für Lufttemperatur abonnieren
    mqtt_client.subscribe(MQTT_WATER_TEMP)                               #NEU: Topic für Wassertemperatur abonnieren
    mqtt_client.subscribe(MQTT_WIND_SPEED)                               #NEU: Topic für Windgeschwindigkeit abonnieren

# The callback for when a PUBLISH message is received from the server.
def on_message(_client, _userdata, msg):                                 #Funktion wird bei jeder empfangenen MQTT-Nachricht automatisch aufgerufen
    """Forward numeric MQTT payloads to connected websocket clients."""  #Beschreibt den Zweck der Callback-Funktion
    topic = msg.topic                                                    #Topic der empfangenen MQTT-Nachricht auslesen
    payload = msg.payload.decode('utf-8')                                #MQTT-Nachricht von Bytes in Text umwandeln

    try:                                                                 #Versuchen, den empfangenen Wert numerisch zu verarbeiten
        # Attempt to convert the payload to a float
        data = float(payload)                                            #Empfangenen Text in eine Gleitkommazahl umwandeln
        # print(f"Received data: {data}")
        socketio.emit('mqtt_message', {'topic': topic, 'data': data})    #Topic und Messwert in Echtzeit an den Browser senden
        # print(f"Emitted data: {data}")
    except ValueError:                                                   #Fehler abfangen, falls die Nachricht keinen numerischen Wert enthält
        # Handle non-numeric payloads (e.g., LWT message)
        print(f"Received non-numeric payload: {payload}")                #Nicht-numerische Nachricht im Terminal ausgeben

# Create an MQTT client and attach our routines to it.
client = mqtt.Client()                                                        #MQTT-Client erstellen
client.on_connect = on_connect                                                #on_connect als Callback für erfolgreiche MQTT-Verbindungen registrieren
client.on_message = on_message                                                #on_message als Callback für eingehende MQTT-Nachrichten registrieren
client.connect(MQTT_SERVER, 1883, 60)                                         #Verbindung zum MQTT-Broker auf Port 1883 herstellen

# Define the index route
@app.route('/')                                                               #URL "/" mit der folgenden Python-Funktion verknüpfen
def index():                                                                  #Funktion für die Startseite definieren
    """Render the live weather chart page."""                                 #Beschreibt den Zweck der Funktion
    return render_template('chart.html')                                      #HTML-Datei chart.html aus dem templates-Ordner laden

# Start the web server
if __name__ == '__main__':                                                    #Prüfen, ob app.py direkt ausgeführt wurde
    client.loop_start()                                                       #MQTT-Client im Hintergrund starten und auf Nachrichten hören
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)  #Flask-/Socket.IO-Webserver auf Port 5000 starten



    