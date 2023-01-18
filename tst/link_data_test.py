import unittest

import bs4
import pandas as pd
from unittest.mock import patch
from bs4 import BeautifulSoup

import link_data


class TestLinkData(unittest.TestCase):

    def setUp(self) -> None:
        html = """<div class="row">
                    <div class="map-property">
                        <div id="leafletMap" style="width:100%; height: 300px"></div>
                        <br />
                        <div class="text-center">
                            <a href="https://www.google.com/maps/dir/?api=1&destination=42.651318,23.316212&travelmode=driving" class="btn btn-secondary btn-large" target="_blank"><img src="/img/googlemaps-16x16.png" alt="" /> Навигация <sup><i class="fas fa-external-link-alt"></i></sup></a>
                        </div>
                    </div><!-- /.map-property -->
                </div>
                <tbody>
                    <tr itemscope itemtype="http://schema.org/Product">
                        <td style="text-align:right"><img src="/img/fuels/eko-95-ekonomy.png" alt="95EKONOMY" /></td>
                            <td itemprop="name">95EKONOMY</td>
                            <td itemprop="offers" itemscope itemtype="http://schema.org/Offer">
                            <span itemprop="price" content="2.67"> 2,67 </span> лв./л </span>
                            <span itemprop="priceCurrency" content="bgn"></span>
                                <sub class="text-success" ><i class="fas fa-long-arrow-alt-down"></i> -0,01</sub></td>
                                 <td>2,60 лв./л </td>
                                <td>2,60 лв./л </td><td align="right"> <span title="2023-01-16 11:58:41"> <i class="far fa-check-circle"></i> </span></td>
                    </tr>
                </tbody>
"""
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = html
            self.price_scraper = link_data.PricesNavScraper()
            self.mocked_get_text = mocked_get.return_value.text

    def test_get_fuel_prices(self):
        test_list = BeautifulSoup(self.mocked_get_text, "html.parser")
        fuel_price_getter = test_list.find_all("span", itemprop="price", content=True)
        actual_output = self.price_scraper.get_fuel_prices(fuel_price_getter)
        self.assertEqual(["2.67 лв/л.(kw/h)"], actual_output)

    def test_compile_fuel_names(self):
        test_list = BeautifulSoup(self.mocked_get_text, "html.parser")
        fuel_name_getter = test_list.find_all("td", itemprop="name")
        actual_output = self.price_scraper.compile_fuel_names(fuel_name_getter)
        self.assertEqual(['95EKONOMY'], actual_output)

    def test_get_fuel_types_vs_prices(self):
        fuels_and_prices = {'95EKONOMY': "2.67 лв/л.(kw/h)"}
        actual_output = self.price_scraper.get_fuel_types_vs_prices(fuels_and_prices)
        self.assertEqual({'Бензин A100': 'None', 'Бензин A95': '2.67 лв/л.(kw/h)', 'Бензин A95+': 'None',
                          'Бензин A98': 'None', 'Дизел': 'None', 'Дизел премиум': 'None', 'Електричество': 'None',
                          'Метан': 'None',
                          'Пропан Бутан': 'None'}, actual_output)

    def test_get_fuel_types(self):
        with patch('scraper.Scraper.fuel_types_scraping') as mocked_scrape:
            mocked_scrape.return_value = {"d", "a", "kyp"}
            actual_output = self.price_scraper.get_fuel_types()
            self.assertEqual(['a', 'd', 'kyp'], actual_output)

    def test_scrape_links(self):
        # arrange

        # step1 mock get_fuel_types to get the columns of the new df
        with patch('link_data.PricesNavScraper.get_fuel_types') as mocked_fuel_types:
            mocked_fuel_types.return_value = ['Бензин A100', 'Бензин A95', 'Бензин A95+', 'Бензин A98', 'Дизел',
                                              'Дизел премиум', 'Електричество', 'Метан', 'Пропан Бутан']

        # step2 mock the html
        with patch('bs4.BeautifulSoup') as mocked_bs4:
            mocked_bs4.return_value = bs4.BeautifulSoup(self.mocked_get_text, 'html.parser')

        columns_list = ['Бензин A100', 'Бензин A95', 'Бензин A95+', 'Бензин A98', 'Дизел',
                        'Дизел премиум', 'Електричество', 'Метан', 'Пропан Бутан','Navigation links' ]

        final_dict = {'Бензин A100': ['3.04 лв/л.(kw/h)'], 'Бензин A95': ['2.63 лв/л.(kw/h)'], 'Бензин A95+': ['None'],
                      'Бензин A98': ['None'], 'Дизел': ['2.96 лв/л.(kw/h)'],
                      'Дизел премиум': ['3.33 лв/л.(kw/h)'], 'Електричество': ['None'], 'Метан': ['None'],
                      'Пропан Бутан': ['None'],
                      'Navigation links': ['https://www.google.com/maps/dir/?api=1&destination=42.706902,23.468399&travelmode=driving']}
        df_to_concat = pd.DataFrame(final_dict, columns=final_dict.keys())
        df_to_read = pd.read_csv('GasStationData.csv')

        frames = [df_to_read, df_to_concat]
        expected_df = pd.concat(frames, axis=1)
        # act
        self.price_scraper.scrape_links()
        # assert
        self.assertTrue(expected_df.equals(self.price_scraper.data_source_df))
