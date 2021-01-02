class EditPuzzleView {
    ID = {
        jqHomeBtn: "#home", jqTitle: '#page-title', jqSaveOkIcon: '#save-ok', jqSaveBtn: '#save',
        jqDeleteBtn: "#delete", jqPublishBtn: '#publish', jqUnpublishBtn: "#unpublish", jqDesc: '#desc',
        jqSizeLabel: '#size-label', jqSizeSelect: '#size', jqRadio1: '#radio-1', jqRadio1Label: "#radio1-label",
        jqRadio2: '#radio-2', jqRadio2Label: '#radio2-label', jqClueForm: '#clue-form',
        jqClueRef: '#clue-ref', jqClueWord: '#clue-word', jqClueText: '#clue-text',
        jqClueMsg: '#clue-msg', jqClueUpdateBtn: '#clue-update', jqClueDeleteBtn: "#clue-delete",
        jqPuzzleDiv: '#puzzle', jqStatus: '#status', jqNavbar: '#navbar'
    };

    dataSaved = true;
    isXWord = true;
    id = 0;
    sharedAt = null;

    //==> CONSTRUCTOR
    constructor(puzzleData) {
        if ( puzzleData.id ) this.id = puzzleData.id;
        if (this.id > 0) $(this.ID.jqDesc).text(puzzleData.desc);
        if (puzzleData.shared_at) this.sharedAt = puzzleData.shared_at;
        $(this.ID.jqSaveOkIcon).prop("hidden", true);
        this._hideUnpublish();
        $(this.ID.jqTitle).text( this._buildTitle() );
        (this.id === 0) ? this._disableDelete() : this._disableDelete(false);
        this.disablePublish();
        this._setClueFormTabIndex();
    }

    //==> PUBLIC METHODS
    bindHandlers(controller) {
        $("input[name='switch']").change(controller.onSwitchChange);
        $(this.ID.jqSizeSelect).change(controller.onSizeChange);
        $(this.ID.jqSaveBtn).click(controller.onSaveClick);
        $(this.ID.jqClueUpdateBtn).click(controller.onClueUpdateClick);
        $(this.ID.jqPublishBtn).click(this._onPublishClick);
        $(this.ID.jqUnpublishBtn).click(this._onUnpublishClick);
        $(this.ID.jqDeleteBtn).click(this._onDeleteClick);
        $(this.ID.jqDesc).change(this._onDescChange);
        $(this.ID.jqClueWord).keypress(this._onEnterKey);
        $(this.ID.jqClueText).keypress(this._onEnterKey);
        $(window).on('beforeunload', this._onBeforeUnload);
    }
    dataChanged = () => {
        this.dataSaved = false;
    }
    disablePublish(disable=true) {
        $(this.ID.jqPublishBtn).prop("disabled", disable);
    }
    getActiveSwitchLabel() {
        if ( $("input[name='switch']:checked").val() === "radio-1" ) return $(this.ID.jqRadio1Label).text();
        else return $(this.ID.jqRadio2Label).text();
    }
    getClueFormInput() {
        let formData = {}
        formData.word = $(this.ID.jqClueWord).val();
        formData.clue = $(this.ID.jqClueText).val();
        return formData;
    }
    getSizeSelection() {
        return parseInt($(this.ID.jqSizeSelect).val());
    }
    hideClueForm(hide=true) {
        if (hide) $(this.ID.jqClueForm).hide();
        else $(this.ID.jqClueForm).show();
    }
    isPublished() {
        return (this.sharedAt !== null);
    }
    save(puzzleData) {
        let fullDataObj = this._getData();
        fullDataObj["data"] = puzzleData;
        $.ajax({
            method: "POST",
            dataType: "json",
            data: { 'action':'save', 'data': JSON.stringify(fullDataObj) },
            success: this._onSaveSuccess,
            error: this._onServerError,
        });
    }
    selectSwitchLabel(label) {
        if ( $(this.ID.jqRadio1Label).text() === label ) $(this.ID.jqRadio1).prop("checked", true).change();
        else $(this.ID.jqRadio2).prop("checked", true).change();
    }
    setClueForm(formFields) {
        $(this.ID.jqClueRef).text(formFields.clueRef);
        $(this.ID.jqClueWord).val(formFields.clueWord);
        $(this.ID.jqClueText).val(formFields.clueText);
        $(this.ID.jqClueWord).attr("maxlength", formFields.maxLength);
        $(this.ID.jqClueMsg).text("");
        $(this.ID.jqClueWord).focus();
        //(formFields.word === "") ? $(this.IDs.clueWord).focus() : $(this.IDs.clueText).focus()
    }
    setClueMsg(message) {
        $(this.ID.jqClueMsg).text(message);
    }
    setPublishedState() {
        this._hideUnpublish(false);
        this.hideClueForm();
        $(this.ID.jqNavbar).hide();
    }
    setPuzzleContent(puzzleHtml) {
        $(this.ID.jqPuzzleDiv).empty();
        $(this.ID.jqPuzzleDiv).append(puzzleHtml);
    }
    setSize(value) {
        $(this.ID.jqSizeSelect).val(value);
    }
    setSizeSelector(sizeOptions, defaultVal) {
        Object.keys(sizeOptions).forEach (key => {
            $(this.ID.jqSizeSelect).append($("<option></option>").val(key).text(sizeOptions[key]));
        });
        $(this.ID.jqSizeSelect).val(defaultVal);
    }
    setStatus(statusText) {
        $(this.ID.jqStatus).text(statusText);
    }
    setUILabels(labels) {
        $(this.ID.jqSizeLabel).text(labels.size);
        $(this.ID.jqRadio1Label).text(labels.radio1);
        $(this.ID.jqRadio2Label).text(labels.radio2);
    }

    //==> PRIVATE METHODS
    _buildTitle(){
        return (this.id === 0) ? "New Crossword" : "Edit Crossword #" + this.id;
    }
    _disableDelete(disable=true) {
        $(this.ID.jqDeleteBtn).prop("disabled", disable);
    }
    _getData() {
        return {is_xword: this.isXWord, id: this.id, size: parseInt($(this.ID.jqSizeSelect).val()),
                desc: $(this.ID.jqDesc).text(), shared_at: this.sharedAt, data:{}};
    }
    _hideSaveOKIcon = () => {
        $(this.ID.jqSaveOkIcon).fadeOut(3000);
    }
    _hideUnpublish(hide=true) {
        if (hide) {
            $(this.ID.jqUnpublishBtn).hide();
            $(this.ID.jqPublishBtn).show();
        } else {
             $(this.ID.jqUnpublishBtn).show();
            $(this.ID.jqPublishBtn).hide();
        }
    }
    _setClueFormTabIndex() {
        $(this.ID.jqClueWord).attr('tabindex', 1);
        $(this.ID.jqClueText).attr('tabindex', 2);
    }
    _showSaveOKIcon() {
        $(this.ID.jqSaveOkIcon).show(0, this._hideSaveOKIcon);
    }

    //==> PRIVATE EVENT HANDLERS
    _onBeforeUnload = () => {
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
    _onDescChange = () => {
        this.dataChanged();
    }
    _onEnterKey = (event) => {
        if (event.keyCode === 13) $(this.ID.jqClueUpdateBtn).click();
    }
    _onPublishClick = () => {
        let message = "Puzzle will be accessible to all users. Editing will be disabled. Please confirm.";
        let confirmed = confirm(message);
        if (confirmed) {
            this.setPublishedState();
            this.sharedAt = new Date().toISOString();
            $(this.ID.jqSaveBtn).click();
        }
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
    _onUnpublishClick = () => {
        let message = "Puzzle will not be accessible to users. Editing will be re-enabled. Please confirm.";
        let confirmed = confirm(message);
        if (confirmed) {
            this._hideUnpublish();
            $(this.ID.jqNavbar).show();
            this.sharedAt = null;
            $(this.ID.jqSaveBtn).click();
        }
    }
}