import pandas as pd
import folium
from folium.plugins import Fullscreen


# ============================================================
# 1. LOAD PROCESSED GRID DATA
# ============================================================

DATA_FILE = "../data/processed/processed_data.csv"
OUTPUT_FILE = "substation_map.html"

df = pd.read_csv(DATA_FILE)


# ============================================================
# 2. PREPARE SUBSTATION DATA
# ============================================================

# Source substations
source_cols = [
    "Source Substation ID",
    "Source Substation",
    "Source Region",
    "Source Latitude",
    "Source Longitude",
    "Source Voltage (kV)",
    "Source Capacity (MVA)",
    "Source Status"
]

sources = df[source_cols].copy()
sources.columns = [
    "ID",
    "Name",
    "Region",
    "Latitude",
    "Longitude",
    "Voltage",
    "Capacity",
    "Status"
]

# Destination substations
destination_cols = [
    "Destination Substation ID",
    "Destination Substation",
    "Destination Region",
    "Destination Latitude",
    "Destination Longitude",
    "Destination Voltage (kV)",
    "Destination Capacity (MVA)",
    "Destination Status"
]

destinations = df[destination_cols].copy()
destinations.columns = [
    "ID",
    "Name",
    "Region",
    "Latitude",
    "Longitude",
    "Voltage",
    "Capacity",
    "Status"
]

# Combine source and destination substations
substations = pd.concat(
    [sources, destinations],
    ignore_index=True
)

# Remove duplicates
substations = substations.drop_duplicates(subset="ID")

# Remove records without coordinates
substations = substations.dropna(
    subset=["Latitude", "Longitude"]
)


# ============================================================
# 3. VOLTAGE COLOUR FUNCTION
# ============================================================

def voltage_color(voltage):
    """
    Assign a visual category to a substation based on voltage.
    """

    if pd.isna(voltage):
        return "gray"

    voltage = float(voltage)

    if voltage >= 330:
        return "red"

    elif voltage >= 220:
        return "orange"

    elif voltage >= 132:
        return "green"

    elif voltage >= 69:
        return "blue"

    else:
        return "purple"


# ============================================================
# 4. CREATE BASE MAP
# ============================================================

# Calculate map centre from available coordinates
center_lat = substations["Latitude"].mean()
center_lon = substations["Longitude"].mean()

grid_map = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=7,
    tiles="CartoDB positron"
)


# ============================================================
# 5. CREATE VOLTAGE LAYERS
# ============================================================

voltage_layers = {
    "330 kV+": folium.FeatureGroup(name="330 kV+", show=True),
    "220–329 kV": folium.FeatureGroup(name="220–329 kV", show=True),
    "132–219 kV": folium.FeatureGroup(name="132–219 kV", show=True),
    "69–131 kV": folium.FeatureGroup(name="69–131 kV", show=True),
    "Below 69 kV": folium.FeatureGroup(name="Below 69 kV", show=True),
    "Unknown Voltage": folium.FeatureGroup(name="Unknown Voltage", show=True)
}


def voltage_layer(voltage):

    if pd.isna(voltage):
        return voltage_layers["Unknown Voltage"]

    voltage = float(voltage)

    if voltage >= 330:
        return voltage_layers["330 kV+"]

    elif voltage >= 220:
        return voltage_layers["220–329 kV"]

    elif voltage >= 132:
        return voltage_layers["132–219 kV"]

    elif voltage >= 69:
        return voltage_layers["69–131 kV"]

    else:
        return voltage_layers["Below 69 kV"]


# ============================================================
# 6. ADD SUBSTATIONS
# ============================================================

for _, station in substations.iterrows():

    popup_html = f"""
    <div style="font-family: Arial; width: 250px;">
        <h4>{station['Name']}</h4>

        <b>Substation ID:</b> {station['ID']}<br>
        <b>Region:</b> {station['Region']}<br>
        <b>Voltage:</b> {station['Voltage']} kV<br>
        <b>Capacity:</b> {station['Capacity']} MVA<br>
        <b>Status:</b> {station['Status']}<br>
    </div>
    """

    marker = folium.CircleMarker(
        location=[
            station["Latitude"],
            station["Longitude"]
        ],
        radius=7,
        color=voltage_color(station["Voltage"]),
        fill=True,
        fill_color=voltage_color(station["Voltage"]),
        fill_opacity=0.8,
        weight=2,
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        tooltip=station["Name"]
    )

    marker.add_to(
        voltage_layer(station["Voltage"])
    )


# ============================================================
# 7. ADD TRANSMISSION LINES
# ============================================================

line_layer = folium.FeatureGroup(
    name="Transmission Lines",
    show=True
)

for _, line in df.iterrows():

    source_lat = line["Source Latitude"]
    source_lon = line["Source Longitude"]

    destination_lat = line["Destination Latitude"]
    destination_lon = line["Destination Longitude"]

    # Skip lines with missing coordinates
    if pd.isna(source_lat) or pd.isna(source_lon):
        continue

    if pd.isna(destination_lat) or pd.isna(destination_lon):
        continue

    popup_html = f"""
    <div style="font-family: Arial; width: 250px;">
        <h4>Transmission Line</h4>

        <b>Line ID:</b> {line['Line ID']}<br>
        <b>From:</b> {line['Source Substation']}<br>
        <b>To:</b> {line['Destination Substation']}<br>
        <b>Voltage:</b> {line['Line Voltage (kV)']} kV<br>
        <b>Length:</b> {line['Line Length (km)']} km<br>
        <b>Capacity:</b> {line['Line Capacity (MVA)']} MVA<br>
        <b>Status:</b> {line['Line Status']}<br>
        <b>Type:</b> {line['Line Type']}<br>
    </div>
    """

    folium.PolyLine(
        locations=[
            [source_lat, source_lon],
            [destination_lat, destination_lon]
        ],
        weight=3,
        opacity=0.7,
        popup=folium.Popup(
            popup_html,
            max_width=300
        ),
        tooltip=f"{line['Source Substation']} → "
                f"{line['Destination Substation']}"
    ).add_to(line_layer)


# ============================================================
# 8. ADD ALL LAYERS TO MAP
# ============================================================

for layer in voltage_layers.values():
    layer.add_to(grid_map)

line_layer.add_to(grid_map)


# ============================================================
# 9. ADD CONTROLS
# ============================================================

folium.LayerControl(
    collapsed=False
).add_to(grid_map)

Fullscreen(
    position="topright"
).add_to(grid_map)


# ============================================================
# 10. ADD TITLE
# ============================================================

title_html = """
<div style="
    position: fixed;
    top: 10px;
    left: 50px;
    z-index: 9999;
    background-color: white;
    padding: 10px 18px;
    border-radius: 6px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
">
    <h3 style="margin: 0;">
        National Electricity Grid Network Map
    </h3>
</div>
"""

grid_map.get_root().html.add_child(
    folium.Element(title_html)
)


# ============================================================
# 11. SAVE MAP
# ============================================================

grid_map.save(OUTPUT_FILE)

print("GIS map successfully created.")
print(f"Substations mapped: {len(substations)}")
print(f"Transmission lines mapped: {len(df)}")
print(f"Output: {OUTPUT_FILE}")