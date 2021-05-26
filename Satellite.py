import math
from datetime import *
import numpy as np
from urllib.request import urlopen


class Satellite:
    mask = 0
    satelliteDict = {}
    selectedDay = [2021, 3, 1, 0, 00, 00]

    def __init__(self, nrSatellite, selectedDate):
        self.nrSatellite = nrSatellite
        self.parameterOfSatellite = []
        self.coordSatellite = np.zeros([0, 3])
        self.selectedDate = selectedDate
        if not Satellite.satelliteDict:
            openFile()

    def getNrSatellite(self):
        return self.nrSatellite

    def getDate(self):
        return self.selectedDate

    def getParameter(self):
        deltaTime = self.getDeltaTime()
        nParameter = self.getNParameter()
        Mk = self.getMk()
        Ek = self.getEk()
        vk = self.getVk()
        fiK = self.getFiK()
        rK = self.getRadiusK()
        xk, yk = self.getPositionSatellite()
        omegaK = self.getOmegaK()
        Xk, Yk, Zk = self.getCoordSatellite()
        return [deltaTime, nParameter, Mk, Ek, vk, fiK, rK, xk, yk, omegaK, Xk, Yk, Zk]

    def getDeltaTime(self):
        toA = self.parameterOfSatellite[4]
        gps_week = self.parameterOfSatellite[13]
        tSelectDay = self.calcTimeOfAlmanac()
        toa = gps_week * 604800 + toA
        return tSelectDay - toa

    def calcTimeOfAlmanac(self):
        year, month, day, hour, minute, second = setVariableFromDate(self.selectedDate)
        daysFromStartGPStoDate = date.toordinal(date(year, month, day)) - date.toordinal(date(1980, 1, 6))
        weekFromStartGPStoDate = daysFromStartGPStoDate // 7
        numberOfDayInWeek = daysFromStartGPStoDate % 7
        towParameter = numberOfDayInWeek * 86400 + hour * 3600 + minute * 60 + second
        weekFromStartGPStoDate -= 2048
        return weekFromStartGPStoDate * 604800 + towParameter

    def getNParameter(self):
        U = 3.986004415 * 10 ** 14
        a = self.parameterOfSatellite[7] ** 2
        return math.sqrt(U / a ** 3)

    def getMk(self):
        mAnomalia = self.parameterOfSatellite[10]
        deltaTime = self.getDeltaTime()
        nParameter = self.getNParameter()
        mK = mAnomalia + nParameter * deltaTime
        mK %= 2 * math.pi
        return mK

    def getEk(self):
        e = self.parameterOfSatellite[3]
        Mk = self.getMk()
        previousE = Mk
        nextE = Mk + e * math.sin(previousE)
        while abs((previousE - nextE)) > 10 ** (-15):
            previousE = nextE
            nextE = Mk + e * math.sin(previousE)
        return nextE

    def getVk(self):
        e = self.parameterOfSatellite[3]
        Ek = self.getEk()
        vk = math.atan2(math.sqrt(1 - e ** 2) * math.sin(Ek), math.cos(Ek) - e)
        return vk if vk > 0 else vk + 2 * math.pi

    def getFiK(self):
        vk = self.getVk()
        perigeeParameter = self.parameterOfSatellite[9]
        return vk + perigeeParameter

    def getRadiusK(self):
        e = self.parameterOfSatellite[3]
        a = self.parameterOfSatellite[7] ** 2
        Ek = self.getEk()
        return a * (1 - e * math.cos(Ek))

    def getPositionSatellite(self):
        rK = self.getRadiusK()
        fiK = self.getFiK()
        xk = rK * math.cos(fiK)
        yk = rK * math.sin(fiK)
        return xk, yk

    def getOmegaK(self):
        wE = 7.2921151467 * 10 ** (-5)
        toA = self.parameterOfSatellite[4]
        RoRA = self.parameterOfSatellite[6]
        RAW = self.parameterOfSatellite[8]
        deltaTime = self.getDeltaTime()
        return RAW + (RoRA - wE) * deltaTime - wE * toA

    def getCoordSatellite(self):
        self.setTableOfParameter()
        orbitIncl = self.parameterOfSatellite[5]
        xk, yk = self.getPositionSatellite()
        omegaK = self.getOmegaK()
        Xk = xk * math.cos(omegaK) - yk * math.cos(orbitIncl) * math.sin(omegaK)
        Yk = xk * math.sin(omegaK) + yk * math.cos(orbitIncl) * math.cos(omegaK)
        Zk = yk * math.sin(orbitIncl)
        return np.array([Xk, Yk, Zk])

    def getCoordForAllSatellite(self):
        for nrSatellite in range(1, 32):
            self.nrSatellite = nrSatellite
            self.setTableOfParameter()
            self.setTableOfCoordSatellite()
        return self.coordSatellite

    def setTableOfCoordSatellite(self):
        coordSatellite = self.getCoordSatellite()
        self.coordSatellite = np.append(self.coordSatellite, coordSatellite)

    def setTableOfParameter(self):
        nameSatellite = Satellite.satelliteDict[self.nrSatellite][0][0]
        idSatellite = int(Satellite.satelliteDict[self.nrSatellite][1][1])
        health = float(Satellite.satelliteDict[self.nrSatellite][2][1])
        eParameter = float(Satellite.satelliteDict[self.nrSatellite][3][1])
        toA = float(Satellite.satelliteDict[self.nrSatellite][4][1])
        orbitIncl = float(Satellite.satelliteDict[self.nrSatellite][5][1])
        RoRA = float(Satellite.satelliteDict[self.nrSatellite][6][1])
        aSqrt = float(Satellite.satelliteDict[self.nrSatellite][7][1])
        RAW = float(Satellite.satelliteDict[self.nrSatellite][8][1])
        perigeeParameter = float(Satellite.satelliteDict[self.nrSatellite][9][1])
        mAnomalia = float(Satellite.satelliteDict[self.nrSatellite][10][1])
        Af0 = float(Satellite.satelliteDict[self.nrSatellite][11][1])
        Af1 = float(Satellite.satelliteDict[self.nrSatellite][12][1])
        gps_week = int(Satellite.satelliteDict[self.nrSatellite][13][1])
        self.parameterOfSatellite = [nameSatellite, idSatellite, health, eParameter, toA, orbitIncl, RoRA, aSqrt, RAW,
                                     perigeeParameter, mAnomalia, Af0, Af1, gps_week]

    def saveTableOfCoordSatellite(self):
        np.savetxt('coords.txt', self.coordSatellite, delimiter='    ', fmt='%.3f')


