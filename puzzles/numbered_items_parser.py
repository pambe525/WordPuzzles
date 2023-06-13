import re


class NumberedItemsParser:
    # Tokens check flag
    NO_CHECKS = 0
    SINGLE_ENTRY = 1
    ORTHO_PAIR = 2

    # Error messages
    ITEM_NOT_NUMBERED = "Item {} is not numbered."
    DUPLICATE_ITEM_NUMBER = "Item {} has duplicate item number {}."
    DUPLICATE_ITEM_TEXT = "Item {} has duplicate text."
    ITEM_HAS_NO_TEXT = "Item {} has no text."
    ITEM_IS_NOT_SINGLE_TOKEN = "Item {} has more than one entry."
    MISSING_CROSS_ENTRY = "Corresponding cross-entry for #{} missing."
    EXTRA_CROSS_ENTRY = "Item {} has no matching cross-entry."
    MISMATCH_IN_CROSS_ENTRY_LENGTH = "Item {} mismatches specified cross-entry length."

    def __init__(self, form_field_text, tokens_check_flag=0):
        self.error = None
        self.items_dict = {}
        self.__validate(form_field_text, tokens_check_flag)

    def cross_check_entries(self, target_dict):
        if self.error: return
        try:
            self.__cross_check_extra_entries(target_dict)
            self.__cross_check_missing_entries(target_dict)
            self.__cross_check_length_of_entries(target_dict)
        except ValueError as err:
            self.error = str(err)

    def __validate(self, form_field_text, tokens_check_flag):
        items = self.__parse_text_into_items(form_field_text)
        for index, item in enumerate(items):
            try:
                item_num, item_text = self.__parse_item_into_tokens(item, index)
                self.__add_item_to_dict(item_num, item_text, index, tokens_check_flag)
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

    def __add_item_to_dict(self, item_num, item_text, index, tokens_check_flag):
        if item_num in self.items_dict:
            raise ValueError(self.DUPLICATE_ITEM_NUMBER.format((index + 1), item_num))
        elif item_text in self.items_dict.values():
            raise ValueError(self.DUPLICATE_ITEM_TEXT.format(index + 1))
        elif item_text == "":
            raise ValueError(self.ITEM_HAS_NO_TEXT.format(index + 1))
        elif tokens_check_flag == self.SINGLE_ENTRY:
            tokens = [token.strip() for token in item_text.split(',') if token.strip()]
            if len(tokens) != 1: raise ValueError(self.ITEM_IS_NOT_SINGLE_TOKEN.format(index + 1))
        self.items_dict[item_num] = item_text

    def __cross_check_missing_entries(self, target_dict):
        for key in target_dict:
            if key not in self.items_dict: raise ValueError(self.MISSING_CROSS_ENTRY.format(key))

    def __cross_check_extra_entries(self, target_dict):
        for key in self.items_dict:
            if key not in target_dict: raise ValueError(self.EXTRA_CROSS_ENTRY.format(key))

    def __cross_check_length_of_entries(self, target_dict):
        for key in self.items_dict:
            length_to_match = self.__extract_from_end_parenthesis(target_dict[key])
            if length_to_match is not None:
                length_text = self.__get_answer_footprint_as_string(self.items_dict[key])
                if length_to_match != length_text: raise ValueError(self.MISMATCH_IN_CROSS_ENTRY_LENGTH.format(key))

    @staticmethod
    def __extract_from_end_parenthesis(text):
        match = re.search(r'\(([0-9, -]+)\)$', text)
        if match: return match.group(1).replace(" ", "")
        return None

    def __get_answer_footprint_as_string(self, text):
        footprint = ''
        words = text.split()
        for idx, word in enumerate(words):
            footprint += self.__get_word_length_as_string(word)
            if idx < len(words) - 1: footprint += ','
        return footprint

    @staticmethod
    def __get_word_length_as_string(word):
        len_text = str(len(word))
        hyphenated_parts = word.split('-')
        if len(hyphenated_parts) > 1:
            len_text = ''
            for idx, part in enumerate(hyphenated_parts):
                len_text += str(len(part))
                if idx < (len(hyphenated_parts) - 1):
                    len_text += '-'
        return len_text
