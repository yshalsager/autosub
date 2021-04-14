#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Defines WIT AI API used by autosub.
"""

# Import built-in modules
import json
import gettext
import os

# Import third-party modules
import requests

# Any changes to the path and your own modules
from autosub import constants

API_WIT_AI_TEXT = gettext.translation(domain=__name__,
                                      localedir=constants.LOCALE_PATH,
                                      languages=[constants.CURRENT_LOCALE],
                                      fallback=True)

_ = API_WIT_AI_TEXT.gettext


def get_wit_ai_transcript(result_dict):
    """
    Function for getting transcript from WIT AI Speech-to-Text json format string result.
    """
    return result_dict['_text'] if '_text' in result_dict else result_dict['text']


class WITAiAPI:  # pylint: disable=too-few-public-methods
    """
    Class for performing Speech-to-Text using Baidu ASR API.
    """

    def __init__(self,
                 api_url,
                 api_key,
                 retries=3,
                 is_keep=False,
                 is_full_result=False):
        # pylint: disable=too-many-arguments
        self.retries = retries
        self.api_url = api_url
        self.api_key = api_key
        self.is_keep = is_keep
        self.is_full_result = is_full_result
        self.headers = {
            'authorization': f'Bearer {self.api_key}',
            'accept': 'application/vnd.wit.20200513+json',
            'content-type': 'audio/raw;encoding=signed-integer;bits=16;rate=8000;endian=little',
        }

    def __call__(self, filename):
        try:  # pylint: disable=too-many-nested-blocks
            with open(filename, mode='rb') as audio_file:
                audio_data = audio_file.read()
            if not self.is_keep:
                os.remove(filename)
            for _ in range(self.retries):
                try:
                    requests_result = requests.post(self.api_url, data=audio_data, headers=self.headers)
                except requests.exceptions.ConnectionError:
                    continue
                requests_result_json = requests_result.content.decode("utf-8")
                try:
                    result_dict = json.loads(requests_result_json)
                except ValueError:
                    # no result
                    continue

                if not self.is_full_result:
                    return get_wit_ai_transcript(result_dict)
                return result_dict

        except KeyboardInterrupt:
            return None

        return None
