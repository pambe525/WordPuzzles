/**
 * ABSTRACT BASE CLASS PuzzleEditor. This class cannot be instantiated.
 */
class PuzzleEditor {

    IDs = {
        title: '#page-title', saveOk: '#save-ok', saveBtn: '#save', deleteBtn: "#delete", homeBtn: "#home",
        desc: '#desc', shareBtn: '#share', sizeLabel: '#size-label', sizeSelect: '#size', toggle1: '#toggle-1',
        toggle2: '#toggle-2', clueForm: '#clue-form', clueNum: '#clue-num', clueWord: '#clue-word',
        clueText: '#clue-text', clueMsg: '#clue-msg', clueUpdateBtn: '#clue-update',
        clueDeleteBtn: "#clue-delete", puzzleDiv: '#puzzle'
    };
    dataSaved = false;
    puzzleInstance = null;
    puzzleDivId = "puzzle";

    static getPuzzleEditorInstance(puzzleData) {

    }

    constructor() {
        if (this.constructor.name === "PuzzleEditor")
            throw new Error("Abstract Class PuzzleEditor cannot be instantiated");
    }

    setElementId(elemRef, elemId) {
        if (this.IDs[elemRef] === undefined) throw new Error("Invalid element reference " + elemRef);
        if ($("#" + elemId).length === 0) throw new Error("Element id " + elemId + " not found");
        this.IDs[elemRef] = elemId;
    }

    initialize(puzzleData) {
        if (puzzleData && typeof(puzzleData) !== 'object') throw new Error("Invalid puzzle data");
        this._checkPageElementsExist();
        this._setDefaultUIState(puzzleData);
        this._configureUIElements();
        this._setupUIEventHandlers();
        this.puzzleInstance = this._getPuzzleInstance(puzzleData);
        this._setupPuzzleEventHandlers();
        this.puzzleInstance.show(this.puzzleDivId);
        this._setPageTitle();
    }

    setSizeSelector(jsonData, defaultVal) {
        for (let value in jsonData)
            $(this.IDs.sizeSelect).append($("<option></option>").val(value).text(jsonData[value]));
        $(this.IDs.sizeSelect).val(defaultVal);
    }

    getSelectedSize() {
        return parseInt($(this.IDs.sizeSelect).val());
    }

    setUnloadHandler() {
        $(window).on('beforeunload', this._handleUnload);
    }

    /**
     * PRIVATE METHODS
     */
    _setDefaultUIState(puzzleData) {
        if (puzzleData && puzzleData.id > 0) {
            $(this.IDs.saveOk).hide();
            $(this.IDs.saveBtn).prop("disabled", true);
            $(this.IDs.deleteBtn).prop("disabled", false);
        } else {
            $(this.IDs.saveOk).hide();
            $(this.IDs.saveBtn).prop("disabled", false);
            $(this.IDs.deleteBtn).prop("disabled", true);
        }
        $(this.IDs.clueForm).hide();
        $(this.IDs.clueWord).css("text-transform", "uppercase");
        $(this.IDs.shareBtn).prop("disabled", true);
        this._setClueFormTabIndex();
    }

    _checkPageElementsExist() {
        for (var key in this.IDs)
            if ($(this.IDs[key]).length === 0) throw new Error(this.IDs[key] + " does not exist");
    }

    _setupUIEventHandlers() {
        $(this.IDs.sizeSelect).change(this._sizeSelectionChanged);
        $(this.IDs.modeToggle).change(this._modeSelectionChanged);
        $(this.IDs.saveBtn).click(this._saveBtnClicked);
        $(this.IDs.deleteBtn).click(this._deleteBtnClicked);
        $(this.IDs.homeBtn).click(this._homeBtnClicked)
        $(this.IDs.clueUpdateBtn).click(this._updateWordDataClicked);
        $(this.IDs.clueDeleteBtn).click(this._deleteWordDataClicked)
        $(this.IDs.clueWord).keyup(this._onEnterKey);
        $(this.IDs.clueText).keyup(this._onEnterKey);
    }

