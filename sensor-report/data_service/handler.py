import os
import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)


class DataHandler:
    NULL_COLUMNS = ['value']
    NOT_NULL_COLUMNS = ['site_id', 'sensor_id', 'timestamp', 'measure']

    def __init__(self, input_path, output_path):

        self.df = None
        self.valid_files = None
        self.output_path = None

        # Check file extension
        if not (output_path.endswith(".csv")):
            raise ValueError(f"The output file is not a CSV: {self.output_path}")
        else:
            self.output_path = output_path

        # Get input files
        if os.path.isfile(input_path):
            files = [input_path]
        else:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Cannot find input directory: {input_path}")

            files = [os.path.join(input_path, x) for x in os.listdir(input_path)]

        # Get files with a .csv file extension only
        self.valid_files = [x for x in files if x.endswith(".csv") and os.path.isfile(x)]

        if len(self.valid_files) == 0:
            raise FileNotFoundError(f"No valid csv files found at: {input_path}")

        if os.path.dirname(self.valid_files[0]) == os.path.dirname(self.output_path):
            raise ValueError("Input and output directories must be different")

    def process_input(self):
        for file in self.valid_files:
            try:
                df_temp = pd.read_csv(file)
                
                LOGGER.info("Read '%s'", file)
                
                self._validate_df(df_temp)

                if self.df is None:
                    self.df = df_temp
                else:
                    self.df = self.df.append(df_temp)

            except pd.errors.ParserError as ex:
                error_msg = "Invalid CSV data: " + str(ex).split(':')[1]
                raise ValueError(error_msg) from ex

    def _validate_df(self, df):

        all_columns = self.NOT_NULL_COLUMNS + self.NULL_COLUMNS
        actual_columns = df.columns.tolist()
        assert actual_columns == all_columns, \
            f'\nExpected columns:\n{", ".join(all_columns)} \n\nActual columns:\n{", ".join(actual_columns)}'

        cols_with_nulls = df.columns[df.isna().any()].tolist()
        cols_with_nulls = [x for x in cols_with_nulls if x not in self.NULL_COLUMNS]

        assert len(cols_with_nulls) == 0, \
            f'The following columns should not have nulls {", ".join(cols_with_nulls)}'

    def create_report(self, amber_threshold: float, serialise: bool = True) -> pd.DataFrame:
        self.df["value"] = pd.to_numeric(self.df["value"])
        self.df["counter"] = 1
        self.df["active"] = np.where(self.df["value"].notna(), 1, 0)

        df_out = self.df.groupby(["site_id", "sensor_id", "measure"], as_index=False).sum()

        # Calculate up-time
        df_out["uptime"] = df_out["active"] / df_out["counter"]
        df_out["RAG"] = df_out["uptime"].apply(lambda x: self.calculate_rag(x, amber_threshold))

        report = df_out[["site_id", "sensor_id", "measure", "uptime", "RAG"]]

        if serialise:
            try:
                path = self.get_safe_save_path(self.output_path)
                report.to_csv(path, index=False)
                LOGGER.info("Wrote '%s'", path)
            except PermissionError:
                LOGGER.error("Previous output report is open, so new one cannot be created")
                raise

        return report

    @staticmethod
    def calculate_rag(value, amber_threshold) -> str:
        if value < amber_threshold:
            return "Red"
        elif value < 1:
            return "Amber"
        else:
            return "Green"

    @staticmethod
    def get_safe_save_path(path: str) -> str:
        directory = os.path.dirname(path)

        os.makedirs(directory, exist_ok=True)

        return path
