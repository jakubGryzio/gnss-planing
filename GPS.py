import numpy as np
import math


class EllipsoidPoint:
    def __init__(self, *args):
        if len(args) > 0:
            self.fi = np.deg2rad(args[0])
            self.lamb = np.deg2rad(args[1])
            self.h = args[2]
        else:
            self.fi = np.deg2rad(52.0)
            self.lamb = np.deg2rad(21.0)
            self.h = 100.0

    def getFi(self):
        return self.fi

    def getLambda(self):
        return self.lamb

    def getH(self):
        return self.h

    def __str__(self):
        return f"{self.fi}, {self.lamb}, {self.h}"


# noinspection PyUnresolvedReferences
class GPS:
    def __init__(self, point, satellite):
        self.point = point
        self.satellite = satellite

    def getXYZ(self):
        e2 = 0.00669438002290
        N = self.getN()
        fi, lamb, h = self.getCoord()
        X = (N + h) * math.cos(fi) * math.cos(lamb)
        Y = (N + h) * math.cos(fi) * math.sin(lamb)
        Z = (N * (1 - e2) + h) * math.sin(fi)
        return np.array([X, Y, Z])

    def getN(self):
        aElipsoid = 6378137
        e2 = 0.00669438002290
        return aElipsoid / (math.sqrt(1 - e2 * math.sin(self.point.getFi()) ** 2))

    def getCoord(self):
        return self.point.getFi(), self.point.getLambda(), self.point.getH()

    def getVectorSatelliteGPS(self):
        geocentric_XYZ = self.getXYZ()
        coordSatellite = self.satellite.getCoordSatellite()
        return np.transpose(np.array(coordSatellite - geocentric_XYZ))

    def getNEU(self):
        fi = self.point.getFi()
        lamb = self.point.getLambda()
        return np.array([[-math.sin(fi) * math.cos(lamb), -math.sin(lamb), math.cos(fi) * math.cos(lamb)],
                         [-math.sin(fi) * math.sin(lamb), math.cos(lamb), math.cos(fi) * math.sin(lamb)],
                         [math.cos(fi), 0, math.sin(fi)]])

    def getVectorNEU(self):
        return np.dot(np.transpose(self.getNEU()), self.getVectorSatelliteGPS())

    def getAzimuth(self):
        NEU = self.getVectorNEU()
        return np.rad2deg(math.atan2(NEU[1], NEU[0])) if np.rad2deg(math.atan2(NEU[1], NEU[0])) > 0 else np.rad2deg(
            math.atan2(NEU[1], NEU[0])) + 360

    def getElevation(self):
        NEU = self.getVectorNEU()
        return np.rad2deg(math.asin(NEU[2] / (math.sqrt(NEU[0] ** 2 + NEU[1] ** 2 + NEU[2] ** 2))))

    def getCosZ(self):
        NEU = self.getVectorNEU()
        return NEU[2] / (math.sqrt(NEU[0] ** 2 + NEU[1] ** 2 + NEU[2] ** 2))

    def getLengthVectorSatelliteGPS(self):
        vector = self.satellite.getCoordSatellite() - self.getXYZ()
        return np.linalg.norm(vector)