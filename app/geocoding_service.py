import requests
import logging
import os
from row_to_json import DfRowToAddressJsonProducer
class GeocodingService:
    GEO_URL = os.getenv('GEO_URL')
    row_to_json: DfRowToAddressJsonProducer

    @property
    def logger(self):
        # Create a logger specific to this class
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def __init__(self):
        self.row_to_json = DfRowToAddressJsonProducer()
        
    def get_x_y_from_geocoding_service(self, row):
        payload = self.row_to_json.create_json(row=row)

        if payload:
            result = self.geocode_address(address=payload)
            return {
                "lon": str(result["lon"]),
                "lat": str(result["lat"]),
                "score": str(result["score"])
            }
        else:
            return {
                "lon": "",
                "lat": "",
                "score": ""
            }

    def geocode_address(self, address: dict):
        # Sending the POST request
        self.logger.debug("Request: %s", address)
        response = requests.post(self.GEO_URL, json=address)

        result = dict()

        if response:
            self.logger.info("Response: %s", response)

            if response.status_code == 200:
                response_json = response.json()

                try:
                    self.logger.debug(response_json["candidates"][0]["score"])
                    self.logger.debug(response_json["candidates"][0]["x"])
                    self.logger.debug(response_json["candidates"][0]["y"])

                    result["lon"] = response_json["candidates"][0]["x"]
                    result["lat"] = response_json["candidates"][0]["y"]
                    result["score"] = response_json["candidates"][0]["score"]
                except Exception:
                    self.logger.error("Geocoding response incomplete: %s", response_json)
                    result["lon"] = ''
                    result["lat"] = ''
                    result["score"] = ''
            else:
                result["lon"] = ''
                result["lat"] = ''
                result["score"] = ''

            self.logger.debug("Response received: %s", response.json())
        else:
            result["lon"] = ''
            result["lat"] = ''
            result["score"] = ''

        self.logger.info("Result: %s", result)

        return result
