from flask import Flask, request, jsonify, render_template
import requests
import os
import speech_recognition as sr
import pyttsx3
import folium

app = Flask(__name__)

# API Key and Base URL for OpenWeatherMap
API_KEY = "8ebd10ad04f96444e9024741ec50b1b2"
BASE_URL = "http://api.openweathermap.org/data/2.5/"

# File for persistent storage of saved cities
SAVED_CITIES_FILE = "saved_cities.txt"

# Initialize the speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech using pyttsx3."""
    engine.say(text)
    engine.runAndWait()

def listen_command(prompt="Listening...", silent=False):
    """
    Listen for a voice command using the microphone.
    Returns the recognized text in lowercase.
    """
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        if not silent:
            speak(prompt)
        print(prompt)
        recognizer.adjust_for_ambient_noise(source, duration=1)
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        command = recognizer.recognize_google(audio)
        print("You said:", command)
        return command.lower()
    except sr.UnknownValueError:
        speak("Sorry, I did not catch that. Please try again.")
        return ""
    except sr.RequestError as e:
        speak("Could not request results; please check your network connection.")
        print("Error:", e)
        return ""

def load_saved_cities():
    """Load saved cities from persistent storage."""
    if os.path.exists(SAVED_CITIES_FILE):
        with open(SAVED_CITIES_FILE, "r") as f:
            cities = f.read().splitlines()
        return cities
    return []

def save_city(city):
    """Save a city to persistent storage if not already saved (case-insensitive)."""
    city = city.strip()
    cities = load_saved_cities()
    if city.lower() not in [c.lower() for c in cities]:
        with open(SAVED_CITIES_FILE, "a") as f:
            f.write(city + "\n")

def get_weather_data(city):
    """Fetch current weather data for a given city and format stats."""
    try:
        response = requests.get(f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric")
        response.raise_for_status()
        data = response.json()
        save_city(city)
        if "main" in data and "weather" in data:
            temp_c = data['main']['temp']
            temp_f = temp_c * 9/5 + 32
            feels_c = data['main']['feels_like']
            feels_f = feels_c * 9/5 + 32
            weather_desc = data['weather'][0]['description'].capitalize()
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            coords = data['coord']
            formatted = (
                f"Temperature: {temp_f:.1f}°F / {temp_c:.1f}°C\n"
                f"Feels Like: {feels_f:.1f}°F / {feels_c:.1f}°C\n"
                f"Weather: {weather_desc}\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} m/s\n"
                f"Coordinates: {coords}"
            )
            data['formatted'] = formatted
        return data
    except Exception as e:
        return {"error": str(e)}

def get_forecast_data(city):
    """Fetch 5-day forecast data for a given city."""
    try:
        response = requests.get(f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric")
        response.raise_for_status()
        data = response.json()
        save_city(city)
        return data
    except Exception as e:
        return {"error": str(e)}

def extract_cities(command):
    """
    Extract city names from a spoken command.
    Looks for keywords 'in' or 'for' and splits the remainder on "and" or commas.
    Returns a list of detected city names.
    """
    cities = []
    if "in" in command:
        index = command.find("in")
        city_string = command[index + len("in"):].strip()
    elif "for" in command:
        index = command.find("for")
        city_string = command[index + len("for"):].strip()
    else:
        city_string = ""
    if city_string:
        city_string = city_string.replace(",", " and ")
        cities = [c.strip() for c in city_string.split(" and ") if c.strip()]
    return cities

@app.route('/')
def index():
    saved_cities = load_saved_cities()
    return render_template('index.html', saved_cities=saved_cities)

@app.route('/weather', methods=['GET'])
def weather():
    city = request.args.get('city', '')
    data = get_weather_data(city)
    return jsonify(data)

@app.route('/forecast', methods=['GET'])
def forecast():
    city = request.args.get('city', '')
    data = get_forecast_data(city)
    return jsonify(data)

@app.route('/voice', methods=['GET'])
def voice():
    """Initiate AI voice command and return the spoken command."""
    command = listen_command("Please speak your command.")
    return jsonify({"command": command})

@app.route('/saved', methods=['GET'])
def saved():
    cities = load_saved_cities()
    return jsonify({"saved_cities": cities})

@app.route('/mapview', methods=['GET'])
def mapview():
    """
    Create an interactive map that shows the temperature of surrounding towns.
    Given a city, get its coordinates and use the OpenWeatherMap 'find' endpoint to get nearby cities.
    Then, use Folium to generate the map.
    """
    city = request.args.get('city', '')
    if not city:
        return "City not provided", 400

    # Get the center city's data
    city_data = get_weather_data(city)
    if "error" in city_data:
        return city_data["error"], 400
    lat = city_data["coord"]["lat"]
    lon = city_data["coord"]["lon"]

    # Use the 'find' endpoint to get nearby towns (limit to 10)
    find_url = f"{BASE_URL}find?lat={lat}&lon={lon}&cnt=10&appid={API_KEY}&units=metric"
    find_response = requests.get(find_url)
    find_response.raise_for_status()
    find_data = find_response.json()

    # Create a folium map centered at the city
    folium_map = folium.Map(location=[lat, lon], zoom_start=10)

    # Add marker for the center city (highlighted)
    folium.Marker(
         [lat, lon],
         popup=f"{city}: {city_data['main']['temp']}°C",
         icon=folium.Icon(color='red')
    ).add_to(folium_map)

    # Add markers for each surrounding city
    for item in find_data.get('list', []):
         town_name = item['name']
         town_lat = item['coord']['lat']
         town_lon = item['coord']['lon']
         temperature = item['main']['temp']
         popup_text = f"{town_name}: {temperature}°C"
         folium.Marker(
             [town_lat, town_lon],
             popup=popup_text,
             icon=folium.Icon(color='blue')
         ).add_to(folium_map)

    # Render map as HTML
    return folium_map._repr_html_()

if __name__ == '__main__':
    app.run(debug=True)
