m = folium.Map(
    location=[8.9534, 125.5288],
    zoom_start=12,
    tiles=get_folium_tiles(basemap_choice)
)

# ADD REAL FLOOD HAZARD (WMS)
folium.raster_layers.WmsTileLayer(
    url="https://lipad-fmc.dream.upd.edu.ph/geoserver/wms",
    name="Flood Hazard (LiDAR)",
    layers="geonode:ph160202000_fh5yr_30m",
    fmt="image/png",
    transparent=True,
    overlay=True,
    control=True
).add_to(m)

# Barangay points (temporary)
for _, r in barangay_data.iterrows():
    folium.CircleMarker(
        location=[r["Latitude"], r["Longitude"]],
        radius=5,
        color="#184d3b",
        fill=True,
        fill_color="#7bc8b6",
        fill_opacity=0.8,
        popup=f"{r['Barangay']}"
    ).add_to(m)

folium.LayerControl().add_to(m)

st_folium(m, height=600)
