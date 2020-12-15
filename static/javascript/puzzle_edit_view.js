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
    id = 0;
    desc = "";
    size = 15;
    sharedAt = null;
    dataSaved = false;

    constructor(controller) {
        this.controller = controller;
        $(this.ID.jqSizeLabel).text("Grid Size");
        $(this.ID.jqRadio1Label).text("Blocks");
        $(this.ID.jqRadio2Label).text("Clues");
        $(this.ID.jqSaveOkIcon).prop("hidden", true);
    }

    initialize() {
        let title = (this.id === 0) ?
            "New Crossword" : "Edit Crossword #" + this.id;
        $(this.ID.jqTitle).text(title);
        (this.id === 0) ? this.disableDelete() : this.disableDelete(false);
        this.disablePublish();
        this.hideClueForm();
        if (this.id > 0) $(this.ID.jqDesc).text(this.desc);
        let size = this.size;
        $(this.ID.jqSizeSelect).val(size);
        this.setPuzzle(this.controller.getPuzzle(size));
        this.bindHandlers();
    }

    bindHandlers() {
        $("input[name='switch']").change(this.onSwitchChange);
        $(this.ID.jqSizeSelect).change(this.onSizeChange);
        $(this.ID.jqSaveBtn).click(this.onSaveClick);
        $(this.ID.jqDeleteBtn).click(this.onDeleteClick);
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
        this.dataSaved = false;
    }

    onSwitchChange = () => {
        if ($("input[name='switch']:checked").val() === "radio-2") $(this.ID.jqClueForm).show();
        else $(this.ID.jqClueForm).hide();
    }

    onDescChange = () => {
        this.desc = $(this.ID.jqDesc).text();
        this.dataSaved = false;
    }

    onBeforeUnload = (e) => {
        if (this.dataSaved) return;
        return "";
    }

    onDeleteClick = () =>{
        var msg = "All saved data will be permanently deleted.";
        var response = confirm(msg);
        if ( !response ) return;
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {action: 'delete', id: this.id},
            success: this.onDeleteSuccess,
            error: this.onServerError,
        });
    }

    onDeleteSuccess = (result) => {
        window.location.replace("/");
    }

    onSaveClick = () => {
        this.desc = $(this.ID.jqDesc).text();
        let data = {is_xword: true, id: this.id, size: this.size, desc: this.desc,
            shared_at: this.sharedAt};
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(data)},
            success: this.onSaveSuccess,
            error: this.onServerError,
        });
    }

    onSaveSuccess = (result) => {
        if (result['error_message'] !== undefined && result['error_message'] !== "") {
            alert(result['error_message']);
        } else {
            this.id = result.id;
            this.showSaveOKIcon();
            this.disableDelete(false);
            this.dataSaved = true;
        }
    }

    onServerError = (xhr, status, error) => {
        alert(error);
    }
}