    _setupPuzzleEventHandlers() {
        this.puzzleInstance.setSaveSuccessHandler(this._saveSuccessHandler);
        this.puzzleInstance.setDeleteSuccessHandler(this._deleteSuccessHandler);
        this.puzzleInstance.setSaveFailureHandler(this._saveFailureHandler);
        this.puzzleInstance.setDeleteFailureHandler(this._deleteFailureHandler);
        this.puzzleInstance.setDataChangedHandler(this._dataChangedHandler);
        this.puzzleInstance.setClickHandler(this._puzzleClicked);
    }

    _onEnterKey = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            $(this.IDs.clueUpdateBtn).click();
        }
    }

    _setClueFormTabIndex() {
        $(this.IDs.clueWord).attr('tabindex', 1);
        $(this.IDs.clueText).attr('tabindex', 2);
    }

    _setPageTitle() {
        var prefix = (!this.puzzleInstance.id) ? "New " : "Edit ";
        var type = (this.puzzleInstance.isXword) ? "Crossword Puzzle" : "Word Puzzle";
        var suffix = (!this.puzzleInstance.id) ? "" : " #"+this.puzzleInstance.id;
        $(this.IDs.title).text(prefix + type + suffix);
    }

    /* The following private methods must be implemented by derived classes */
    _getPuzzleInstance(arg) {
        throw new Error("Method PuzzleEditor._getPuzzleInstance must be implemented.");
        // arg can be size or puzzledata
    }
    _configureUIElements() {
        throw new Error("Method PuzzleEditor._configureUIElements must be implemented.");
        // setup size selector and element labels
        // call this.setSizeSelector()
    }

    // UI elements Event Handlers
    //--------------------------------------------------------------------------------------------
    _sizeSelectionChanged = () => {
        throw new Error("PuzzleEditor._sizeSelectionChanged method must be implemented.");
    }

    _modeSelectionChanged = () => {
        throw new Error("PuzzleEditor._modeSelectionChanged method must be implemented.");
    }

    _updateWordDataClicked = () => {
        throw new Error("PuzzleEditor._updateWordDataClicked method must be implemented.");
    }

    _deleteWordDataClicked = () => {
        throw new Error("PuzzleEditor._deleteWordDataClicked method must be implemented.");
    }

    _saveBtnClicked = () => {
        if (this.puzzleInstance.id === null) $(this.IDs.deleteBtn).prop("disabled", false);
        this.puzzleInstance.desc = $(this.IDs.desc).text();
        this.puzzleInstance.setShared( $(this.IDs.shared).prop("checked") );
        this.puzzleInstance.save();
    }

    _deleteBtnClicked = () => {
        var msg = "All saved data will be permanently deleted.";
        var deleteData = confirm(msg);
        if (deleteData) this.puzzleInstance.delete();
    }

    _homeBtnClicked = () => {
        window.location.replace("/");
    }

    _dataSaved() {
        $(this.IDs.saveOk).show(400, this._hideIcon);
        this.dataSaved = true;
    }

    _hideIcon = () => {
        $(this.IDs.saveOk).fadeOut(3000);
    }

    // This is not unit tested
    _handleUnload = (e) => {
        if (this.dataSaved) return;
        var msg = "Do you really want to leave this page?"
        if (e) e.returnValue = msg;
        return msg;
    }

    // Puzzle instance Event Handlers
    //--------------------------------------------------------------------------------------------
    _saveSuccessHandler = (result) => {
        if (result['error_message'] !== undefined && result['error_message'] !== "") {
            alert(result['error_message']);
        } else {
            this.puzzleInstance.id = result.id;
            this._dataSaved();
        }
    }

    _deleteSuccessHandler = (event) => {
        //this._dataSaved();
        window.location.replace("/");
    }

    _saveFailureHandler = (jqXHR, status, error) => {
        alert(error);
    }

    _deleteFailureHandler = (jqXHR, status, error) => {
        alert(status);
    }

    _dataChangedHandler = () => {
        $(this.IDs.saveBtn).prop("disabled", false);
        this.dataSaved = false;
    }

    _puzzleClicked = (event) => {
        throw new Error("PuzzleEditor._puzzleClicked method must be implemented.");
    }
}