def openFile():
    emptySatelliteDictionary()

    with urlopen(getFileYUMA()) as file:
        numberSatellite = 1
        for line in file:
            parameterSatellite = ''.join(line.decode('utf-8').split()).split(':')
            if not isEmptyLine(parameterSatellite):
                Satellite.satelliteDict[numberSatellite].append(parameterSatellite)
            else:
                numberSatellite += 1


def getFileYUMA():
    yuma = {0: "061440", 86400: "147456", 172800: "233472", 259200: "319488", 345600: "405504", 432000: "503808",
            518400: "589824"}
    dDay = date.toordinal(
        date(Satellite.selectedDay[0], Satellite.selectedDay[1], Satellite.selectedDay[2])) - date.toordinal(
        date(1980, 1, 6))
    week = dDay // 7
    day = dDay % 7
    tow = day * 86400
    week -= 2048
    return f'https://celestrak.com/GPS/almanac/Yuma/{Satellite.selectedDay[0]}/almanac.yuma.week{str(week).zfill(4)}.{yuma[tow]}.txt'


def emptySatelliteDictionary():
    numberOfSatelliteWithoutOne = 31
    for key in range(1, numberOfSatelliteWithoutOne + 1):
        Satellite.satelliteDict[key] = []


def isEmptyLine(line):
    return line == ['']


def setVariableFromDate(data):
    return data[0], data[1], data[2], data[3], data[4], data[5]


def setGPSDay():
    return Satellite.selectedDay


def getHoursPerDay():
    day = setGPSDay()
    startDate = datetime(day[0], day[1], day[2], day[3], day[4], day[5])
    endDate = startDate + timedelta(days=1)
    dateRange = []
    while startDate <= endDate:
        dateRange.append(startDate)
        startDate += timedelta(minutes=10)
    return dateRange

