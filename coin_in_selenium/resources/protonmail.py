import os
from json import dumps, loads
import shutil
from platform import freedesktop_os_release, system

from proton.api import Session

from coin_in_selenium import logging


class Protonmail:
    def __init__(
        self,
        protonmail_username: str,
        protonmail_password: str,
        session_file: str = "cache/proton.session",
    ) -> None:
        self.username: str = protonmail_username
        self.password: str = protonmail_password
        self.user_agent: str = self._gen_user_agent()
        self.session_file: str = session_file
        self.proton_session: Session = self._get_session()

    def _gen_user_agent(self) -> str:
        _user_agent = ""
        _user_agent += f"{system()};"
        for key in freedesktop_os_release().items():
            if key[0] in ["ID", "VERSION_ID"]:
                _user_agent += key[1]
        return _user_agent

    def _get_session(self) -> Session:
        if os.path.isfile(self.session_file):
            try:
                with open(self.session_file, "r", encoding="utf-8") as _input:
                    session = loads(_input.read())
                    if len(session) == 0:

                        logging.debug("Empty session file found")
                        raise Exception
                    logging.info("Found session file")
                    proton_session = Session.load(
                        dump=session,
                        tls_pinning=False,
                        log_dir_path=os.getcwd() + "/logs",
                        cache_dir_path=os.getcwd() + "/cache",
                    )
                    proton_session.enable_alternative_routing = False
            except Exception as exception:
                logging.error(exception)
                with open(self.session_file, "w", encoding="utf-8") as _output:
                    logging.debug("Empty session file found, login into Protonmail")
                    proton_session = Session(
                        api_url="https://account.proton.me/api",
                        appversion="web-account@5.0.22.1",
                        user_agent=self.user_agent,
                        tls_pinning=False,
                        log_dir_path=os.getcwd() + "/logs",
                        cache_dir_path=os.getcwd() + "/cache",
                        timeout=30,
                    )
                    proton_session.enable_alternative_routing = False
                    proton_session.authenticate(self.username, self.password)
                    _output.write(dumps(proton_session.dump(), indent=4))
        else:
            with open(self.session_file, "w", encoding="utf-8") as _output:
                logging.debug("Session file not found, login into Protonmail")
                proton_session = Session(
                    api_url="https://account.proton.me/api",
                    appversion="web-account@5.0.22.1",
                    user_agent=self.user_agent,
                    tls_pinning=False,
                    log_dir_path=os.getcwd() + "/logs",
                    cache_dir_path=os.getcwd() + "/cache",
                    timeout=30,
                )
                proton_session.enable_alternative_routing = False
                proton_session.authenticate(self.username, self.password)
                _output.write(dumps(proton_session.dump(), indent=4))



        return proton_session

    def get_subject_by_sender(
        self,
        sender: str,
        params: dict[str, int | str] = None,
    ) -> str | None:
        if params is None:
            params = {
                "Page": 0,
                "PageSize": 5,
                "Limit": 5,
                "LabelID": 0,
                "Sort": "Time",
                "Desc": 1,
                "Unread": 1,
            }
        self.proton_session._Session__api_url = 'https://mail.proton.me/api'
        emails_recieved = self.proton_session.api_request(
            "/mail/v4/conversations",
            params=params,
        )

        for email in emails_recieved["Conversations"]:
            if (email["Senders"][0]["Address"]) == sender:
                logging.debug(self.mark_as_read(email["ID"]))
                return email["Subject"]
        return None

    def mark_as_read(self, _id: str | list[str]):
        if isinstance(_id, str):
            data = {"IDs": [_id]}
            return self.proton_session.api_request(
                endpoint="/mail/v4/conversations/read", jsondata=data, method="PUT"
            )
        if isinstance(_id, list):
            data = {"IDs": _id}
            return self.proton_session.api_request(
                endpoint="/mail/v4/conversations/read", jsondata=data, method="PUT"
            )

    # def clean_up():


if __name__ == "__main__":
    from os import getenv

    print(
        Protonmail(
            getenv("PROTON_USERNAME"), getenv("PROTON_PASSWORD")
        ).get_subject_by_sender("noreply@alertsmailer.zerodha.net")
    )
