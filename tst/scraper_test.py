import unittest
from unittest.mock import patch
import scraper


class TestScraper(unittest.TestCase):

    def setUp(self) -> None:
        html = """
        <tbody><tr>
           <td><a href="/gasstation/id/257?lang=bg"><img src="/img/logos/eko-gr-small.png" alt="Eko" />Eko 1164 София – Долни Богров</a></td><td>с. Долни Богров</td><td>
           <img src="/img/fuels/default/gasoline.png" alt="Бензин А95" title="Бензин A95" />
           <img src="/img/fuels/default/diesel.png" alt="Дизелово Гориво" title="Дизел" />
           <img src="/img/fuels/default/gasoline98plus.png" alt="Бензин А98 с добавки" title="Бензин A100" />
           <img src="/img/fuels/default/dieselplus.png" alt="Дизелово Гориво с добавки" title="Дизел премиум" />
           </td><td><i class='fas fa-user' title='Актуални цени предоставени от посетител на Fuelo.net'></i></td></tr>
                       """
        with patch('requests.get') as mocked_get:
            mocked_get.return_value.ok = True
            mocked_get.return_value.text = html
            self.scraper = scraper.Scraper()

    def test_table_scraping(self):
        actual_output = self.scraper.table_scraping()
        self.assertEqual([['Eko 1164 София – Долни Богров', 'с. Долни Богров',
                           'https://bg.fuelo.net/gasstation/id/257?lang=bg']], actual_output)

    def test_fuel_types_scraping(self):
        actual_output = self.scraper.fuel_types_scraping()
        self.assertEqual({'Бензин A95', 'Дизел', 'Бензин A100', 'Дизел премиум'}, actual_output)

    @property
    def mock_csv_data(self):
        return [
            'Gas Station,Address,Link\n',
            'Eko 1164 София – Долни Богров,с. Долни Богров,https://bg.fuelo.net/gasstation/id/257?lang=bg\n'
        ]

    def test_dataframe_conversion(self):
        expected_output = self.mock_csv_data
        self.scraper.dataframe_conversion()
        actual_result = open('GasStationData.csv', 'r', encoding='UTF-8')
        self.assertListEqual(list1=expected_output, list2=list(actual_result))
        actual_result.close()


if __name__ == "__main__":
    tst = TestScraper()
