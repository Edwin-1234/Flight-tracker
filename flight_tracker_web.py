import streamlit as st
import requests
import os
from dotenv import load_dotenv
import folium
from streamlit_folium import st_folium


# Load environment variables
load_dotenv()
API_KEY = os.getenv("AVIATIONSTACK_API_KEY")


# Function to get flight data
def get_flight_status(flight_number):
    url = f"http://api.aviationstack.com/v1/flights?access_key={API_KEY}&flight_iata={flight_number}"
    response = requests.get(url)
    data = response.json()

    if 'data' not in data or len(data['data']) == 0:
        return None

    flight = data['data'][0]  # get the latest or first result
    return {
        "Airline": flight['airline']['name'],
        "Flight Number": flight['flight']['iata'],
        "Departure": f"{flight['departure']['airport']} at {flight['departure'].get('estimated') or flight['departure']['scheduled']}",
        "Arrival": f"{flight['arrival']['airport']} at {flight['arrival'].get('estimated') or flight['arrival']['scheduled']}",
        "Delay (min)": flight['departure'].get('delay'),

        "Status": flight['flight_status'],
        "Latitude": flight['live']['latitude'] if flight.get('live') else None,
        "Longitude": flight['live']['longitude'] if flight.get('live') else None
    }

# Streamlit UI
st.title("✈️ Flight Tracker App")

flight_no = st.text_input("Enter Flight IATA Number (e.g., AI302):")

if flight_no:
    result = get_flight_status(flight_no)
    if result:
        st.success("Flight Found!")
        for key, value in result.items():
            if key == "Delay (min)" and value:
                st.warning(f"⏰ Delay: {value} minutes")
            elif key not in ["Latitude", "Longitude", "Delay (min)"] and value:
                st.write(f"**{key}:** {value}")
        
        if result.get("Latitude") and result.get("Longitude"):
            st.subheader("🗺️ Live Flight Location (if available)")
            m = folium.Map(location=[result["Latitude"], result["Longitude"]], zoom_start=6)
            folium.Marker(
                location=[result["Latitude"], result["Longitude"]],
                tooltip=f"Flight {result['Flight Number']}",
                icon=folium.Icon(icon="plane", prefix="fa", color="blue")
            ).add_to(m)
            st_folium(m, width=700, height=500)
        else:
            st.info("Live location not available for this flight.")
    else:
        st.error("Flight not found or API limit reached.")
