# AI_Weather_Dashboard
The AI Weather Dashboard is a Python-based application that integrates voice recognition and text-to-speech capabilities with real-time weather data from OpenWeatherMap. It provides current weather conditions, a 5-day forecast (displayed in 3-hour increments via graphs), and air pollution data for user-specified cities. The dashboard can be interacted with using voice commands and saves preferences such as your chosen AI name and cities for future sessions.

Features
Voice Interaction:
Uses speech recognition to listen for commands and pyttsx3 for text-to-speech feedback.

Weather Data Retrieval:
Retrieves current weather conditions and a 5-day forecast using the OpenWeatherMap API.

Air Pollution Information:
Fetches air quality index (AQI) data based on geographical coordinates.

Forecast Visualization:
Generates a four-panel matplotlib graph showing:

Temperature (in both Fahrenheit and Celsius)
Humidity
Rainfall (mm)
Snowfall (mm)
Persistent Storage:
Stores the AI’s name and saved cities in local text files (ai_name.txt and saved_cities.txt) to provide a seamless experience across sessions.

Conversational Flow:
Initiates a session where it offers to display full information on saved cities or allows the user to specify new ones. It also supports renaming the AI via voice commands.

Dependencies
Before running the application, ensure you have the following Python packages installed:

os
requests
matplotlib
speech_recognition
pyttsx3
datetime
You can install the required libraries (if not already available) using pip. For example:

pip install requests matplotlib SpeechRecognition pyttsx3

Note:
Some packages, like speech_recognition and pyttsx3, may require additional system dependencies. Make sure your system has the appropriate drivers and permissions to use your microphone and speakers.

Setup
Clone or Download the Repository:
Download the project files into a local directory named AI_Weather_Dashboard.

API Key Configuration:
The application uses an OpenWeatherMap API key which is hardcoded in the script. If you have your own API key, replace the existing key in the code:

API_KEY = "your_api_key_here"
Verify Persistent Files:
The project will create ai_name.txt and saved_cities.txt if they do not already exist. These files store the AI's name and the list of cities, respectively.

Usage
Run the Application:
Execute the main Python script:

python <your_script_filename>.py
Voice Activation:
Upon startup, the AI announces its name (default is "josh" if no name is set) and instructs you to say the wake phrase (e.g., "hey josh").

Interactive Session:

Speak the wake phrase to activate the dashboard.
Follow the spoken prompts to retrieve weather information or to update preferences.
You can ask for the current weather, forecast, or air pollution data by mentioning a city.
To rename the AI, say "change name" or "rename" followed by the new name.
To end the session, say "go to sleep" or "sleep."
Graphical Forecast:
The dashboard generates a matplotlib graph showing a 5-day forecast in 3-hour increments for temperature, humidity, rain, and snow. Each data point is annotated with its value.

Code Structure
Main Functions:

main(): Initializes the AI, sets up the wake phrase, and begins listening for commands.
conversation_session(ai_name): Handles an interactive conversation session including saved cities and command processing.
Weather and Forecast Functions:

get_weather(city): Retrieves current weather data.
get_forecast(city): Retrieves 5-day forecast data.
display_weather(data): Outputs current weather details.
display_3hour_forecast_graph(city): Generates and displays the forecast graph.
Air Pollution Functions:

get_air_pollution(lat, lon): Retrieves air pollution data based on latitude and longitude.
display_air_pollution(data): Outputs air quality information.
Utility Functions:

Functions for saving and loading AI name and cities.
listen_command(prompt, silent=False): Captures and processes voice commands.
speak(text): Converts text to speech.
Future Enhancements
Error Handling:
More robust error handling and user prompts in case of network issues or unrecognized commands.

Additional Data:
Integration with more APIs to include additional weather metrics or environmental data.

GUI Integration:
Potential integration with a graphical user interface for a more user-friendly experience.

Troubleshooting
Microphone Issues:
Ensure your microphone is properly connected and configured. Adjust the ambient noise settings if necessary.

API Errors:
Verify your API key is valid and that you have internet connectivity when requesting weather data.

Graph Display Issues:
If the matplotlib graph does not display properly, check your installation of matplotlib and your system’s display settings.
