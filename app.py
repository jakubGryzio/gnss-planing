from flask import Flask, render_template, request, redirect, url_for
from DOP import dopPlot
from Satellite import Satellite, openFile
from elevation import elevationPlot
from mapView import mapView
from positionMap import positionMap
from GPS import EllipsoidPoint
from skyPlot import skyPlot
from visibleSatellite import visibleSatellitePlot

app = Flask(__name__)

fi = "52.0000"
lamb = "21.0000"
h = "100"
mask = "0"
day = "2021-03-01"
time = "00:00"
map = positionMap(float(fi), float(lamb))
satellite = "all"
point = EllipsoidPoint()


def setDay(postDay):
    dayToChange = postDay.split('-')
    Satellite.selectedDay[0] = int(dayToChange[0])
    Satellite.selectedDay[1] = int(dayToChange[1])
    Satellite.selectedDay[2] = int(dayToChange[2])


def setTime(postTime):
    timeToChange = postTime.split(':')
    Satellite.selectedDay[3] = int(timeToChange[0])
    Satellite.selectedDay[4] = int(timeToChange[1])


def numberSatellite(SatelliteNumberToPlot):
    if "all" in SatelliteNumberToPlot:
        return SatelliteNumberToPlot
    else:
        return [int(elem) if int(elem) < 11 else int(elem) - 1 for elem in SatelliteNumberToPlot.split(',')]


@app.route('/', methods=['POST'])
def main():
    global fi, lamb, h, mask, day, time, point, map, satellite
    if request.method == 'POST':
        fi = request.form.get("fi")
        lamb = request.form.get("lamb")
        h = request.form.get("h")
        mask = request.form.get("mask")
        day = request.form.get("day")
        time = request.form.get("time")
        satellite = request.form.get("nrsat")
        point = EllipsoidPoint(float(fi), float(lamb), float(h))
        Satellite.mask = int(mask)
        setDay(day)
        setTime(time)
        Satellite.satelliteDict = {}
        openFile()
        map = positionMap(float(fi), float(lamb))
        return redirect(url_for('plots'))
    return render_template('main.html', fi=fi, lamb=lamb, h=h, mask=mask, day=day, time=time, mapPlot=map, satellite=satellite)


@app.route('/plots')
def plots():
    vsat = visibleSatellitePlot(point)
    elev = elevationPlot(point, numberSatellite(satellite))
    dop = dopPlot(point)
    return render_template('plots.html', plot=vsat, elevPlot=elev, dopPlot=dop)


@app.route('/sky_plot',  methods=['POST', 'GET'])
def sky_plot():
    global time
    sky = skyPlot(point)
    if request.method == 'POST':
        time = request.form.get("time")
        setTime(time)
        sky = skyPlot(point)
        return render_template('skyPlot.html', plot=sky, time=time)
    return render_template('skyPlot.html', plot=sky, time=time)


@app.route('/map_view', methods=['POST', 'GET'])
def map_view():
    global time
    map = mapView(point)
    if request.method == 'POST':
        time = request.form.get("time")
        setTime(time)
        map = mapView(point)
        return render_template('worldView.html', map=map, time=time)
    return render_template('worldView.html', map=map, time=time)


if __name__ == '__main__':
    app.run(debug=True)
