import pandas as pd
import plotly
import plotly.graph_objs as go
import json
import numpy as np
import math
from GPS import GPS
from Satellite import setGPSDay, Satellite, getHoursPerDay
from visibleSatellite import gpsVisibleSatellite


def mapView(point):
    lon = lonSatellite(point)
    lat = latSatellite(point)
    mapbox_access_token = 'pk.eyJ1IjoiamFrdWJncnl6aW8iLCJhIjoiY2toeDlyOTVhMDVtdDJxbzducmV1aWZndyJ9.TClJXnJE1ALnmPi25y0m3Q'
    fig = go.Figure()
    for i in range(0, len(lon.columns) - 1):
        fig.add_trace(go.Scattermapbox(
            mode="lines",
            lon=lon.iloc[0:np.where(lon.iloc[:, i].isna())[0][0] - 1, i],
            lat=lat.iloc[0:np.where(lat.iloc[:, i].isna())[0][0] - 1, i],
            line=dict(
                color='#89eb34',
                width=3
            ),
            showlegend=False,
            hoverinfo='skip'
        ))

        fig.add_trace(go.Scattermapbox(
            lat=[lat.iloc[0, i]],
            lon=[lon.iloc[0, i]],
            mode='markers+text',
            text=f"GPS0{lon.columns[i]}" if int(lon.columns[i]) < 11 else f"GPS{int(lon.columns[i]) + 1}", textposition="bottom right",
            textfont=dict(
                family="sans serif",
                size=15,
                color="black"
            ),
            hovertemplate='<b>Latitude</b>: %{lat}' +
                          '<br><b>Longitude</b>: %{lon}',
            showlegend=False,
            name=f"GPS0{lon.columns[i]}" if int(lon.columns[i]) < 11 else f"GPS{int(lon.columns[i]) + 1}",
            marker=go.scattermapbox.Marker(
                size=13,
            )
        ))

    fig.add_trace(go.Scattermapbox(
        lat=[np.rad2deg(point.getFi())],
        lon=[np.rad2deg(point.getLambda())],
        mode='markers',
        showlegend=False,
        hovertemplate='<b>Latitude</b>: %{lat}' +
                      '<br><b>Longitude</b>: %{lon}',
        name=f"Observation point",
        marker=go.scattermapbox.Marker(
            size=14,
            color='#3236a8'
        )
    ))
    fig.update_layout(
        hovermode='closest',
        width=1560,
        height=750,
        margin=dict(l=0, r=0, t=0, b=0),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            zoom=2,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=np.rad2deg(point.getFi()),
                lon=np.rad2deg(point.getLambda())
            ),
            pitch=0,
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def latLon(XYZ):
    r_delta = np.linalg.norm(XYZ[0:1])
    sinA = XYZ[1] / r_delta
    cosA = XYZ[0] / r_delta
    lon = math.atan2(sinA, cosA)
    if lon < -math.pi:
        lon += 2 * math.pi
    lat = math.asin(XYZ[2]/np.linalg.norm(XYZ))
    return [math.degrees(lat), math.degrees(lon)]


def latSatellitePerDay(nrSatellite, gpsCoord):
    lat = []
    for hour in getHoursPerDay():
        selectedDate = [int(hour.strftime("%Y")), int(hour.strftime("%m")), int(hour.strftime("%d")),
                        int(hour.strftime("%H")), int(hour.strftime("%M")), int(hour.strftime("%S"))]
        satellite = Satellite(nrSatellite, selectedDate)
        recv = GPS(gpsCoord, satellite)
        if recv.getElevation() > satellite.mask:
            lat.append(latLon(satellite.getCoordSatellite())[0])
        else:
            lat.append(None)
    return lat


def lonSatellitePerDay(nrSatellite, gpsCoord):
    lon = []
    for hour in getHoursPerDay():
        selectedDate = [int(hour.strftime("%Y")), int(hour.strftime("%m")), int(hour.strftime("%d")),
                        int(hour.strftime("%H")), int(hour.strftime("%M")), int(hour.strftime("%S"))]
        satellite = Satellite(nrSatellite, selectedDate)
        recv = GPS(gpsCoord, satellite)
        if recv.getElevation() > satellite.mask:
            lon.append(latLon(satellite.getCoordSatellite())[1])
        else:
            lon.append(None)
    return lon


def latSatellite(point):
    dt = pd.DataFrame([])
    for nrSatellite in gpsVisibleSatellite(point, setGPSDay()):
        dt[f"{nrSatellite}"] = latSatellitePerDay(nrSatellite, point)
    dt['hour'] = getHoursPerDay()
    return dt


def lonSatellite(point):
    dt = pd.DataFrame([])
    for nrSatellite in gpsVisibleSatellite(point, setGPSDay()):
        dt[f"{nrSatellite}"] = lonSatellitePerDay(nrSatellite, point)
    dt['hour'] = getHoursPerDay()
    return dt

