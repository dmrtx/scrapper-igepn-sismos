# -*- coding: utf-8 -*-
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import date


class scrapperIgen():
    def __init__(self, startDate, endDate):
        self.startDate = startDate
        self.endDate = endDate
        self.months = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "jul": 7, "aug": 8, "sep": 9,
                       "oct": 10, "nov": 11, "dec": 12}

    def sortAnio(self, e):
        return e[0]

    def buscarAnios(self, basePath):
        req = Request(basePath, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read()

        # Crear nueva URL para unir
        basePathWoHtml = basePath.replace("browser.html", "");

        bs = BeautifulSoup(data, 'html.parser')

        anios = bs.find_all("div", {"class", "square year"})
        listaAniosEnlaces = []
        for i in anios:
            anio = i.find_all("span", {"class", "label"})[0].string
            enlaces = i.find_all("a")
            enlaceAnio = enlaces[0]["href"]
            if (len(enlaceAnio) > 0):
                toDelete = enlaceAnio.split("/")[-1]
            listaAniosEnlaces.append((int(anio), basePathWoHtml + enlaceAnio, toDelete))
        listaAniosEnlaces.sort(key=self.sortAnio)
        print(listaAniosEnlaces)
        return listaAniosEnlaces

    def buscarSquareWithLinks(self, basePath, squareType, toDelete):
        print("Procesando url: " + basePath)
        # Crear nueva URL para unir
        basePathWoHtml = basePath.replace(toDelete, "")

        req = Request(basePath, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read()
        bs = BeautifulSoup(data, 'html.parser')
        divWithLinks = bs.find_all("div", {"class": squareType})
        lstSquareLink = []
        if (len(divWithLinks) > 0):
            for i in divWithLinks:
                stringSquare = i.find_all("span", {"class", "label"})[0].string
                if (len(stringSquare.lower()) > 0 and stringSquare.lower() in self.months):
                    stringSquare = self.months[stringSquare.lower()]
                linksSquare = i.find_all("a")
                if (len(linksSquare) > 0):
                    linkSquare = linksSquare[0]["href"]
                    if (len(linksSquare) > 0):
                        toDelete = linkSquare.split("/")[-1]
                    lstSquareLink.append((stringSquare, basePathWoHtml + linkSquare, toDelete))
        return lstSquareLink

    def scrape(self):
        basePath = "https://www.igepn.edu.ec/portal/eventos/www/browser.html"
        listaAniosEnlaces = self.buscarAnios(basePath)
        tupleYears = self.processDates(self.startDate, self.endDate)
        listaAniosEnlaces = self.filterDates(listaAniosEnlaces, tupleYears[0][2], tupleYears[1][2])
        yearLinks = {}
        for i in (listaAniosEnlaces):
            lstMonthLinks = self.buscarSquareWithLinks(i[1], "square month", i[2])
            lstMonthLinks = self.filterDates(lstMonthLinks, tupleYears[0][1], tupleYears[1][1])
            monthLinks = {}
            if (len(lstMonthLinks) > 0):
                for month in lstMonthLinks:
                    lstDaysLinks = self.buscarSquareWithLinks(month[1], "square day", month[2])
                    lstDaysLinks = self.filterDates(lstDaysLinks, tupleYears[0][0], tupleYears[1][0])
                    monthLinks[month[0]] = lstDaysLinks
                yearLinks[i[0]] = monthLinks
        print(yearLinks)
        for key in yearLinks:
            if (yearLinks[key]):
                monthLinks = yearLinks[key]
                for keyMonth in monthLinks:
                    dayLinks = monthLinks[keyMonth]
                    print(dayLinks)
                    for i in dayLinks:
                        print(i[1])

    def filterDates(self, listaAniosEnlaces, start, end):
        if (not listaAniosEnlaces or not start or not end):
            return listaAniosEnlaces

        lstYearsFiltered = []
        for i in listaAniosEnlaces:
            if (int(i[0]) >= start and int(i[0]) <= end):
                lstYearsFiltered.append(i)
        return lstYearsFiltered;

    def processDates(self, startDate, endDate):
        # verificar si hay datos con los que se pueda trabajar
        if (not startDate or not endDate):
            return []

        splitStart = startDate.split("/")
        splitEnd = endDate.split("/")
        if (not splitStart or not splitEnd or not len(splitStart) == 3 or not len(splitEnd) == 3 or splitStart[2] >
                splitEnd[2]):
            print("Rango de fechas Incorrecto")
            return []
        splitStart = [int(i) for i in splitStart]
        splitEnd = [int(i) for i in splitEnd]
        return (splitStart, splitEnd)

