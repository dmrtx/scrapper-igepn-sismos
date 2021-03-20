from scrapperIgen import scrapperIgen
startDate = "01/01/2021"
endDate = "31/01/2021"
scrapper = scrapperIgen(startDate, endDate)
results = scrapper.scrape();
scrapper.writeFile()