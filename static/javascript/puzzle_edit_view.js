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

    initialize() {
        $(this.#ID.jqTitle).text("New Crossword Puzzle");
        this.disableDelete();
        this.disablePublish();
        this.hideClueForm();
        this.bindHandlers();
    }

    bindHandlers() {
        $("input[type=radio][name='switch']").change(this.#controller.onSwitchChange);
        $(this.#ID.jqSizeSelect).change(this.#controller.onSizeChange);
        $(this.#ID.jqSaveBtn).click(this.#controller.onSaveClick);
        $(this.#ID.jqDeleteBtn).click(this.#controller.onDeleteClick);
        $(window).on('beforeunload', this.#controller.onBeforeUnload);
    }

    disableDelete(disable=true) {
        (disable) ? $(this.#ID.jqDeleteBtn).prop("disabled", true) : $(this.#ID.jqDeleteBtn).prop("disabled", false);
    }

    disablePublish(disable=true) {
        (disable) ? $(this.#ID.jqPublishBtn).prop("disabled", true) : $(this.#ID.jqPublishBtn).prop("disabled", false);
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

    hideClueForm(hide=true) {
        (hide) ? $(this.#ID.jqClueForm).hide() : $(this.#ID.jqClueForm).show();
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

    getDesc() {
        return $(this.#ID.jqDesc).text();
    }

    showSaveOKIcon() {
        $(this.#ID.jqSaveOkIcon).show(0, this.hideSaveOKIcon);
    }

    hideSaveOKIcon = () => {
        $(this.#ID.jqSaveOkIcon).fadeOut(3000);
    }
}