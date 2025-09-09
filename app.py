from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import re
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)

# URLs of your events
EVENTS = {
    "event1": "https://gravitas.vit.ac.in/events/e72677fb-caaa-43b5-99ce-24bf878ff242",
    "event2": "https://gravitas.vit.ac.in/events/00cee489-395a-47f6-bacc-46066160caa8"
}

MAX_SEATS = 200  # adjust if different for each event

# Cache dictionary
cache = {
    "timestamp": 0,
    "data": None
}
CACHE_DURATION = 1800  # 30 minutes in seconds

def get_registration_count(url, max_seats):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Look for divs with the class
        divs = soup.select("div.text-white\\/70.text-sm.sm\\:text-base")

        seats_left = None
        for div in divs:
            text = div.get_text(" ", strip=True)  # join pieces into one string
            if "seats left" in text:
                match = re.search(r"(\d+)\s*seats left", text)
                if match:
                    seats_left = int(match.group(1))
                    break

        if seats_left is not None:
            return max_seats - seats_left
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

@app.route("/registrations")
def registrations():
    current_time = time.time()

    # Return cached data if it's still valid
    if cache["data"] and current_time - cache["timestamp"] < CACHE_DURATION:
        return jsonify(cache["data"])

    # Otherwise, fetch fresh data
    results = {}
    results["event1"] = get_registration_count(EVENTS["event1"], MAX_SEATS)
    results["event2"] = get_registration_count(EVENTS["event2"], MAX_SEATS)

    # Update cache
    cache["timestamp"] = current_time
    cache["data"] = results

    return jsonify(results)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
