class PuzzleEditView {
    ID = {
        jqHomeBtn: "#home", jqTitle: '#page-title', jqSaveOkIcon: '#save-ok', jqSaveBtn: '#save',
        jqDeleteBtn: "#delete", jqPublishBtn: '#publish', jqDesc: '#desc', jqSizeLabel: '#size-label',
        jqSizeSelect: '#size', jqRadio1: '#radio-1', jqRadio1Label: "#radio1-label",
        jqRadio2: '#radio-2', jqRadio2Label: '#radio2-label', jqClueForm: '#clue-form',
        jqClueNum: '#clue-num', jqClueWord: '#clue-word', jqClueText: '#clue-text',
        jqClueMsg: '#clue-msg', jqClueUpdateBtn: '#clue-update', jqClueDeleteBtn: "#clue-delete",
        jqPuzzleDiv: '#puzzle'
    };
    controller = null;

    constructor(controller) {
        this.controller = controller;
        $(this.ID.jqSizeLabel).text("Grid Size");
        $(this.ID.jqRadio1Label).text("Blocks");
        $(this.ID.jqRadio2Label).text("Clues");
        $(this.ID.jqSaveOkIcon).prop("hidden", true);
    }

    initialize() {
        let title = (this.controller.id === 0) ?
            "New Crossword" : "Edit Crossword #" + this.controller.id;
        $(this.ID.jqTitle).text(title);
        (this.controller.id === 0) ? this.disableDelete() : this.disableDelete(false);
        this.disablePublish();
        this.hideClueForm();
        if (this.controller.id > 0) $(this.ID.jqDesc).text(this.controller.desc);
        let size = this.controller.size;
        $(this.ID.jqSizeSelect).val(size);
        this.setPuzzle(this.controller.getPuzzle(size));
        this.bindHandlers();
    }

    bindHandlers() {
        $("input[type=radio][name='switch']").change(this.onSwitchChange);
        $(this.ID.jqSizeSelect).change(this.onSizeChange);
        $(this.ID.jqSaveBtn).click(this.controller.onSaveClick);
        $(this.ID.jqDeleteBtn).click(this.controller.onDeleteClick);
        $(this.ID.jqDesc).change(this.onDescChange);
        $(window).on('beforeunload', this.onBeforeUnload);
    }

    disableDelete(disable=true) {
        if (disable) $(this.ID.jqDeleteBtn).prop("disabled", true);
        else $(this.ID.jqDeleteBtn).prop("disabled", false);
    }

    disablePublish(disable=true) {
        if (disable) $(this.ID.jqPublishBtn).prop("disabled", true);
        else $(this.ID.jqPublishBtn).prop("disabled", false);
    }

    hideClueForm(hide=true) {
        if (hide) $(this.ID.jqClueForm).hide();
        else $(this.ID.jqClueForm).show();
    }

    setSizeSelector(sizeOptions) {
        Object.keys(sizeOptions).forEach (key => {
            $(this.ID.jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
        });
    }

    setPuzzle(puzzleObj) {
        $(this.ID.jqPuzzleDiv).empty();
        $(this.ID.jqPuzzleDiv).append(puzzleObj);
    }

    getDesc() {
        return $(this.ID.jqDesc).text();
    }

    showSaveOKIcon() {
        $(this.ID.jqSaveOkIcon).show(0, this.hideSaveOKIcon);
    }

    hideSaveOKIcon = () => {
        $(this.ID.jqSaveOkIcon).fadeOut(3000);
    }

    onSizeChange = () => {
        var size = parseInt($(this.ID.jqSizeSelect).val());
        $(this.ID.jqPuzzleDiv).empty().append( this.controller.getPuzzle(size) );
        $(this.ID.jqRadio1).prop("checked", true);
        $(this.ID.jqClueForm).hide();
        this.controller.dataSaved = false;
    }

    onSwitchChange = () => {
        if ($("input[name='switch']:checked").val() === "radio-2") $(this.ID.jqClueForm).show();
        else $(this.ID.jqClueForm).hide();
    }

    onDescChange = () => {
        this.controller.desc = $(this.ID.jqDesc).text();
        this.controller.dataSaved = false;
    }

    onBeforeUnload = (e) => {
        if (this.controller.dataSaved) return;
        return "";
    }
}