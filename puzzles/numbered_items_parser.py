import re


class NumberedItemsParser:
    # Error messages
    ITEM_NOT_NUMBERED = "Item {} is not numbered."
    DUPLICATE_ITEM_NUMBER = "Item {} has duplicate item number {}."
    DUPLICATE_ITEM_TEXT = "Item {} has duplicate text."
    ITEM_HAS_NO_TEXT = "Item {} has no text."

    def __init__(self, form_field_text):
        self.error = None
        self.items_dict = {}
        self.__validate(form_field_text)

    def __validate(self, form_field_text):
        items = self.__parse_text_into_items(form_field_text)
        for index, item in enumerate(items):
            try:
                item_num, item_text = self.__parse_item_into_tokens(item, index)
                self.__add_item_to_dict(item_num, item_text, index)
            except ValueError as err:
                self.error = str(err)
                self.items_dict = {}
                break

    @staticmethod
    def __parse_text_into_items(form_field_text):
        text = form_field_text.strip()
        return [token.strip() for token in text.split("\n") if token.strip()]

    def __parse_item_into_tokens(self, item, index):
        match = re.match(r'^(\d+\.*)(.*)', item)
        if match is None: raise ValueError(self.ITEM_NOT_NUMBERED.format(index + 1))
        item_num = int(match.group(1).rstrip('.'))
        item_text = match.group(2).strip()
        return item_num, item_text

    def __add_item_to_dict(self, item_num, item_text, index):
        if item_num in self.items_dict:
            raise ValueError(self.DUPLICATE_ITEM_NUMBER.format((index + 1), item_num))
        elif item_text in self.items_dict.values():
            raise ValueError(self.DUPLICATE_ITEM_TEXT.format(index + 1))
        elif item_text == "":
            raise ValueError(self.ITEM_HAS_NO_TEXT.format(index + 1))
        self.items_dict[item_num] = item_text
