import re


class NumberedItemsParser:
    items = None
    error = None

    def __init__(self, form_field_text):
        text = form_field_text.strip()
        self.items = [token.strip() for token in form_field_text.split("\n") if token.strip()]
        for index, item in enumerate(self.items):
            if re.match(r'^(\d+)(.*)', item) is None: self.error = "No numbered items found."

