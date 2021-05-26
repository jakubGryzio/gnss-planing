import pandas as pd
import plotly
import plotly.graph_objs as go
import json
from GPS import GPS
from Satellite import Satellite, getHoursPerDay


def elevationPlot(point, numberSatellite):
    dt = getElevation(point, numberSatellite)
    fig = go.Figure()
    if Satellite.mask > 0:
        fig.add_trace(go.Scatter(x=dt['hour'],
                                 y=[float(Satellite.mask) for _i in range(len(dt['hour']))],
                                 mode='lines',
                                 name="Mask",
                                 hovertemplate='<b>Mask</b>: %{y}<sup>o</sup>',
                                 line=dict(color='royalblue', width=1, dash='dash')
                                 ))
    if "all" in numberSatellite:
        for i in range(1, 32):
            fig.add_trace(go.Scatter(x=dt['hour'],
                                     y=dt.iloc[:, i - 1],
                                     mode='lines',
                                     hovertemplate='<b>Time</b>: %{x}' +
                                                   '<br><b>Elevation</b>: %{y}<sup>o</sup>',
                                     name=f"GPS0{i}" if i < 11 else f"GPS{i + 1}"
                                     ))
    else:
        for i in range(len(numberSatellite)):
            fig.add_trace(go.Scatter(x=dt['hour'],
                                     y=dt.iloc[:, i],
                                     mode='lines',
                                     hovertemplate='<b>Time</b>: %{x}' +
                                                   '<br><b>Elevation</b>: %{y}<sup>o</sup><br>',
                                     name=f"GPS0{numberSatellite[i]}" if numberSatellite[
                                                                             i] < 11 else f"GPS{numberSatellite[i] + 1}"
                                     ))

    fig.update_layout(
        title_text="Elevation",
        title_x=0.5,
        autosize=False,
        width=1500,
        height=500,
        yaxis=dict(
            title_text="Elevation [o]",
            range=(0, 100)
        ),
        xaxis=dict(
            title_text="GPS time [h]",
            dtick=3600000 * 2
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getElevation(gpsCoord, numberSatellite):
    dt = pd.DataFrame([])
    if "all" in numberSatellite:
        for nrSatellite in range(1, 32):
            dt[f"{nrSatellite}"] = getElevationPerDay(nrSatellite, gpsCoord)
    else:
        for nrSatellite in numberSatellite:
            dt[f"{nrSatellite}"] = getElevationPerDay(nrSatellite, gpsCoord)
    dt['hour'] = getHoursPerDay()
    return dt


def getAzimuth(gpsCoord, numberSatellite):
    dt = pd.DataFrame([])
    for nrSatellite in numberSatellite:
        dt[f"{nrSatellite}"] = getAzimuthPerDay(nrSatellite, gpsCoord)
    dt['hour'] = getHoursPerDay()
    return dt


def getElevationPerDay(nrSatellite, gpsCoord):
    elev = []
    for hours in getHoursPerDay():
        selectedDate = [int(hours.strftime("%Y")), int(hours.strftime("%m")), int(hours.strftime("%d")),
                        int(hours.strftime("%H")), int(hours.strftime("%M")), int(hours.strftime("%S"))]
        satellite = Satellite(nrSatellite, selectedDate)
        recv = GPS(gpsCoord, satellite)
        if recv.getElevation() > satellite.mask:
            elev.append(recv.getElevation())
        else:
            elev.append(None)
    return elev


def getAzimuthPerDay(nrSatellite, gpsCoord):
    azimuth = []
    for hour in getHoursPerDay():
        selectedDate = [int(hour.strftime("%Y")), int(hour.strftime("%m")), int(hour.strftime("%d")),
                        int(hour.strftime("%H")), int(hour.strftime("%M")), int(hour.strftime("%S"))]
        satellite = Satellite(nrSatellite, selectedDate)
        recv = GPS(gpsCoord, satellite)
        if recv.getElevation() > satellite.mask:
            azimuth.append(recv.getAzimuth())
        else:
            azimuth.append(None)
    return azimuth
