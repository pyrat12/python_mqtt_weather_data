"""Subscribe to MQTT topics and print incoming weather readings."""  #Beschreibt den Zweck des Skripts

import paho.mqtt.client as mqtt                                      #MQTT-Clientbibliothek zum Empfangen von Nachrichten laden

# MQTT broker settings
BROKER = "localhost"                                                 #Adresse des MQTT-Brokers festlegen
PORT = 1883                                                          #Standard-Port für unverschlüsseltes MQTT festlegen
TOPIC = "sensor/temp"                                                #MQTT-Topic für Lufttemperatur
TOPIC_WATER = "sensor/water_temp"                                    #NEU: MQTT-Topic für Wassertemperatur
TOPIC_WIND = "sensor/wind_speed"                                     #NEU: MQTT-Topic für Windgeschwindigkeit

# Callback function for when a message is received
def on_message(_client, _userdata, message):                            #Funktion wird automatisch aufgerufen, sobald eine MQTT-Nachricht empfangen wird
    """Print the weather value carried by an incoming MQTT message."""  #Zweck der Callback-Funktion beschreiben
    payload = message.payload.decode()                                  #Empfangene MQTT-Nachricht von Bytes in Text umwandeln

    try:                                                                #Versuchen, den empfangenen Wert in eine Zahl umzuwandeln
        value = float(payload)                                          #Empfangenen Text in eine Gleitkommazahl umwandeln

        if message.topic == TOPIC:                                      #Prüfen, ob die Nachricht zur Lufttemperatur gehört
            print(f"Received air temperature: {value}°C")               #Lufttemperatur ausgeben

        elif message.topic == TOPIC_WATER:                              #NEU: Prüfen, ob die Nachricht zur Wassertemperatur gehört
            print(f"Received water temperature: {value}°C")             #NEU: Wassertemperatur ausgeben

        elif message.topic == TOPIC_WIND:                               #NEU: Prüfen, ob die Nachricht zur Windgeschwindigkeit gehört
            print(f"Received wind speed: {value} m/s")                  #NEU: Windgeschwindigkeit ausgeben

    except ValueError:                                                  #Fehler abfangen, falls der empfangene Wert keine Zahl ist
        pass                                                            #Fehler ignorieren und Programm weiterlaufen lassen

# Initialize the MQTT client
client = mqtt.Client("Subscriber")                                      #MQTT-Client mit dem Namen Subscriber erstellen

# Set the callback function for message reception
client.on_message = on_message                                          #on_message als Funktion für eingehende MQTT-Nachrichten registrieren

# Enable logging (optional)
# client.on_log = lambda client, userdata, level, buf: print(f"Log: {buf}")
# Connect to the MQTT broker
client.connect(BROKER, PORT)                                            #Verbindung zum MQTT-Broker herstellen

# Subscribe to the topics
client.subscribe(TOPIC)                                                 #Topic für Lufttemperatur abonnieren
client.subscribe(TOPIC_WATER)                                           #NEU: Topic für Wassertemperatur abonnieren
client.subscribe(TOPIC_WIND)                                            #NEU: Topic für Windgeschwindigkeit abonnieren

# Start the MQTT client loop to process messages
client.loop_forever()                                                   #Endlosschleife starten und fortlaufend auf neue MQTT-Nachrichten warten