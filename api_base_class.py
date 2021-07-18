import argparse
import base64
import logging
import requests
import sys
import time
import uuid

from beautifultable import BeautifulTable
from pprint import pformat
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from requests import Session
from typing import *
from unittest import TestCase

# imports from user defined utils
from endpoints import *

scriptName = sys.argv[0].split("\\")[-1][0:-3]  # the script without the .py extension
dateTimeStamp = time.strftime("%Y%m%d%H%M%S")  # in the format YYYYMMDDHHMMSS
logFileName = scriptName + "_" + dateTimeStamp + ".log"

file_handler = logging.FileHandler(filename=logFileName, mode="w", encoding="utf-8")
stdout_handler = logging.StreamHandler(sys.stdout)
log_handlers_list = [file_handler, stdout_handler]


log = None


class ApiBaseClass(TestCase):

    """
    Common base class for REST API testing
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Initialize class variables
        """
        cls.mismatched_http_resp = "Mismatched http reponse"
        cls.exception_msg = "Exception occurred during script execution"
        cls.pretty = "*" * 100
        cls.pretty_formatter = f"\n{cls.pretty}" * 3
        cls.start_tc = "START TC: %s"
        cls.end_tc = "END TC: %s"
        cls.report = BeautifulTable(maxwidth=220)
        cls.args = cls.arguments(cls)
        logging.basicConfig(
            level=getattr(logging, cls.args.log_level.upper()),
            format="%(asctime)s::%(filename)s::line-no %(lineno)d::%(levelname)s - %(message)s",
            handlers=log_handlers_list,
        )
        cls.log = logging.getLogger(__name__)
        global log
        log = cls.log

    def arguments(self) -> argparse.Namespace:
        """
        Initialize default list of arguments from command-line
        """
        arg_parser = argparse.ArgumentParser()
        arg_parser.add_argument(
            "--base-url",
            type=str,
            default=Defaults.BASE_URL,
            help="Microservice cluster URL under test",
        )
        arg_parser.add_argument(
            "--usr", type=str, default=Defaults.api_key, help="login username"
        )
        arg_parser.add_argument(
            "--pwd", type=str, default=Defaults.api_secret, help="login password"
        )
        arg_parser.add_argument(
            "--log_level",
            type=str,
            default=Defaults.log_level,
            help="set logging level",
        )
        return arg_parser.parse_args()

    def enc_credentials(self, usr: str, pwd: str) -> str:
        """
        Encode user credentials with base64 mechanism
        usr: username in string format
        pwd: password in string format
        """
        credentials = f"{usr}:{pwd}".encode("ascii")
        log.debug("Encode user credentials with base64")
        b64_enc = base64.b64encode(credentials)
        return b64_enc.decode("utf-8")

    def default_login(
        self,
        usr: Optional[str] = None,
        pwd: Optional[str] = None,
        **kwargs: dict,
    ) -> Session:
        """login and return user session
        usr: username to login
        pwd: password
        url: cluster's url
        first_login: set to True if user logins for first time else False

        kwargs: set retry options in dict format key=value
        ex:
        retries=5 -> numbers of times to re-establish a session connection incase of a failure,
        backoff_factor=0.3 -> exponential-factor to apply between each retry
        status_forcelist=[500, 502, 504] -> raise http errors if occured during session object creation,
        session: create a new session object if no session object is passed,
        """
        # self.args = self.arguments()
        login_headers = Defaults.DEF_HEADERS
        # login_headers["Authorization"] = "Basic " + self.enc_credentials(usr, pwd)
        login_headers["Authorization"] = f"Bearer {Defaults.jwt_token}"
        self.session = self.requests_retry_session(**kwargs)
        # s.headers.update({"Content-Type": "application/json", "Authorization": f"Bearer {Defaults.jwt_token}"})
        self.session.headers.update(login_headers)
        setattr(self.session, "usr", usr)
        setattr(self.session, "pwd", pwd)

    def requests_retry_session(
        self,
        retries: int = 5,
        backoff_factor: float = 0.3,
        status_forcelist=[500, 502, 504],
        session: Optional[Session] = None,
    ) -> Session:
        """create and return requests module session object
        retries=5 -> numbers of times to re-establish a session connection incase of a failure,
        backoff_factor=0.3 -> exponential-factor to apply between each retry to know more refer to https://www.peterbe.com/plog/best-practice-with-retries-with-requests,
        status_forcelist=[500, 502, 504] -> raise http errors if occured during session object creation,
        session: create a new session object if no session object is passed,
        """
        session = session or Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
            method_whitelist=frozenset(["GET", "POST", "PUT", "DELETE", "PATCH"]),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        return session

    def resp_eval(
        self,
        resp: requests.models.Response,
        files: bool = False,
        supress_error: bool = True,
    ) -> None:
        """
        Evaluate and raise exception with given response
        params:
            resp: requests.models.Response
            files: set to True if request response contain file upload information
            supress_error: set to True always, supresses error and warning log statements
        """
        url = pformat(resp.request.url)
        headers = pformat(resp.request.headers)
        rmethod = resp.request.method
        try:
            log.debug(f"Request method: {rmethod}, \nURL: {url}")
            resp.raise_for_status()
        except requests.exceptions.HTTPError as httpErr:
            if not supress_error:
                log.warning(f"Request method: {rmethod}, \nURL: {url}")
                log.warning(f"Request headers:\n{headers}")
                if "Content-Type" in resp.request.headers:
                    if (
                        not "multipart/form-data"
                        in resp.request.headers["Content-Type"]
                    ):
                        log.warning(f"Request body:\n{resp.request.body}")
                log.warning(f"Http Error:\n{httpErr}\n{resp.text}")
        except requests.exceptions.ConnectionError as errc:
            log.error(f"Error Connecting:\n{errc}")
        except requests.exceptions.Timeout as errt:
            log.error(f"Timeout Error:\n{errt}")
        except requests.exceptions.RequestException as err:
            log.error(RuntimeError(f"Exception occurred:\n{err}"))

    def validate_without_assert(
        self, resp: requests.models.Response, fail_msg: str, **kwargs: dict
    ) -> Tuple:
        """
        Validate request module response without asserting and return tuple
        params:
            resp: requests.models.Response
            fail_msg: failure message to be logged
            kwargs: key=value dict type variable example
            client_fail: set to True if http client error is expected
            server_fail: set to True if http server error is expected
            rjson: set to True by default if dict output is expected to be returned
        """
        client_fail = kwargs.get("client_fail", False)
        server_fail = kwargs.get("server_fail", False)
        rjson = kwargs.get("rjson", True)
        supress_output = kwargs.get("supress_output", False)
        eval_http = False
        if client_fail:
            if not resp.status_code in HTTP_CODES.CLIENT_ERRORS:
                self.resp_eval(resp, supress_error=supress_output)
                log.error(fail_msg)
            else:
                self.resp_eval(resp)
                eval_http = True
        elif server_fail:
            if not resp.status_code in HTTP_CODES.SERVER_ERRORS:
                self.resp_eval(resp, supress_error=supress_output)
                log.error(fail_msg)
            else:
                self.resp_eval(resp)
                eval_http = True
        else:
            if not resp.status_code in HTTP_CODES.SUCCESS:
                self.resp_eval(resp, supress_error=supress_output)
                log.error(fail_msg)
            else:
                self.resp_eval(resp)
                eval_http = True
        if resp.request.headers["Content-Type"] != "application/octet-stream":
            if rjson:
                response = resp.json()
            else:
                response = resp.text
            if not supress_output:
                log.info(pformat(response))
        else:
            response = {}
        return eval_http, response

    def random_uuid_string(self) -> str:
        """
        Return random uuid string of length: 8
        """
        return str(uuid.uuid4())[:8]

    def tearDown(self) -> None:
        """
        Close session if it exists
        Print the logger filename where the results are stored
        """
        if getattr(self, "session"):
            self.session.close()
        log.info(f"Test Results saved to: {logFileName}")
