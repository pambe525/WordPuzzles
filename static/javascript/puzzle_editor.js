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

    constructor(puzzleDivId) {
        if (!puzzleDivId) throw new Error("No argument specified on Puzzle");
        this.IDs.puzzleDiv = "#" + puzzleDivId;
    }

    setElementId(elemRef, elemId) {
        if (this.IDs[elemRef] === undefined) throw new Error("Invalid element reference " + elemRef);
        if ($("#" + elemId).length === 0) throw new Error("Element id " + elemId + " not found");
        this.IDs[elemRef] = elemId;
    }

    initialize() {
        this._checkPageElementsExist();
        this._setDefaultUIState();
        this._configureUIElements();
    }

    _setDefaultUIState() {
        $(this.IDs.saveOk).hide();
        $(this.IDs.deleteBtn).prop("disabled", "true");
        $(this.IDs.clueForm).hide();
        $(this.IDs.clueWord).css("text-transform", "uppercase");
    }
    _checkPageElementsExist() {
        for (var key in this.IDs)
            if ($(this.IDs[key]).length === 0) throw new Error(this.IDs[key] + " does not exist");
    }

    _setupEventHandlers() {
        $(this.IDs.sizeSelect).change(this._sizeSelectionChanged);
        $(this.IDs.modeToggle).change(this._modeSelectionChanged);
        $(this.IDs.saveBtn).click(this._saveBtnClicked);
        $(this.IDs.deleteBtn).click(this._deleteBtnClicked);
        $(this.IDs.clueUpdateBtn).click(this._updateWordDataClicked);
        $(this.IDs.clueDeleteBtn).click(this._deleteWordDataClicked)
        $(this.IDs.doneBtn).click(this._doneBtnClicked)
        $(this.IDs.clueWord).keyup(this._onEnterKey);
        $(this.IDs.clueText).keyup(this._onEnterKey);
    }

    _onEnterKey = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            $(this.IDs.clueUpdateBtn).click();
        }
    }

    _setPageTitle() {

    }

    /* The following private methods must be implemented by derived classes */
    _getNewPuzzleInstance() {

    }
    _configureUIElements() {
        // setup size selector and element labels
    }

    _sizeSelectionChanged = () => {
    }

    _modeSelectionChanged = () => {
    }

    _updateWordDataClicked = () => {
    }

    _deleteWordDataClicked = () => {
    }

    _saveBtnClicked = () => {
    }

    _deleteBtnClicked = () => {
    }

    _puzzleClicked = (event) => {

    }

    // This is not unit tested
    _doneBtnClicked = () => {
        window.location.replace("/");
    }
}
