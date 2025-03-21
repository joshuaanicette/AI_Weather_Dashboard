import os
import requests
import matplotlib.pyplot as plt
import speech_recognition as sr
import pyttsx3
from datetime import datetime

# API Key and Base URL for OpenWeatherMap
API_KEY = "8ebd10ad04f96444e9024741ec50b1b2"
BASE_URL = "http://api.openweathermap.org/data/2.5/"

# Files for persistent storage
AI_NAME_FILE = "ai_name.txt"
SAVED_CITIES_FILE = "saved_cities.txt"

# Initialize the speech engine
engine = pyttsx3.init()

def speak(text):
    """Convert text to speech."""
    engine.say(text)
    engine.runAndWait()

def listen_command(prompt="Listening...", silent=False):
    """
    Listen for a voice command.
    Adjusts for ambient noise and allows up to 10 seconds to complete the sentence.
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
        if not silent:
            speak("Sorry, I did not catch that. Please try again.")
        return ""
    except sr.RequestError as e:
        if not silent:
            speak("Could not request results; please check your network connection.")
        print("Error:", e)
        return ""

def load_ai_name():
    """Load the AI name from a file if it exists."""
    if os.path.exists(AI_NAME_FILE):
        with open(AI_NAME_FILE, "r") as file:
            name = file.read().strip()
            if name:
                return name.lower()
    return None

def save_ai_name(name):
    """Save the AI name to a file."""
    with open(AI_NAME_FILE, "w") as file:
        file.write(name)

def load_saved_cities():
    """Load saved cities from a file."""
    if os.path.exists(SAVED_CITIES_FILE):
        with open(SAVED_CITIES_FILE, "r") as f:
            cities = [line.strip() for line in f if line.strip()]
        return cities
    return []

def save_cities(cities):
    """Save cities to a file (one per line)."""
    with open(SAVED_CITIES_FILE, "w") as f:
        for city in cities:
            f.write(city + "\n")

def extract_cities(command):
    """
    Attempt to extract city names from the command.
    It looks for keywords 'for' or 'in', then splits the remaining text by 'and' or commas.
    Only the first two detected city names are returned.
    """
    cities = []
    if "for" in command:
        index = command.find("for")
        city_string = command[index + len("for"):].strip()
    elif "in" in command:
        index = command.find("in")
        city_string = command[index + len("in"):].strip()
    else:
        city_string = ""
    
    if city_string:
        city_string = city_string.replace(",", " and ")
        cities = [c.strip() for c in city_string.split(" and ") if c.strip()]
    
    if len(cities) > 2:
        cities = cities[:2]
    return cities

def get_weather(city):
    """Fetch current weather data for a given city."""
    try:
        response = requests.get(f"{BASE_URL}weather?q={city}&appid={API_KEY}&units=metric")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        speak(f"Error retrieving weather data for {city}.")
        return None

def get_forecast(city):
    """Fetch 5-day forecast data for a given city."""
    try:
        response = requests.get(f"{BASE_URL}forecast?q={city}&appid={API_KEY}&units=metric")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        speak(f"Error retrieving forecast data for {city}.")
        return None

def get_air_pollution(lat, lon):
    """Fetch air pollution data for given coordinates."""
    try:
        response = requests.get(f"{BASE_URL}air_pollution?lat={lat}&lon={lon}&appid={API_KEY}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        speak("Error retrieving air pollution data.")
        return None

def celsius_to_fahrenheit(celsius):
    return celsius * 9/5 + 32

def display_weather(data):
    """Display current weather information with Fahrenheit first."""
    if data:
        temp_c = data['main']['temp']
        feels_c = data['main']['feels_like']
        temp_f = celsius_to_fahrenheit(temp_c)
        feels_f = celsius_to_fahrenheit(feels_c)
        info = (
            f"City: {data['name']}\n"
            f"Temperature: {temp_f:.1f}°F / {temp_c:.1f}°C\n"
            f"Feels Like: {feels_f:.1f}°F / {feels_c:.1f}°C\n"
            f"Weather: {data['weather'][0]['description'].capitalize()}\n"
            f"Humidity: {data['main']['humidity']}%\n"
            f"Wind Speed: {data['wind']['speed']} m/s\n"
            f"Coordinates: {data['coord']}"
        )
        print("\n--- Current Weather ---")
        print(info)
        speak(f"In {data['name']}, the temperature is {temp_f:.1f} degrees Fahrenheit, which is {temp_c:.1f} degrees Celsius.")
    else:
        print("No weather data available.")
        speak("No weather data available.")

def display_air_pollution(data):
    """Display air pollution data with AQI."""
    if data:
        aqi = data["list"][0]["main"]["aqi"]
        aqi_levels = {1: "Good", 2: "Fair", 3: "Moderate", 4: "Poor", 5: "Very Poor"}
        info = f"Air Quality Index (AQI): {aqi} - {aqi_levels.get(aqi, 'Unknown')}"
        print("\n--- Air Pollution Data ---")
        print(info)
        speak(f"The air quality index is {aqi}, which is considered {aqi_levels.get(aqi, 'unknown')}.")
    else:
        print("No air pollution data available.")
        speak("No air pollution data available.")

def display_3hour_forecast_graph(city):
    """
    Display a 5-day forecast graph in 3-hour increments.
    The graph shows:
      - Temperature (°F)
      - Humidity (%)
      - Rain (mm)
      - Snow (mm)
    Each data point is annotated with its numeric value.
    """
    forecast_data = get_forecast(city)
    if not forecast_data or "list" not in forecast_data:
        speak(f"Cannot retrieve forecast data for {city}.")
        return

    # Extract 3-hour forecast data points
    timestamps = [entry["dt_txt"] for entry in forecast_data["list"]]
    temps_c = [entry["main"]["temp"] for entry in forecast_data["list"]]
    temps_f = [celsius_to_fahrenheit(t) for t in temps_c]
    hums = [entry["main"]["humidity"] for entry in forecast_data["list"]]
    rains = [entry.get("rain", {}).get("3h", 0) for entry in forecast_data["list"]]
    snows = [entry.get("snow", {}).get("3h", 0) for entry in forecast_data["list"]]

    # Create 4 subplots
    fig, axs = plt.subplots(4, 1, figsize=(14, 18), sharex=True)

    # Temperature subplot
    axs[0].plot(timestamps, temps_f, marker="o", color="red")
    axs[0].set_ylabel("Temp (°F)")
    axs[0].set_title(f"5-Day Forecast for {city} (3-hour increments)")
    for i, val in enumerate(temps_f):
        axs[0].annotate(f"{val:.1f}", (timestamps[i], temps_f[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

    # Humidity subplot
    axs[1].plot(timestamps, hums, marker="x", color="blue")
    axs[1].set_ylabel("Humidity (%)")
    for i, val in enumerate(hums):
        axs[1].annotate(f"{val}%", (timestamps[i], hums[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

    # Rain subplot
    axs[2].plot(timestamps, rains, marker="s", color="cyan")
    axs[2].set_ylabel("Rain (mm)")
    for i, val in enumerate(rains):
        axs[2].annotate(f"{val:.1f}", (timestamps[i], rains[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

    # Snow subplot
    axs[3].plot(timestamps, snows, marker="^", color="purple")
    axs[3].set_ylabel("Snow (mm)")
    axs[3].set_xlabel("Date & Time")
    for i, val in enumerate(snows):
        axs[3].annotate(f"{val:.1f}", (timestamps[i], snows[i]), textcoords="offset points", xytext=(0,5), ha='center', fontsize=8)

    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    plt.show(block=True)

def conversation_session(ai_name):
    """
    Run a conversation session once awakened.
    The assistant first offers to show full information for saved cities (if any),
    including current weather, the 3-hour forecast graph, and air pollution data.
    Then it listens for further commands until you say "go to sleep."
    """
    saved_cities = load_saved_cities()
    if saved_cities:
        speak("I see you have saved cities: " + ", ".join(saved_cities) +
              ". Would you like full information on these cities? Please say yes or no.")
        answer = listen_command("Listening for your answer.")
        if "yes" in answer:
            for city in saved_cities:
                speak(f"Fetching full information for {city}.")
                display_3hour_forecast_graph(city)
                weather_data = get_weather(city)
                display_weather(weather_data)
                if weather_data:
                    lat = weather_data["coord"]["lat"]
                    lon = weather_data["coord"]["lon"]
                    air_data = get_air_pollution(lat, lon)
                    display_air_pollution(air_data)
        else:
            speak("Okay, please tell me the cities you want to check.")
            city_input = listen_command("Listening for city names.")
            cities = extract_cities("for " + city_input)
            if not cities:
                cities = [city_input.strip()]
            save_cities(cities)
            for city in cities:
                display_3hour_forecast_graph(city)
                weather_data = get_weather(city)
                display_weather(weather_data)
                if weather_data:
                    lat = weather_data["coord"]["lat"]
                    lon = weather_data["coord"]["lon"]
                    air_data = get_air_pollution(lat, lon)
                    display_air_pollution(air_data)
    else:
        speak("No saved cities found. Please tell me the cities you want to check.")
        city_input = listen_command("Listening for city names.")
        cities = extract_cities("for " + city_input)
        if not cities:
            cities = [city_input.strip()]
        save_cities(cities)
        for city in cities:
            display_3hour_forecast_graph(city)
            weather_data = get_weather(city)
            display_weather(weather_data)
            if weather_data:
                lat = weather_data["coord"]["lat"]
                lon = weather_data["coord"]["lon"]
                air_data = get_air_pollution(lat, lon)
                display_air_pollution(air_data)
    
    while True:
        command = listen_command("I'm listening for your command.")
        if "change name" in command or "rename" in command:
            speak("Please say the new name for me.")
            new_name = listen_command("Listening for new AI name.")
            if new_name:
                ai_name = new_name.strip().lower()
                save_ai_name(ai_name)
                speak(f"My name has been updated to {ai_name}.")
            continue
        if "go to sleep" in command or "sleep" in command:
            speak("Okay, I'm going to sleep. Wake me up when you need me.")
            break
        if "exit" in command or "quit" in command:
            speak("Goodbye!")
            exit(0)
        if "weather" in command or "forecast" in command or "air pollution" in command or "saved cities" in command:
            cities = extract_cities(command)
            if not cities:
                speak("I didn't detect a city name. Please say the city name or names separated by 'and'.")
                city_input = listen_command("Listening for city names.")
                cities = extract_cities("for " + city_input)
                if not cities:
                    cities = [city_input.strip()]
            save_cities(cities)
            for city in cities:
                display_3hour_forecast_graph(city)
                weather_data = get_weather(city)
                display_weather(weather_data)
                if weather_data:
                    lat = weather_data["coord"]["lat"]
                    lon = weather_data["coord"]["lon"]
                    air_data = get_air_pollution(lat, lon)
                    display_air_pollution(air_data)
        else:
            speak("I'm sorry, I didn't understand your command. Please try again.")
    return ai_name

def main():
    ai_name = load_ai_name()
    if ai_name:
        speak(f"Welcome back. My name is {ai_name}.")
    else:
        speak("I don't have a name yet. I'll call myself josh.")
        ai_name = "josh"
        save_ai_name(ai_name)
    
    wake_phrase = f"hey {ai_name}"
    speak(f"To wake me up, say '{wake_phrase}'.")
    
    while True:
        command = listen_command(silent=True)
        if wake_phrase in command:
            speak("Yes?")
            ai_name = conversation_session(ai_name)
            wake_phrase = f"hey {ai_name}"

if __name__ == "__main__":
    main()