import pandas as pd
import plotly
import plotly.graph_objs as go
import json
import numpy as np
import math
from GPS import GPS
from Satellite import setGPSDay, Satellite, getHoursPerDay
from visibleSatellite import gpsVisibleSatellite


def dopPlot(point):
    dt = getDOP(point)
    fig = go.Figure()
    for i in range(1, len(dt.columns)):
        fig.add_trace(go.Scatter(x=dt['hour'],
                                 y=dt.iloc[:, i],
                                 mode='lines',
                                 name=f"{dt.columns[i]}"
                                 ))

    fig.update_layout(
        title_text="DOPs",
        hovermode='x',
        title_x=0.5,
        autosize=False,
        width=1500,
        height=500,
        yaxis=dict(
            title_text="DOP values",
            range=(0, dt.iloc[:, 1:len(dt.columns)].max() + 1)
        ),
        xaxis=dict(
            title_text="GPS time [h]",
            dtick=3600000 * 2
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON


def getDOP(gpsCoord):
    dt = pd.DataFrame([])
    gdop = []
    pdop = []
    tdop = []
    hdop = []
    vdop = []
    hours = getHoursPerDay()
    for hour in hours:
        selectedDate = [int(hour.strftime("%Y")), int(hour.strftime("%m")), int(hour.strftime("%d")),
                        int(hour.strftime("%H")), int(hour.strftime("%M")), int(hour.strftime("%S"))]
        matrixQ = getQ(gpsCoord, selectedDate)
        gdop.append(round(getGDOP(matrixQ), 3))
        pdop.append(round(getPDOP(matrixQ), 3))
        tdop.append(round(getTDOP(matrixQ), 3))
        hdop.append(round(getHDOP(gpsCoord, matrixQ), 3))
        vdop.append(round(getVDOP(gpsCoord, matrixQ), 3))
    dt['hour'] = hours
    dt['Geometrical'] = gdop
    dt['Position'] = pdop
    dt['Time'] = tdop
    dt['Horizontal'] = hdop
    dt['Vertical'] = vdop
    return dt


def getQ(gpsCoord, hour):
    matrixA = np.zeros([0, 4])
    for nrSatellite in gpsVisibleSatellite(gpsCoord, hour):
        satellite = Satellite(nrSatellite, hour)
        recv = GPS(gpsCoord, satellite)
        satelliteXYZ = satellite.getCoordSatellite()
        gpsXYZ = recv.getXYZ()
        lengthVector = recv.getLengthVectorSatelliteGPS()
        matrixA = np.append(matrixA, np.array(
            [-(satelliteXYZ[0] - gpsXYZ[0]) / lengthVector, -(satelliteXYZ[1] - gpsXYZ[1]) / lengthVector,
             -(satelliteXYZ[2] - gpsXYZ[2]) / lengthVector, 1]))
    matrixA = np.reshape(matrixA, (matrixA.size // 4, 4))
    matrixQ = np.linalg.inv(np.dot(matrixA.T, matrixA))
    return matrixQ


def getGDOP(mat_Q):
    matrixQ = mat_Q
    return math.sqrt(matrixQ.diagonal()[0] + matrixQ.diagonal()[1] + matrixQ.diagonal()[2] + matrixQ.diagonal()[3])


def getPDOP(mat_Q):
    matrixQ = mat_Q
    return math.sqrt(matrixQ.diagonal()[0] + matrixQ.diagonal()[1] + matrixQ.diagonal()[2])


def getTDOP(mat_Q):
    matrixQ = mat_Q
    return math.sqrt(matrixQ.diagonal()[3])


def getQNEU(gpsCoord, mat_Q):
    gpsDay = setGPSDay()
    satellite = Satellite(None, gpsDay)
    recv = GPS(gpsCoord, satellite)
    rNEU = recv.getNEU()
    qXYZ = mat_Q[0:3, 0:3]
    qNEU = np.dot(np.dot(rNEU.T, qXYZ), rNEU)
    return qNEU


def getHDOP(gpsCoord, mat_Q):
    matrixQNEU = getQNEU(gpsCoord, mat_Q)
    return math.sqrt(matrixQNEU.diagonal()[0] + matrixQNEU.diagonal()[1])


def getVDOP(gpsCoord, mat_Q):
    matrixQNEU = getQNEU(gpsCoord, mat_Q)
    return math.sqrt(matrixQNEU.diagonal()[2])