import plotly
import plotly.graph_objs as go
import json
import numpy as np
from Satellite import setGPSDay, Satellite
from elevation import getElevation, getAzimuth
from visibleSatellite import gpsVisibleSatellite


def skyPlot(point):
    dtElev = getElevation(point, gpsVisibleSatellite(point, setGPSDay()))
    dtAzimuth = getAzimuth(point, gpsVisibleSatellite(point, setGPSDay()))
    fig = go.Figure()
    for i in range(len(dtElev.columns) - 1):
        fig.add_trace(go.Scatterpolar(
            r=[90 - elem for elem in dtElev.iloc[0:np.where(dtElev.iloc[:, i].isna())[0][0] - 1, i]],
            theta=dtAzimuth.iloc[0:np.where(dtAzimuth.iloc[:, i].isna())[0][0] - 1, i],
            mode='lines',
            hovertemplate='<b>cosZ</b>: %{r}' +
                          '<br><b>Azimuth</b>: %{theta}',
            name=f"GPS0{dtElev.columns[i]}" if int(dtElev.columns[i]) < 11 else f"GPS{int(dtElev.columns[i]) + 1}",
            showlegend=False,
            line_color='#89eb34'
        ))

        fig.add_trace(go.Scatterpolar(
            r=[90 - dtElev.iloc[0, i]],
            theta=[dtAzimuth.iloc[0, i]],
            mode='markers+text',
            showlegend=False,
            text=f"GPS0{dtElev.columns[i]}" if int(dtElev.columns[i]) < 11 else f"GPS{int(dtElev.columns[i]) + 1}",
            textfont=dict(
                family="sans serif",
                size=18,
                color="black"
            ),
            textposition="top center",
            hovertemplate='<b>cosZ</b>: %{r}' +
                          '<br><b>Azimuth</b>: %{theta}',
            marker=dict(size=20, symbol='bowtie', line=dict(
                color='#182e06',
                width=2
            )),
            name=f"GPS0{dtElev.columns[i]}" if int(dtElev.columns[i]) < 11 else f"GPS{int(dtElev.columns[i]) + 1}"
        ))

    fig.add_trace(go.Scatterpolar(
        r=[90 - Satellite.mask for _i in range(0, 361)],
        theta=[i for i in range(0, 361)],
        mode='lines',
        line=dict(
            color='#0541e6',
            width=3
        ),
        name = f"Mask: {Satellite.mask}"
    ))

    fig.update_layout(
        width=800,
        height=800,
        margin=dict(l=0, r=0, t=0, b=0),
        polar=dict(
            radialaxis=dict(
                tickfont_size=12,
                dtick=30,
                range=(0, 90)
            ),
            angularaxis=dict(
                tickfont_size=15,
                rotation=90,
                direction="clockwise",
                dtick=90
            ),
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON