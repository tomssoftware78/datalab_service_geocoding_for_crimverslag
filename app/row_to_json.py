import pandas as pd
import json

import logging

class DfRowToAddressJsonProducer:

    @property
    def logger(self):
        # Create a logger specific to this class
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    # Keywords
    def create_json(self, row: pd.Series) -> dict:
        self.logger.debug("Postcode: %s", row['Postcode'])
        self.logger.debug("Gemeente: %s", row['Gemeente'])
        self.logger.debug("Straat: %s", row['Straat'])
        self.logger.debug("Nummer: %s", row['Nummer'])
        self.logger.debug("Land: %s", row['Land'])
        self.logger.debug("")
        self.logger.debug("")
        municipality = row['Gemeente']
        if pd.isna(municipality) or not str(municipality).strip():
            return {}
        
        payload = {
            "municipality": str(municipality),
            "postalcode": None if pd.isna(row.get("Postcode")) else str(row.get("Postcode")),
            "street": None if pd.isna(row.get("Straat")) else str(row.get("Straat")),
            "nr": None if pd.isna(row.get("Nummer")) else str(row.get("Nummer")),
            "country": None if pd.isna(row.get("Land")) else str(row.get("Land"))
        }

        self.logger.debug("Payload: %s", payload)
        self.logger.debug("")
        self.logger.debug("")

        return payload

