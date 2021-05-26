import pandas as pd
import plotly
import plotly.graph_objs as go
import json
from GPS import GPS
from Satellite import Satellite, getHoursPerDay


def visibleSatellitePlot(point):
    df = visibleSatelliteCounter(point)
    fig = go.Figure(
        go.Scatter(
            x=df['hour'],
            y=df['visibleSatellite'],
            mode='lines',
            hovertemplate='<b>Time</b>: %{x}' +
                          '<br><b>Number</b>: %{y}',
            name="GPS",
            stackgroup='one'
        )
    )

    fig.update_layout(
        title_text="Visible satellite",
        title_x=0.5,
        autosize=False,
        width=1500,
        height=500,
        yaxis=dict(
            title_text="Number of satellite",
            range=(0, 20)
        ),
        xaxis=dict(
            title_text="GPS time [h]",
            dtick=3600000 * 2
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def visibleSatelliteCounter(point):
    dt = pd.DataFrame([])
    visibleSatelliteCount = []
    gpsCoord = point
    for hour in getHoursPerDay():
        selectedDate = [int(hour.strftime("%Y")), int(hour.strftime("%m")), int(hour.strftime("%d")),
                        int(hour.strftime("%H")), int(hour.strftime("%M")), int(hour.strftime("%S"))]
        visibleSatelliteCount.append(len(gpsVisibleSatellite(gpsCoord, selectedDate)))
    dt['hour'] = getHoursPerDay()
    dt['visibleSatellite'] = visibleSatelliteCount
    return dt


def gpsVisibleSatellite(gpsCoord, selectedDate):
    visibleSatellite = []
    for i in range(1, 32):
        satellite = Satellite(i, selectedDate)
        recv = GPS(gpsCoord, satellite)
        if recv.getElevation() > satellite.mask:
            visibleSatellite.append(satellite.nrSatellite)
    return visibleSatellite
