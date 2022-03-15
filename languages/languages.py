import os
import yaml


class Lang:
    def __init__(self, locale):
        self.locales = self.get_available_locales()
        if locale not in self.locales:
            locale = "en"
            print(f"{locale} is not a valid locale , using en instead")
        self.locale = locale
        self.text = self.load_text()
        self.all_locales = self.load_locales()

    @staticmethod
    def get_available_locales() -> list:
        return sorted([lang.split(".")[0] for lang in os.listdir("languages")
                       if not (lang.endswith("locales.yml") or lang.endswith("__pycache__")
                               or lang.endswith("languages.py"))])

    def load_text(self) -> dict:
        text = {}
        for locale in self.locales:
            with open(f"languages/{locale}.yml", "r", encoding="utf-8") as yaml_file:
                text.update({locale: yaml.load(yaml_file, Loader=yaml.FullLoader)})
        return text

    @staticmethod
    def load_locales():
        with open(f"languages/locales.yml", "r", encoding="utf-8") as yaml_file:
            return yaml.load(yaml_file, Loader=yaml.FullLoader)

    def get(self, text):
        try:
            return self.text["custom"][text]
        except KeyError:
            try:
                return self.text[self.locale][text]
            except KeyError:
                try:
                    return self.text["en"][text]
                except KeyError:
                    return text
