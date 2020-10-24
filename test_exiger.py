import unittest
import exiger
# these test are based a dummy excel file that is included in the project


class TestFileReader(unittest.TestCase):

    def test_read_iso_date(self):
        fr = exiger.FileReader()
        iso_date_df = fr.read_iso_date()
        self.assertEqual((iso_date_df.loc[0, 'iso']), 'USA')

    def test_clean_iso_date(self):
        fr = exiger.FileReader()
        fr.read_iso_date()
        df = fr.clean_iso_date()
        self.assertEqual((df.loc[4, 'iso']), 'CAN')


class TestCovidFetcher(unittest.TestCase):

    def test_create_covid_table(self):
        fr = exiger.FileReader()
        fr.read_iso_date()
        df = fr.clean_iso_date()
        df = fr.make_combinations()
        cf = exiger.CovidFetcher()

        result_df = cf.create_covid_table(df)
        self.assertEqual(result_df.loc[0, 'deaths'], 222176.0)

    def test_write_table(self):

        fr = exiger.FileReader()
        fr.read_iso_date()
        df = fr.clean_iso_date()
        cf = exiger.CovidFetcher()
        cf.create_covid_table(df)
        self.assertIsNotNone(cf.write_table())


if __name__ == '__main__':
    unittest.main()
