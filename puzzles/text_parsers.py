import re


class NumberedItemsParser:
    # Tokens check flag
    NO_CHECKS = 0
    SINGLE_ENTRY = 1
    ORTHO_PAIR = 2

    # Error messages
    ITEM_NOT_NUMBERED = "Entry {} is not numbered."
    DUPLICATE_ITEM_NUMBER = "#{} is repeated."
    DUPLICATE_ITEM_TEXT = "#{} has repeated text."
    ITEM_HAS_NO_TEXT = "#{} has no text."
    ITEM_IS_NOT_SINGLE_TOKEN = "#{} must have a single entry."
    MISSING_CROSS_ENTRY = "Corresponding cross-entry for #{} missing."
    EXTRA_CROSS_ENTRY = "#{} has no matching cross-entry."
    MISMATCH_IN_CROSS_ENTRY_LENGTH = "#{} mismatches specified cross-entry length."
    NON_ALPHA_CHARS_IN_TEXT = "#{} has characters other than alphabets & hyphen."
    REPEATED_TEXT_IN_FIELD = "#{} has {} text identical to #{}"

    def __init__(self, form_field_text, tokens_check_flag=0):
        self.error = None
        self.items_dict = {}
        self.__validate_entries(form_field_text, tokens_check_flag)

    def cross_check_entries(self, target_dict):
        if self.error: return
        try:
            self.__cross_check_extra_entries(target_dict)
            self.__cross_check_missing_entries(target_dict)
            self.__cross_check_length_of_entries(target_dict)
        except ValueError as err:
            self.error = str(err)

    def check_non_alpha_chars(self):
        if self.error: return
        for key in self.items_dict:
            if ClueChecker().has_non_alpha_chars(self.items_dict[key]):
                self.error = self.NON_ALPHA_CHARS_IN_TEXT.format(key)
                break

    def __validate_entries(self, form_field_text, tokens_check_flag):
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
            raise ValueError(self.DUPLICATE_ITEM_NUMBER.format(item_num))
        elif item_text in self.items_dict.values():
            raise ValueError(self.DUPLICATE_ITEM_TEXT.format(item_num))
        elif item_text == "":
            raise ValueError(self.ITEM_HAS_NO_TEXT.format(item_num))
        elif tokens_check_flag == self.SINGLE_ENTRY:
            if not ClueChecker().has_single_answer(item_text):
                raise ValueError(self.ITEM_IS_NOT_SINGLE_TOKEN.format(item_num))
        self.items_dict[item_num] = item_text

    def __cross_check_missing_entries(self, target_dict):
        for key in target_dict:
            if key not in self.items_dict: raise ValueError(self.MISSING_CROSS_ENTRY.format(key))

    def __cross_check_extra_entries(self, target_dict):
        for key in self.items_dict:
            if key not in target_dict: raise ValueError(self.EXTRA_CROSS_ENTRY.format(key))

    def __cross_check_length_of_entries(self, target_dict):
        for key in self.items_dict:
            clue_data = {'clue_num': key, 'clue_text': target_dict[key], 'answer': self.items_dict[key]}
            if not ClueChecker().has_matching_answer_lengths(target_dict[key], self.items_dict[key]):
                raise ValueError(self.MISMATCH_IN_CROSS_ENTRY_LENGTH.format(key))


class ClueChecker:

    def get_decorated_clue_text(self, clue_text, answer):
        length_digits_in_clue = self.__get_clue_answer_length(clue_text)
        if length_digits_in_clue is None:
            answer_digits = self.__get_answer_length(answer)
            return clue_text + " (" + answer_digits + ")"
        else:
            return clue_text

    def has_matching_answer_lengths(self, clue_text, answer):
        length_digits_in_clue = self.__get_clue_answer_length(clue_text)
        if length_digits_in_clue is None: return True
        return self.__get_answer_length(answer) == length_digits_in_clue

    @staticmethod
    def has_non_alpha_chars(answer):
        # forbidden_char = re.compile('[0-9@_!#$%^&*()<>?/\|}{~:,]')
        return True if re.search(r'[^a-zA-Z- ,]', answer) is not None else False

    @staticmethod
    def has_single_answer(answer):
        tokens = [token.strip() for token in answer.split(',') if token.strip()]
        return len(tokens) == 1

    def has_ortho_pair_answer(self, answer):
        pass

    @staticmethod
    def __get_clue_answer_length(clue_text):
        match = re.search(r'\(([0-9, -]+)\)$', clue_text)
        if match: return match.group(1).replace(" ", "")
        return None

    def __get_answer_length(self, answer):
        footprint = ''
        words = answer.split()
        for idx, word in enumerate(words):
            footprint += self.__encode_word_length_as_numeric_string(word)
            if idx < len(words) - 1: footprint += ','
        return footprint

    @staticmethod
    def __encode_word_length_as_numeric_string(word):
        numeric_string = str(len(word))
        hyphenated_parts = word.split('-')
        if len(hyphenated_parts) > 1:
            numeric_string = ''
            for idx, part in enumerate(hyphenated_parts):
                numeric_string += str(len(part))
                if idx < (len(hyphenated_parts) - 1):
                    numeric_string += '-'
        return numeric_string
