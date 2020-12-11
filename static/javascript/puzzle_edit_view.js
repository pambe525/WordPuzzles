var PuzzleEditView = (function () {
    var jqHomeBtn = "#home", jqTitle = '#page-title', jqSaveOkIcon = '#save-ok', jqSaveBtn = '#save',
        jqDeleteBtn = "#delete", jqPublishBtn = '#publish', jqDesc = '#desc', jqSizeLabel = '#size-label',
        jqSizeSelect = '#size', jqRadio1 = '#radio-1', jqRadio1Label = "#radio1-label",
        jqRadio2 = '#radio-2', jqRadio2Label = '#radio2-label', jqClueForm = '#clue-form',
        jqClueNum = '#clue-num', jqClueWord = '#clue-word', jqClueText = '#clue-text',
        jqClueMsg = '#clue-msg', jqClueUpdateBtn = '#clue-update', jqClueDeleteBtn = "#clue-delete",
        jqPuzzleDiv = '#puzzle';

    return {
        setTitle: function () {
            $(jqTitle).text("New Crossword Puzzle");
        },
        hideSaveOkIcon: function () {
            $(jqSaveOkIcon).prop("hidden", true);
        },
        disableDelete: function () {
            $(jqDeleteBtn).prop("disabled", true);
        },
        disablePublish: function () {
            $(jqPublishBtn).prop("disabled", true);
        },
        setSizeLabel: function (text) {
            $(jqSizeLabel).text(text);
        },
        setRadioSwitch: function (radio1Label, radio2Label, changeHandler) {
            $(jqRadio1Label).text(radio1Label);
            $(jqRadio2Label).text(radio2Label);
            $("input[type=radio][name='switch']").change(changeHandler);
        },
        setRadio1: function () {
            $(jqRadio1).prop("checked", true);
        },
        setRadio2: function () {
            $(jqRadio2).prop("checked", true);
        },
        getRadioChecked: function () {
            return $("input[name='switch']:checked").val();
        },
        hideClueForm: function () {
            $(jqClueForm).prop("hidden", true);
        },
        showClueForm: function () {
            $(jqClueForm).prop("hidden", false);
        },
        setSizeSelector: function (sizeOptions, changeHandler) {
            for (var key in sizeOptions)
                $(jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
            $(jqSizeSelect).change(changeHandler);
        },
        setSize: function (size) {
            $(jqSizeSelect).val(size);
        },
        getSize: function () {
            return parseInt($(jqSizeSelect).val());
        },
        setPuzzle: function (puzzleObj) {
            $(jqPuzzleDiv).empty();
            $(jqPuzzleDiv).append(puzzleObj);
        },

    }
}());