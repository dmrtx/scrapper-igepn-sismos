# -*- coding: utf-8 -*-
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from datetime import datetime, date
import pandas as pd
import time


class scrapperIgen():
    def __init__(self, startDate, endDate):
        self.dataFrame = pd.DataFrame()
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
        self.processDates()
        listaAniosEnlaces = self.filterDatesYear(listaAniosEnlaces, self.startDate.year, self.endDate.year)
        yearLinks = {}
        for i in (listaAniosEnlaces):
            lstMonthLinks = self.buscarSquareWithLinks(i[1], "square month", i[2])
            lstMonthLinks = self.filterDatesMonth(lstMonthLinks, i[0], date(self.startDate.year, self.startDate.month, 1),date(self.endDate.year, self.endDate.month, 1))
            monthLinks = {}
            if (len(lstMonthLinks) > 0):
                for month in lstMonthLinks:
                    lstDaysLinks = self.buscarSquareWithLinks(month[1], "square day", month[2])
                    lstDaysLinks = self.filterDatesDay(lstDaysLinks,i[0], month[0], self.startDate, self.endDate)
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
                        self.scrapeData(i[1])
                        time.sleep(1)

    def filterDatesYear(self, listaAniosEnlaces, start, end):
        if (not listaAniosEnlaces or not start or not end):
            return listaAniosEnlaces
        lstYearsFiltered = []
        for i in listaAniosEnlaces:
            if (int(i[0]) >= start and int(i[0]) <= end):
                lstYearsFiltered.append(i)
        return lstYearsFiltered;

    def filterDatesMonth(self, listaAniosEnlaces, year, startDate, endDate):
        if (not listaAniosEnlaces or not startDate or not endDate):
            return listaAniosEnlaces
        lstYearsFiltered = []
        for i in listaAniosEnlaces:
            testDate = date(year,int(i[0]),1)
            if (testDate >= startDate and testDate <= endDate):
                lstYearsFiltered.append(i)
        return lstYearsFiltered;

    def filterDatesDay(self, listaAniosEnlaces, year, month, startDate, endDate):
        if (not listaAniosEnlaces or not startDate or not endDate):
            return listaAniosEnlaces
        lstYearsFiltered = []
        for i in listaAniosEnlaces:
            testDate = date(year,month,int(i[0]))
            if (testDate >= startDate and testDate <= endDate):
                lstYearsFiltered.append(i)
        return lstYearsFiltered;

    def processDates(self):
        # verificar si hay datos con los que se pueda trabajar
        if (not self.startDate or not self.endDate):
            raise Exception("Rango de fechas es requerido")

        splitStart = self.startDate.split("/")
        splitEnd = self.endDate.split("/")
        if (not splitStart or not splitEnd or not len(splitStart) >= 3 or not len(splitEnd) >= 3 or splitStart[2] >
                splitEnd[2]):
            raise Exception("Rango de fechas es requerido")
        splitStart = [int(i) for i in splitStart]
        splitEnd = [int(i) for i in splitEnd]
        self.startDate = date(splitStart[2],splitStart[1],splitStart[0])
        self.endDate = date(splitEnd[2], splitEnd[1], splitEnd[0])
        return [self.startDate,self.endDate]

    def scrapeData(self, url):
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urlopen(req).read()
        bs = BeautifulSoup(data, 'html.parser')
        lstTables = bs.find_all("table", {"class": "events"})
        if (len(lstTables)>0):
            for table in lstTables:
                datasetLocal = []
                cabecera = list(td.get_text() for td in table.find_all("thead")[0].find_all("td"))
                cuerpo = table.find_all("tbody")[0];
                if (cuerpo):
                    if (cuerpo.find_all("tr")):
                        for row in cuerpo.find_all("tr"):
                            dataset = list(td.get_text() for td in row.find_all("td"))
                            if len(dataset)==12:
                                datasetLocal.append(dataset)
            df = pd.DataFrame(datasetLocal, columns=cabecera)
            frames = [df,self.dataFrame]
            self.dataFrame = pd.concat(frames)
        print(self.dataFrame)



    def writeFile(self):
        date_time = self.startDate.strftime("%m_%d_%Y") + "-" + self.endDate.strftime("%m_%d_%Y")
        self.dataFrame.to_csv(str(date_time + 'sismos.csv'), index=False, encoding='utf-8')