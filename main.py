# -*- coding: utf-8 -*-
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

months={"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12}
def sortAnio(e):
    return e[0]


def buscarAnios(basePath):
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
        if (len(enlaceAnio)>0):
            toDelete = enlaceAnio.split("/")[-1]
        listaAniosEnlaces.append((int(anio), basePathWoHtml + enlaceAnio, toDelete))
    listaAniosEnlaces.sort(key=sortAnio)
    print(listaAniosEnlaces)
    return listaAniosEnlaces


def buscarSquareWithLinks(basePath, squareType, toDelete):
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
            if (len(stringSquare.lower())>0 and stringSquare.lower() in months):
                stringSquare = months[stringSquare.lower()]
            linksSquare = i.find_all("a")
            if (len(linksSquare) > 0):
                linkSquare = linksSquare[0]["href"]
                if (len(linksSquare)>0):
                    toDelete = linkSquare.split("/")[-1]
                lstSquareLink.append((stringSquare, basePathWoHtml + linkSquare, toDelete))
    return lstSquareLink

basePath = "https://www.igepn.edu.ec/portal/eventos/www/browser.html"
listaAniosEnlaces = buscarAnios(basePath)
yearLinks = {}
for i in (listaAniosEnlaces):
    lstMonthLinks = buscarSquareWithLinks(i[1], "square month", i[2])
    monthLinks = {}
    if (len(lstMonthLinks) > 0):
        for month in lstMonthLinks:
            lstDaysLinks = buscarSquareWithLinks(month[1], "square day", month[2])
            monthLinks[month[0]] = lstDaysLinks
        yearLinks[i[0]] = monthLinks
print(yearLinks)



