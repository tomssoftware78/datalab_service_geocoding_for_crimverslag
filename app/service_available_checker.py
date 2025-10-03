import requests
from requests.exceptions import RequestException, ConnectionError, Timeout
import logging
import os

class ServiceAvailableChecker:

    @property
    def logger(self):
        # Create a logger specific to this class
        if not hasattr(self, '_logger'):
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
    
    def __init__(self):
        self.services_to_check = {
            "Geocoding Service": os.getenv("GEO_CHECK_URL")
        }   

    def check_all_services(self):
        all_ok = True
        for name, url in self.services_to_check.items():
            ok = self.check_service(name, url)
        
            if not ok:
                all_ok = False

        if not all_ok:
            self.logger.error("Not all services are available, application not started.")
            exit(1)

    def check_service(self, name, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                self.logger.debug("%s is available (STATUS %s)", name, response.status_code)
                return True
            else:
                self.logger.debug("%s is not available (STATUS %s)", name, response.status_code)
                return False
        except (ConnectionError, Timeout):
            self.logger.error("%s is not available", name, exc_info=True)
            return False
        except RequestException as e:
            self.logger.error("%s is not available", name, exc_info=True)
            return False
