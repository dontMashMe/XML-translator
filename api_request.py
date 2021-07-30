import requests
import json


#    params = {"q": line, "langpair": "{0}|{1}".format("es", "en")}
#     segments = request_from_api(url, params)
from typing import List


class APIInterface:
    def __init__(self, source_lang: str, dest_lang_lid: str):
        self.source_lang = source_lang
        self.dest_lang_lid = dest_lang_lid
        self.endpoint = "http://api.mymemory.translated.net/get"

    def request_from_api(self, params: dict):
        response_object = requests.post(self.endpoint, params)
        response_JSON = json.loads(response_object.text)
        return response_JSON

    def translate_list(self, values: list) -> dict:
        string_to_translate = ""
        translations_dict = {}
        eng_translations = []
        dest_lang_translations = []
        for value_group in values:
            for value in value_group:
                if value.text is not None:
                    # concatenate strings with a delimiter NOT used anywhere inside bskernel.xmls
                    string_to_translate += value.text + "×"
                    eng_translations.append(value.text)
        # print(translation_string.split("¨"))
        # print(len(translation_string))
        translated_string = self.translate(string_to_translate)
        # matching the lists in this loop does not work for some reason, don't know why
        explode_list = translated_string.split("×")
        for line in explode_list:
            dest_lang_translations.append(line)

        # since in the first loop of the method we append values to string and push them to list in the same iteration
        # we know they are indexed the same, therefore we can match them up
        for idx, value in enumerate(eng_translations):
            try:
                translations_dict[eng_translations[idx]] = dest_lang_translations[idx]
            except IndexError:
                translations_dict[eng_translations[idx]] = eng_translations[idx]

        return translations_dict

    def translate(self, text):
        params = {"q": text, "langpair": "{0}|{1}".format(self.source_lang.upper(), self.dest_lang_lid.upper()),
                  "de": "marijan.bebek@mail.com"}
        segments = self.request_from_api(params=params)
        response_data = segments.get('responseData')
        return response_data.get('translatedText')
