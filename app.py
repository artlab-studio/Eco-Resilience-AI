folium.WmsTileLayer(
    url="https://lipad-fmc.dream.upd.edu.ph/geoserver/wms",
    layers="geonode:ph160202000_fh5yr_30m",
    name="Flood Hazard",
    fmt="image/png",
    transparent=True,
    overlay=True,
    control=True,
    attr="LiPAD / UP DREAM"
).add_to(m)
