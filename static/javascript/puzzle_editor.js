class PuzzleEditor {
    ID = {
        jqHomeBtn: "#home", jqTitle: '#page-title', jqSaveOkIcon: '#save-ok', jqSaveBtn: '#save',
        jqDeleteBtn: "#delete", jqPublishBtn: '#publish', jqDesc: '#desc', jqSizeLabel: '#size-label',
        jqSizeSelect: '#size', jqRadio1: '#radio-1', jqRadio1Label: "#radio1-label",
        jqRadio2: '#radio-2', jqRadio2Label: '#radio2-label', jqClueForm: '#clue-form',
        jqClueNum: '#clue-num', jqClueWord: '#clue-word', jqClueText: '#clue-text',
        jqClueMsg: '#clue-msg', jqClueUpdateBtn: '#clue-update', jqClueDeleteBtn: "#clue-delete",
        jqPuzzleDiv: '#puzzle'
    };
    puzzle = null;
    dataSaved = false;

    constructor(puzzle) {
        this.puzzle = puzzle;
        $(this.ID.jqSaveOkIcon).prop("hidden", true);
    }

    setSizeSelector(sizeOptions) {
        Object.keys(sizeOptions).forEach (key => {
            $(this.ID.jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
        });
    }

    setUILabels(labels) {
        $(this.ID.jqSizeLabel).text(labels.size);
        $(this.ID.jqRadio1Label).text(labels.radio1);
        $(this.ID.jqRadio2Label).text(labels.radio2);
    }

    xxx(labels, sizeOptions) {
        this.puzzle = this.createPuzzleInstance(puzzleData);
        var labels = this.puzzle.getUILabels();

        $(this.ID.jqTitle).text( this.buildTitle() );
        this.setSizeSelector(this.puzzle.getSizeOptions());
        (this.puzzle.id === 0) ? this.disableDelete() : this.disableDelete(false);
        this.disablePublish();
        this.hideClueForm();
        if (this.puzzle.id > 0) $(this.ID.jqDesc).text(this.puzzle.desc);
        $(this.ID.jqSizeSelect).val(this.puzzle.size);
        this.setPuzzle(this.puzzle.getPuzzleContents());
        this.bindHandlers();
    }

    /** PRIVATE METHODS **/

    createPuzzleInstance(puzzleData) {
        return new XWordPuzzle(puzzleData);
    }

    buildTitle() {
        var title;
        title = (this.puzzle.id === 0) ? "New Crossword" : "Edit Crossword #" + this.puzzle.id;
        return title;
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
        this.puzzle =
        $(this.ID.jqPuzzleDiv).empty().append( this.puzzle.getPuzzleContents() );
        $(this.ID.jqRadio1).prop("checked", true);
        $(this.ID.jqClueForm).hide();
        this.dataSaved = false;
    }

    onSwitchChange = () => {
        if ($("input[name='switch']:checked").val() === "radio-2") $(this.ID.jqClueForm).show();
        else $(this.ID.jqClueForm).hide();
    }

    onDescChange = () => {
        this.puzzle.desc = $(this.ID.jqDesc).text();
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
            data: {action: 'delete', id: this.puzzle.id},
            success: this.onDeleteSuccess,
            error: this.onServerError,
        });
    }

    onDeleteSuccess = (result) => {
        window.location.replace("/");
    }

    onSaveClick = () => {
        this.puzzle.desc = $(this.ID.jqDesc).text();
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(this.puzzle.getData())},
            success: this.onSaveSuccess,
            error: this.onServerError,
        });
    }

    onSaveSuccess = (result) => {
        if (result['error_message'] !== undefined && result['error_message'] !== "") {
            alert(result['error_message']);
        } else {
            this.puzzle.id = result.id;
            this.showSaveOKIcon();
            this.disableDelete(false);
            this.dataSaved = true;
        }
    }

    onServerError = (xhr, status, error) => {
        alert(error);
    }
}