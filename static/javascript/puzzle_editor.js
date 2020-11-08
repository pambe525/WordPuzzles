/**
 * ABSTRACT BASE CLASS PuzzleEditor. This class cannot be instantiated.
 */
class PuzzleEditor {

    IDs = {
        title: '#page-title', saveOk: '#save-ok', saveBtn: '#save', deleteBtn: "#delete", doneBtn: "#done",
        desc: '#desc', shared: '#share-toggle', sizeLable: '#size-label', sizeSelect: '#size',
        modeToggle: '#mode-toggle', symmOption: '#symm-option', symmToggle: '#symm-toggle',
        clueForm: '#clue-form', clueNum: '#clue-num', clueWord: '#clue-word', clueText: '#clue-text',
        clueMsg: '#clue-msg', clueUpdateBtn: '#clue-update', clueDeleteBtn: "#clue-delete", puzzleDiv: '#puzzle'
    };
    dataSaved = false;
    puzzleInstance = null;
    puzzleDivId = "puzzle";

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
        this._checkPageElementsExist();
        this._setDefaultUIState();
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
        //$(this.IDs.sizeSelect + " option[value='" + defaultVal + "']").attr("selected","selected");
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
    _setDefaultUIState() {
        $(this.IDs.saveOk).hide();
        $(this.IDs.deleteBtn).prop("disabled", "true");
        $(this.IDs.clueForm).hide();
        $(this.IDs.clueWord).css("text-transform", "uppercase");
        $(this.IDs.shared).prop("disabled", true);
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
        // $(this.IDs.doneBtn).click(this._doneBtnClicked)
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
        $(this.IDs.title).text(prefix + type);
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
        throw new Error("PuzzleEditor._saveBtnClicked method must be implemented.");
    }

    _deleteBtnClicked = () => {
        throw new Error("PuzzleEditor._deleteBtnClicked method must be implemented.");
    }

    _doneBtnClicked = () => {
        window.location.replace("/");
    }

    _dataSaved() {
        $(this.IDs.saveBtn).prop("disabled", true);
        $(this.IDs.saveOk).prop("hidden", true);
        this.dataSaved = true;
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
        if (result['error_message']) {
            alert(result['error_message']);
        } else {
            this.puzzleInstance.id = result.id;
            this._dataSaved();
        }
        this._dataSaved();
    }

    _deleteSuccessHandler = (event) => {
        throw new Error("PuzzleEditor._deleteSuccessHandler method must be implemented.");
    }

    _saveFailureHandler = (event) => {
        throw new Error("PuzzleEditor._saveFailureHandler method must be implemented.");
    }

    _deleteFailureHandler = (event) => {
        throw new Error("PuzzleEditor._deleteFailureHandler method must be implemented.");
    }

    _dataChangedHandler = () => {
        throw new Error("PuzzleEditor._dataChangedHandler method must be implemented.");
    }

    _puzzleClicked = (event) => {
        throw new Error("PuzzleEditor._puzzleClicked method must be implemented.");
    }
}
