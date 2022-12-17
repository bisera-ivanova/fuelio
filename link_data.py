import pandas as pd
import requests as re
from bs4 import BeautifulSoup as bs4
import time
from random import randint
from scraper import Scraper

STORE_FUEL_NAMES = [['Racing 100', 'ECTO 100', 'MaxxMotion 100', '100', 'V-Power Racing', '100 eXXtra Force',
                     '99+ Energy', 'A100', 'А-100 Н', 'A100 H', 'A-100', 'G-Drive 100', 'AVIA 95H', 'GTmax 100'],
                    ['Super 95', 'A95', 'Бензин А95', 'Бензин А95Н', 'Opti 95', 'A95 H', '95 Super', 'FuelSave 95',
                     'Бензин', 'А-95 Н', 'А95Н', 'Бензин А95-H', 'FuelSave 95', 'Бензин A95H', 'A-95', 'A-95',
                     'Efix 95', '95EKONOMY'],
                    ['V-Power 95', 'ECTO Plus 95', 'MaxxMotion A95'],
                    ['A98'],
                    ['Diesel EKONOMY', 'Super Diesel', 'Diesel', 'Efix Diesel', 'FuelSave Diesel', 'Diesel Pro Force',
                     'Opti Diesel', 'Дизел', 'Евро Дизел', 'DSL', 'ДГ', 'Дизел Б6', 'Дизелово гориво', 'AVIA Diesel'],
                    ['Diesel Double Filtered', 'ECTO Diesel', 'MaxxMotion Diesel', 'V-Power Diesel',
                     'Diesel Green Force', 'G-Drive Diesel', 'Топдизел', 'Diesel Premium', 'Супер дизел',
                     'GTmax Diesel', 'GOLD Diesel', 'Дизел плюс', 'Diesel+'],
                    ['Електричество', 'Електроколонка', 'Supercharger', 'EC CHARGING'],
                    ['Метан', 'LPG', 'Метан Еко'],
                    ['Пропан-Бутан', 'CNG', 'Автогаз', 'Blue Force Gas', 'AutoGas', 'Пропан Бутан', 'AUTOGAS',
                     'Autogas']]


class PricesNavScraper:
    """ A class used to represent a collection of methods for gathering data from the scraped links

    Attributes
    ----------
    self.data_source_col_names: list
        Collects the names of the columns of the pandas dataframe read from the .csv file
    self.data_source_df: dataframe
        Reads the .csv file passed onto it and converts it into the dataframe
    self.local_storage: list
        Collects the links from the third column of self.data_source_df

    Methods
    ----------
    reader_loop
    get_fuel_types
    get_fuel_types_vs_prices
    link_scraping

    """

    def __init__(self):
        self.data_source_col_names = ["Gas Station", "Address", "Link"]
        self.data_source_df = pd.read_csv('GasStationData.csv', skiprows=1, names=self.data_source_col_names)
        self.station_links = []

    def reader_loop(self):
        """
        Loops through the "Link" column of the data_source_df dataframe and inserts the links in the
        self.local_storage
        :return:
        self.local_storage: list
            links, which are to be used to scrape data
        """

        for item in self.data_source_df["Link"]:
            self.station_links.append(item)

    def get_fuel_types(self):
        """
        imports the fuel_types_scraping from the Scraper class to create
        a sorted list of values - the types of fuels being offered
        :return:
        sorted list, derived from the set
        """
        scraper = Scraper()
        fuel_types = scraper.fuel_types_scraping()
        return sorted([*fuel_types])

    def get_fuel_types_vs_prices(self, fuels_and_prices):
        """
        Function that takes as argument a dictionary, containing the scraped store names of the fuels and their prices,
        compares them to a reference (fuel_store_names_reference) and returns the main type of fuel + its price
        for each gas station
        :param fuels_and_prices: dictionary
            Containing the store fuel names as keys and their prices as values
        :return:
            final_dict: dictionary
            used for the creation of the final dataframe
        """
        print(fuels_and_prices)
        main_fuel_types = self.get_fuel_types()  # list of the main fuel types
        fuel_store_names_reference = dict(
            zip(main_fuel_types, STORE_FUEL_NAMES))  # key - main fuel type, value - store fuel name

        final_dict = {}
        for key, value in fuel_store_names_reference.items():
            for fuel, fuel_price in fuels_and_prices.items():
                if fuel in value:
                    final_dict[key] = fuel_price
                    break
                final_dict[key] = "None"

        return final_dict

    def scrape_links(self):
        """
        for each link in the self.local_storage, the function scrapes the navigation links, the store names
        and the prices for each fuel present in each gas station
        Then, collects the store names, compares them with the reference in get_fuel_types_vs_prices and
        returns a dataframe, which contains the final names, prices and navigation links and gets appended to
        self.datasource_df
        :return:
        self.data_source_df: dataframe
            updated dataframe containing prices, names of fuels and navigation links to each gas station
        """

        navigation_links = []
        prices = pd.DataFrame(columns=self.get_fuel_types())

        for link in self.station_links:
            response = re.get(link)
            time.sleep(randint(1, 7))
            html = bs4(response.text, "html.parser")
            navigation_link = html.find("a", {"class": "btn btn-secondary btn-large"}).get("href")
            fuel_table = html.find("tbody")
            fuel_name_getter = fuel_table.find_all("td", itemprop="name")
            fuel_price_getter = fuel_table.find_all("span", itemprop="price", content=True)

            navigation_links.append(navigation_link)

            fuel_names = self.compile_fuel_names(fuel_name_getter)

            fuel_prices = self.get_fuel_prices(fuel_price_getter)

            fuels_and_prices = dict(zip(fuel_names, fuel_prices))
            completed_prices = self.get_fuel_types_vs_prices(fuels_and_prices)
            prices = prices.append(completed_prices, ignore_index=True)

        frames = [self.data_source_df, prices]
        self.data_source_df = pd.concat(frames, axis=1)
        self.data_source_df["Navigation links"] = navigation_links

        return self.data_source_df

    def get_fuel_prices(self, fuel_price_getter):
        """
        Gets called in the scraped links function to generate the compiled list of prices
        :param fuel_price_getter: html as string
        :return:
        fuel_prices: lst
        compiled list of prices
        """
        fuel_prices = []
        for element in fuel_price_getter:
            fuel_price = r"{} лв/л.(kw/h)".format(element["content"].strip().replace("\t", ""))
            fuel_prices.append(fuel_price)
        return fuel_prices

    def compile_fuel_names(self, fuel_name_getter):
        """
        Gets called in the scraped links function to generate the compiled list of store
        fuel names
        :param fuel_name_getter: html as string
        :return:
        fuel_names: lst
        compiled list of fuel names
        """
        fuel_names = []
        for element in fuel_name_getter:
            fuel_name = element.text
            fuel_names.append(fuel_name)
        return fuel_names


if __name__ == '__main__':
    price = PricesNavScraper()
    price.reader_loop()
    final_dataframe = price.scrape_links()
    final_dataframe.to_csv("GasStationData.csv", index=False)
