import json
import plotly
import plotly.graph_objects as go


def positionMap(lat, long):
    mapbox_access_token = 'pk.eyJ1IjoiamFrdWJncnl6aW8iLCJhIjoiY2toeDlyOTVhMDVtdDJxbzducmV1aWZndyJ9.TClJXnJE1ALnmPi25y0m3Q'

    fig = go.Figure(go.Scattermapbox(
        lat=[f'{lat}'],
        lon=[f'{long}'],
        hovertemplate='<i>%{text}</i>',
        text=['Latitude:{} Longitude: {}'.format(lat, long)],
        mode='markers',
        name='RECV',
        marker=go.scattermapbox.Marker(
            size=10
        )
    ))

    fig.update_layout(
        hovermode='closest',
        width=350,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        mapbox=dict(
            accesstoken=mapbox_access_token,
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=lat,
                lon=long - 1
            ),
            pitch=0,
            zoom=4
        )
    )

    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return graphJSON
