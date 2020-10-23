import os
import sys
import warnings
import configparser
import datetime as dt
import json
import logging
import re
import pandas as pd
import requests


logger = logging.getLogger(__name__) 
class FileReader():

    def __init__(self, config_file_path=None):

        self.DEFAULT_CONFIG_FILE_NAME = 'settings.conf'
        self.main_path = sys.path[0]
        self.config = configparser.ConfigParser()
        self.desired_columns = set(['date', 'iso'])
        self.iso_date_df = pd.DataFrame(columns=self.desired_columns)

        if not config_file_path:
            self.__set_config_file_to_default()
            logger.warning("Using default config file.")
        else:
            self.config_file_path = config_file_path

    def __set_config_file_to_default(self):
        """ 
        Sets config file path to the default value
        """

        self.config_file_path = os.path.join(
            self.main_path, self.DEFAULT_CONFIG_FILE_NAME)

    def __set_excel_file_path(self):
        """
         Exctracts and set the excel file path from the config file.
        """

        try:
            self.config.read(self.config_file_path)
            self.excel_file_path = self.config['path'].get('excel_path')
        except Exception as e:
            logger.warning(
                "Cannot use the provided config file. make sure the path is correct " + str(e))
            self.__set_config_file_to_default()
        finally:
            self.config.read(self.config_file_path)
            self.excel_file_path = self.config['path'].get('excel_path')

    def read_iso_date(self):
        """
        Extracts and returns the iso and date columns from the passed excel_file_path
        By default read the file indicated in the config file 
        """

        self.__set_excel_file_path()
        try:
            self.dfs = pd.read_excel(self.excel_file_path, sheet_name=None)
        except Exception as error:
            logger.warning("Error in reading the excel file" + str(error))
            return self.iso_date_df
        # to handle multiple sheets
        for df in self.dfs.values():
            if self.desired_columns.issubset(set(df.columns)):
                self.iso_date_df = pd.concat(
                    (self.iso_date_df, df[list(self.desired_columns)]))
        self.iso_date_df.reset_index(inplace=True, drop=True)

        return self.iso_date_df

    def clean_iso_date(self):
        """
        Filters out invalid iso codes. Also unifies date times formats and igonre invalid dates
        """

        valid_iso = self.config['valid_iso_codes'].get('iso_list')
        valid_iso = re.findall("\w+", valid_iso)
        self.iso_date_df = self.iso_date_df[self.iso_date_df['iso'].isin(
            valid_iso)]
        self.iso_date_df['date'] = pd.to_datetime(
            self.iso_date_df['date'], errors='coerce')
        if self.iso_date_df['date'].isnull().any():
            logger.warning("Cannot read some of the dates. Ignoring them")

        self.iso_date_df = self.iso_date_df[~self.iso_date_df['date'].isnull()]
        self.iso_date_df['date'] = self.iso_date_df['date'].dt.strftime(
            '%Y-%m-%d')
        self.iso_date_df.reset_index(inplace=True, drop=True)

        return self.iso_date_df


class CovidFetcher():

    def __generate_get_request(self):
        """
        Creates get requests based on given iso and date
        """

        base_req = 'https://covid-api.com/api/reports?date='
        self.iso_date_df['requests'] = (
            base_req+self.iso_date_df['date'] + '&iso='+self.iso_date_df['iso'])

    def create_covid_table(self, iso_date_df, cumulative=True):
        """
        Gets a dataframe with a column of requests, call the API and return a dataset
        """

        self.iso_date_df = iso_date_df
        self.__generate_get_request()

        self.results_df = self.iso_date_df.copy()

        for i in range(len(self.iso_date_df)):
            logger.info('trying ' + str(self.iso_date_df.loc[i, 'requests']))
            try:
                covid_json = requests.get(
                    self.iso_date_df.loc[i, 'requests']).json()
            except requests.exceptions.RequestException as e:
                logger.warning(
                    "Error in receiving data from the API " + str(e))
                return None

            if cumulative:
                self.results_df.loc[i, 'deaths'] = sum(
                    [item['deaths'] for item in covid_json['data']])
                self.results_df.loc[i, 'confirmed'] = sum(
                    [item['confirmed'] for item in covid_json['data']])
                self.results_df.loc[i, 'recovered'] = sum(
                    [item['recovered'] for item in covid_json['data']])
            else:
                self.results_df.loc[i, 'deaths'] = sum(
                    [item['deaths_diff'] for item in covid_json['data']])
                self.results_df.loc[i, 'confirmed'] = sum(
                    [item['confirmed_diff'] for item in covid_json['data']])
                self.results_df.loc[i, 'recovered'] = sum(
                    [item['recovered_diff'] for item in covid_json['data']])

        self.results_df.drop(columns=['requests'], inplace=True)

        return self.results_df

    def write_table(self, file_name=None):
        """
        Stores the fetch data on disk
        """

        if not file_name:
            self.file_name = dt.datetime.now().strftime("%Y%m%d-%H%M%S") + '.xlsx'
        else:
            self.file_name = file_name

        try:
            self.results_df.to_excel(self.file_name, sheet_name="Covid-Stats")
            return self.file_name
        except Exception as e:
            logger.warning("Error in storing excel file on disk")
            return e


if __name__ == "__main__":

    config_file_name = sys.argv[1] if len(sys.argv) > 1 else None
    output_file_name = sys.argv[2] if len(sys.argv) > 2 else None

    fr = FileReader(config_file_name)
    iso_date_df = fr.read_iso_date()
    if iso_date_df.empty:
        print('The dataframe returned from the excel file is empty. Check the log for more info.')
    else:
        cleaned_iso_date_df = fr.clean_iso_date()
        cov = CovidFetcher()
        cov.create_covid_table(cleaned_iso_date_df)
        cov.write_table(output_file_name)
