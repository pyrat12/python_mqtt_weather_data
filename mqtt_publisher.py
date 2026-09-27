"""Fetch weather data from an API and publish it to an MQTT broker."""      #Beschreibt den Zweck des Skripts

import time                                                                 #Zeitfunktionen laden, hier für Pausen zwischen den Abfragen

import requests                                                             #HTTP-Anfragen an die Wetter-API senden
import paho.mqtt.client as mqtt                                             #MQTT-Clientbibliothek zum Publizieren von Nachrichten laden

# MQTT broker settings
BROKER = "localhost"                                                        #Adresse des MQTT-Brokers festlegen
PORT = 1883                                                                 #Standard-Port für unverschlüsseltes MQTT festlegen

TOPIC = "sensor/temp"                                                       #MQTT-Topic für Lufttemperatur
TOPIC_WATER = "sensor/water_temp"                                           #NEU: MQTT-Topic für Wassertemperatur
TOPIC_WIND = "sensor/wind_speed"                                            #NEU: MQTT-Topic für Windgeschwindigkeit

API_URL = (                                                                 #URL der Wetter-API zusammensetzen
    "https://tecdottir.herokuapp.com/measurements/tiefenbrunnen"            #API-Endpunkt der Messstation Tiefenbrunnen
    "?sort=timestamp_cet%20desc&limit=5"                                    #Daten nach Zeit absteigend sortieren und auf 5 Einträge begrenzen
)

# Initialize the MQTT client
client = mqtt.Client("Publisher")                                           #MQTT-Client mit dem Namen Publisher erstellen

# Enable logging (optional)
# client.on_log = lambda client, userdata, level, buf: print(f"Log: {buf}")
# Connect to the MQTT broker
client.connect(BROKER, PORT)                                                #Verbindung zum MQTT-Broker herstellen

# Function to fetch the most recent data from the weather API
def get_data():                                                             #Funktion definieren, welche die aktuellsten Wetterwerte von der API abruft
    """Return the most recent weather readings, or None if unavailable."""
    response = requests.get(API_URL, timeout=10)                            #HTTP-GET-Anfrage an die Wetter-API senden
    data = response.json()                                                  #JSON-Antwort in ein Python-Dictionary umwandeln

    if data["ok"] and len(data["result"]) > 0:                              #Prüfen, ob gültige Messdaten vorhanden sind
        # Assuming the most recent entry is the first in the sorted list
        most_recent_entry = data["result"][0]                               #Aktuellsten Messdatensatz auswählen

        air_temperature = most_recent_entry["values"]["air_temperature"]["value"]       #Lufttemperatur auslesen
        water_temperature = most_recent_entry["values"]["water_temperature"]["value"]   #NEU: Wassertemperatur auslesen
        wind_speed = most_recent_entry["values"]["wind_speed_avg_10min"]["value"]       #NEU: durchschnittliche Windgeschwindigkeit der letzten 10 Minuten auslesen

        return air_temperature, water_temperature, wind_speed                           #NEU: Alle drei Wetterwerte zurückgeben

    return None                                                             #None zurückgeben, falls keine gültigen Messdaten vorhanden sind

# Function to fetch and publish data
def publish_data():                                                         #Funktion definieren, welche Wetterdaten fortlaufend abruft und publiziert
    """Continuously fetch and publish weather data until interrupted."""
    try:                                                                    #Manuellen Abbruch mit Ctrl+C abfangen
        while True:                                                         #Endlosschleife starten
            values = get_data()                                             #NEU: Alle drei aktuellen Wetterwerte abrufen

            if values is not None:                                          #Prüfen, ob gültige Wetterdaten vorhanden sind
                air_temperature, water_temperature, wind_speed = values     #NEU: Rückgabewerte auf drei Variablen verteilen

                print(f"Publishing: {air_temperature}°C from {TOPIC}")      #Lufttemperatur im Terminal anzeigen
                client.publish(TOPIC, str(air_temperature))                 #Lufttemperatur via MQTT publizieren

                print(f"Publishing: {water_temperature}°C from {TOPIC_WATER}")      #NEU: Wassertemperatur anzeigen
                client.publish(TOPIC_WATER, str(water_temperature))                 #NEU: Wassertemperatur via MQTT publizieren

                print(f"Publishing: {wind_speed} m/s from {TOPIC_WIND}")            #NEU: Windgeschwindigkeit anzeigen
                client.publish(TOPIC_WIND, str(wind_speed))                         #NEU: Windgeschwindigkeit via MQTT publizieren

            else:                                                           #Falls keine gültigen Wetterdaten vorhanden sind
                print("No data available.")                                 #Hinweismeldung ausgeben

            time.sleep(1)                                                   #Eine Sekunde warten, bevor erneut Daten abgefragt werden

    except KeyboardInterrupt:                                               #Abfangen, wenn das Skript mit Ctrl+C beendet wird
        print("Disconnecting from broker...")                               #Meldung beim Beenden ausgeben
        client.disconnect()                                                 #MQTT-Verbindung sauber trennen

if __name__ == "__main__":                                                  #Prüfen, ob das Skript direkt ausgeführt wurde
    # Publish data
    publish_data()                                                          #Abrufen und Publizieren der Wetterdaten starten