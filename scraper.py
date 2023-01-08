import requests as rq
import pandas as pd

from bs4 import BeautifulSoup as bs4


class Scraper:
    """
        A class used to represent a collection of methods used for scraping specific
        elements from the table, gathered by the Parser class

        ...

        Attributes
        ----------
        self.url : str
                a formatted string, representing the link to which a get request is sent
                in order for the HTML to be gathered
            self.html_get : response
                contains a response object received by the request sent to self.url
            self.page_html : str
                the result from self.html_get passed through the Beautiful Soup 4 module
                as it is readable
            self.table_gasstations :
                the filtered table meant to be used for further scraping of specific elements


        Methods
        -------
        dataframe_conversion
        table_scraping
        fuel_types_scraping
        """

    def __init__(self):
        self.url = "https://fuelo.net/gasstations/settlement/4342?lang=bg"
        self.html_get = rq.get(self.url)
        self.page_html = bs4(self.html_get.text, "html.parser")
        self.table_gasstations = self.page_html.find("tbody")

    def dataframe_conversion(self):

        """
        Method that converts the given input (data) into a Pandas dataframe
        and inserts it into a .csv file
        :param:
        a list of lists from which a Pandas dataframe is built
        """
        data = self.table_scraping()
        full_data_dataframe = pd.DataFrame(data, columns=["Gas Station", "Address", "Link"])
        full_data_dataframe.to_csv("GasStationData.csv", index=False)

    def table_scraping(self):
        """
        Function that uses the self.table_gasstations from the Parser class,
        scrapes specific elements from the table and returns them
        :return:
        a list of lists (data) - titles, addresses, links meant to be turned into a Pandas Dataframe
        """

        titles = []
        for text in self.table_gasstations.find_all('a'):
            gas_station_name = text.getText()
            titles.append(gas_station_name)

        addresses = []
        thread_list = self.table_gasstations.find_all('tr')
        for td in thread_list:
            add = td.find_all('td')[1]
            address = add.getText()
            addresses.append(address)

        links = []
        for a in self.table_gasstations.find_all('a', href=True):
            links.append(["https://bg.fuelo.net" + a['href']])

        data = []
        for i in range(len(titles)):
            element = [titles[i], addresses[i], links[i][0]]
            data.append(element)

        return data

    def fuel_types_scraping(self):
        """
        Scrapes all offered types of fuels from table_gasstations
        :return:
        set of string values for the fuel types
        """
        fuel_types = set()
        for img in self.table_gasstations.find_all("img", title=True):
            fuel_types.add(img["title"])
        return fuel_types


if __name__ == "__main__":
    scr = Scraper()
    scr.dataframe_conversion()
