/**
 * ABSTRACT BASE CLASS PUZZLE (all puzzle classes are derived from this). This class cannot be instantiated
 */
class Puzzle {

    id = null;
    isXword = true;
    editor = null;
    size = 0;
    desc = "";
    sharedAt = null;
    divId = null;
    puzzleData = null;
    saveSuccessHandler = null;
    saveFailureHandler = null;
    deleteSuccessHandler = null;
    deleteFailureHandler = null;
    dataChangedHandler = null;
    clickHandler = null;

    constructor(arg) {
        if (this.constructor.name === "Puzzle") throw new Error("Abstract Class Puzzle cannot be instantiated");
        if (!arg) throw new Error("No argument specified on Puzzle");
        if (typeof(arg) !== 'object') this.size = arg;
        else {
            this.puzzleData = arg;
            this.size = this.puzzleData['size'];
            this.id = this.puzzleData['id'];
        }
    }

    /**
     * PUBLIC METHODS
     */

    show(divId) {
        this.divId = "#"+divId;
        $(this.divId).empty();
        this._setHtmlOnPuzzleDiv();
        if (this.puzzleData) this._loadPuzzleData();
    }

    // Derived class must implement this
    isReady() {
        throw new Error("Puzzle.isReady method must be implemented by derived class");
    }

    setSharingOn(turnOn=true) {
        if (turnOn) this.sharedAt = new Date().toISOString();
        else this.sharedAt = null;
    }

    save() {
        var puzzle_data = {
            id: this.id, size: this.size, is_ready: this.isReady(), desc: this.desc,
            is_xword: this.isXword, shared_at: this.sharedAt, data: this._getDataToSave()
        };
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(puzzle_data)},
            success: this._saveSucceeded,
            error: this._saveFailed,
        })
    }

    delete() {
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action': 'delete', id: this.id},
            success: this._deleteSucceeded,
            error: this._deleteFailed,
        })
     }

    setShared(isShared) {
        if ( isShared ) this.sharedAt = new Date().toUTCString();
        else this.sharedAt = null;
    }

    /* THESE HANDLERS MUST BE SET BY CLIENT EDITORS */
    setDataChangedHandler(handlerFunc) {
        this.dataChangedHandler = handlerFunc;
    }

    setSaveSuccessHandler(handlerFunc) {
        this.saveSuccessHandler = handlerFunc;
    }

    setSaveFailureHandler(handlerFunc) {
        this.saveFailureHandler = handlerFunc;
    }

    setDeleteSuccessHandler(handlerFunc) {
        this.deleteSuccessHandler = handlerFunc;
    }

    setDeleteFailureHandler(handlerFunc) {
        this.deleteFailureHandler = handlerFunc;
    }

    setClickHandler(handlerFunc) {
        this.clickHandler = handlerFunc;
    }

    /**
     * PRIVATE METHODS
     */
    _saveSucceeded = (result) => {
        this.id = result.id;
        if (this.saveSuccessHandler) this.saveSuccessHandler(result);
    }

    _saveFailed = (jqXHR, status, error) => {
        if (this.saveFailureHandler) this.saveFailureHandler(jqXHR, status, error);
    }

    _deleteSucceeded = (result) => {
        if (this.deleteSuccessHandler) this.deleteSuccessHandler(result);
    }

    _deleteFailed = (result) => {
        if (this.deleteFailureHandler) this.deleteFailureHandler(result);
    }

    // Must be implemented by derived classes
    _setHtmlOnPuzzleDiv() {
        throw new Error("Puzzle._setHtmlOnPuzzleDiv method must be implemented.");
    }

    // Must be implemented by derived classes
    _loadPuzzleData(puzzleData) {
        throw new Error("Puzzle._loadPuzzleData method must be implemented.");
    }

    // Must be called by derived classes when data changes
    _dataChanged() {
        if (this.dataChangedHandler) this.dataChangedHandler();
    }

    // Must be populated by derived classes to prepare save data object
    _getDataToSave() {
        throw new Error("Puzzle._getDataToSave method must be implemented.");
    }
}