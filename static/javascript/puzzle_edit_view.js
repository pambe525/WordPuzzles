class PuzzleEditView {
    #ID = {
        jqHomeBtn: "#home", jqTitle: '#page-title', jqSaveOkIcon: '#save-ok', jqSaveBtn: '#save',
        jqDeleteBtn: "#delete", jqPublishBtn: '#publish', jqDesc: '#desc', jqSizeLabel: '#size-label',
        jqSizeSelect: '#size', jqRadio1: '#radio-1', jqRadio1Label: "#radio1-label",
        jqRadio2: '#radio-2', jqRadio2Label: '#radio2-label', jqClueForm: '#clue-form',
        jqClueNum: '#clue-num', jqClueWord: '#clue-word', jqClueText: '#clue-text',
        jqClueMsg: '#clue-msg', jqClueUpdateBtn: '#clue-update', jqClueDeleteBtn: "#clue-delete",
        jqPuzzleDiv: '#puzzle'
    };
    #controller = null;

    constructor(controller) {
        this.#controller = controller;
        $(this.#ID.jqSizeLabel).text("Grid Size");
        $(this.#ID.jqRadio1Label).text("Blocks");
        $(this.#ID.jqRadio2Label).text("Clues");
        $(this.#ID.jqSaveOkIcon).prop("hidden", true);
    }

    bindHandlers() {
        $("input[type=radio][name='switch']").change(this.#controller.onSwitchChange);
        $(this.#ID.jqSizeSelect).change(this.#controller.onSizeChange);
        $(this.#ID.jqSaveBtn).click(this.#controller.onSaveClick);
    }

    setTitle() {
        $(this.#ID.jqTitle).text("New Crossword Puzzle");
    }

    disableDelete() {
        $(this.#ID.jqDeleteBtn).prop("disabled", true);
    }

    disablePublish() {
        $(this.#ID.jqPublishBtn).prop("disabled", true);
    }

    setRadio1() {
        $(this.#ID.jqRadio1).prop("checked", true);
    }

    setRadio2() {
        $(this.#ID.jqRadio2).prop("checked", true);
    }

    getRadioChecked() {
        return $("input[name='switch']:checked").val();
    }

    hideClueForm() {
        $(this.#ID.jqClueForm).prop("hidden", true);
    }

    showClueForm() {
        $(this.#ID.jqClueForm).prop("hidden", false);
    }

    setSizeSelector(sizeOptions) {
        for (var key in sizeOptions)
            $(this.#ID.jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
    }

    setSize(size) {
        $(this.#ID.jqSizeSelect).val(size);
    }

    getSize() {
        return parseInt($(this.#ID.jqSizeSelect).val());
    }

    setPuzzle(puzzleObj) {
        $(this.#ID.jqPuzzleDiv).empty();
        $(this.#ID.jqPuzzleDiv).append(puzzleObj);
    }
}