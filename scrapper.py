import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import pytz  # added for timezone handling

EVENTS = {
    "event1": "https://gravitas.vit.ac.in/events/e72677fb-caaa-43b5-99ce-24bf878ff242",
    "event2": "https://gravitas.vit.ac.in/events/00cee489-395a-47f6-bacc-46066160caa8"
}

MAX_SEATS = 200
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_registration_count(url, max_seats):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        divs = soup.select("div.text-white\\/70.text-sm.sm\\:text-base")

        for div in divs:
            text = div.get_text(" ", strip=True)
            if "seats left" in text:
                match = re.search(r"(\d+)\s*seats left", text)
                if match:
                    seats_left = int(match.group(1))
                    return {
                        "registered": max_seats - seats_left,
                        "remaining": seats_left
                    }
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def main():
    results = {}
    results["event1"] = get_registration_count(EVENTS["event1"], MAX_SEATS)
    results["event2"] = get_registration_count(EVENTS["event2"], MAX_SEATS)

    # Get IST timestamp
    ist = pytz.timezone("Asia/Kolkata")
    now_ist = datetime.now(ist)
    results["last_updated"] = now_ist.strftime("%Y-%m-%d %H:%M:%S")

    with open("data.json", "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()
