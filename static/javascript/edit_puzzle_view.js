class EditPuzzleView {
    ID = {
        jqHomeBtn: "#home", jqTitle: '#page-title', jqSaveOkIcon: '#save-ok', jqSaveBtn: '#save',
        jqDeleteBtn: "#delete", jqPublishBtn: '#publish', jqDesc: '#desc', jqSizeLabel: '#size-label',
        jqSizeSelect: '#size', jqRadio1: '#radio-1', jqRadio1Label: "#radio1-label",
        jqRadio2: '#radio-2', jqRadio2Label: '#radio2-label', jqClueForm: '#clue-form',
        jqClueRef: '#clue-ref', jqClueWord: '#clue-word', jqClueText: '#clue-text',
        jqClueMsg: '#clue-msg', jqClueUpdateBtn: '#clue-update', jqClueDeleteBtn: "#clue-delete",
        jqPuzzleDiv: '#puzzle'
    };

    dataSaved = false;
    isXWord = true;
    id = 0;
    sharedAt = null;

    /* CONSTRUCTOR */
    constructor(puzzleData) {
        if ( puzzleData.id ) this.id = puzzleData.id;
        if (this.id > 0) $(this.ID.jqDesc).text(puzzleData.desc);
        $(this.ID.jqSaveOkIcon).prop("hidden", true);
        $(this.ID.jqTitle).text( this._buildTitle() );
        (this.id === 0) ? this._disableDelete() : this._disableDelete(false);
        this._disablePublish();
    }

    /* PUBLIC METHODS */
    setSizeSelector(sizeOptions, defaultVal) {
        Object.keys(sizeOptions).forEach (key => {
            $(this.ID.jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
        });
        $(this.ID.jqSizeSelect).val(defaultVal);
    }

    setSize(value) {
        $(this.ID.jqSizeSelect).val(value);
    }

    setUILabels(labels) {
        $(this.ID.jqSizeLabel).text(labels.size);
        $(this.ID.jqRadio1Label).text(labels.radio1);
        $(this.ID.jqRadio2Label).text(labels.radio2);
    }

    setPuzzleContent(puzzleHtml) {
        $(this.ID.jqPuzzleDiv).empty();
        $(this.ID.jqPuzzleDiv).append(puzzleHtml);
    }

    bindHandlers(controller) {
        $("input[name='switch']").change(controller.onSwitchChange);
        $(this.ID.jqSizeSelect).change(controller.onSizeChange);
        $(this.ID.jqSaveBtn).click(controller.onSaveClick);
        $(this.ID.jqClueUpdateBtn).click(controller.onClueUpdateClick)
        $(this.ID.jqDeleteBtn).click(this._onDeleteClick);
        $(this.ID.jqDesc).change(this._onDescChange);
        $(window).on('beforeunload', this._onBeforeUnload);
    }

    hideClueForm(hide=true) {
        if (hide) $(this.ID.jqClueForm).hide();
        else $(this.ID.jqClueForm).show();
    }

    getActiveSwitchLabel() {
        if ( $("input[name='switch']:checked").val() === "radio-1" ) return $(this.ID.jqRadio1Label).text();
        else return $(this.ID.jqRadio2Label).text();
    }

    getSizeSelection() {
        return parseInt($(this.ID.jqSizeSelect).val());
    }

    setSwitchLabel(label) {
        if ( $(this.ID.jqRadio1Label).text() === label ) $(this.ID.jqRadio1).prop("checked", true);
        else $(this.ID.jqRadio2).prop("checked", true);
    }

    setClueForm(formFields) {
        $(this.ID.jqClueRef).text(formFields.clueRef);
        $(this.ID.jqClueWord).val(formFields.clueWord);
        $(this.ID.jqClueText).val(formFields.clueText);
        $(this.ID.jqClueWord).attr("maxlength", formFields.maxLength);
        $(this.ID.jqClueMsg).text("");
        //(formFields.word === "") ? $(this.IDs.clueWord).focus() : $(this.IDs.clueText).focus()
    }

    getClueFormInput() {
        let formData = {}
        formData.word = $(this.ID.jqClueWord).val();
        formData.clue = $(this.ID.jqClueText).val();
        return formData;
    }

    setClueMsg(message) {
        $(this.ID.jqClueMsg).text(message);
    }

    save() {
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(this._getData())},
            success: this._onSaveSuccess,
            error: this._onServerError,
        });
    }

    dataChanged = () => {
        this.dataSaved = false;
    }

    /* PRIVATE METHODS */
    _buildTitle(){
        return (this.id === 0) ? "New Crossword" : "Edit Crossword #" + this.id;
    }

    _showSaveOKIcon() {
        $(this.ID.jqSaveOkIcon).show(0, this._hideSaveOKIcon);
    }

    _hideSaveOKIcon = () => {
        $(this.ID.jqSaveOkIcon).fadeOut(3000);
    }

    _getData() {
        return {is_xword: this.isXWord, id: this.id, size: parseInt($(this.ID.jqSizeSelect).val()),
                desc: $(this.ID.jqDesc).text(), shared_at: this.sharedAt};
    }

    _disableDelete(disable=true) {
        $(this.ID.jqDeleteBtn).prop("disabled", disable);
    }

    _disablePublish(disable=true) {
        $(this.ID.jqPublishBtn).prop("disabled", disable);
    }

    /* PRIVATE EVENT HANDLERS */
    _onDescChange = () => {
        this.dataChanged();
    }

    _onBeforeUnload = (e) => {
        if (this.dataSaved) return;
        return "";
    }

    _onDeleteClick = () =>{
        var msg = "All saved data will be permanently deleted.";
        var response = confirm(msg);
        if ( !response ) return;
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {action: 'delete', id: this.id},
            success: this._onDeleteSuccess,
            error: this._onServerError,
        });
    }

    _onDeleteSuccess = (result) => {
        window.location.replace("/");
    }

    _onSaveSuccess = (result) => {
        if (result['error_message'] !== undefined && result['error_message'] !== "") {
            alert(result['error_message']);
        } else {
            this.id = result.id;
            this._showSaveOKIcon();
            this._disableDelete(false);
            this.dataSaved = true;
        }
    }

    _onServerError = (xhr, status, error) => {
        alert(error);
    }
}