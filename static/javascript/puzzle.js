/**
 * BASE CLASS PUZZLE (all puzzle classes are drived from this)
 */
class Puzzle {

    puzzleId = 0;
    isXword = true;
    editor = null;
    size = 0;
    desc = "";
    data = null;
    sharedAt = null;
    divId = null

    saveSuccessHandler = null;
    saveFailureHandler = null;
    deleteSuccessHandler = null;
    deleteFailureHandler = null;
    dataChangedHandler = null;
    clickHandler = null;

    constructor(size) {
        if (size) this.size = size;
    }

    /**
     * PUBLIC METHODS
     */

    // Derived class must call super.show() and implement this
    show(divId) {
        this.divId = "#"+divId;
        $(this.divId).empty();
    }

    // Derived class must implement this
    isReady() {
    }

    save() {
        var puzzle_data = {
            puzzle_id: this.puzzleId, size: this.size, is_ready: this.isReady(), desc: this.desc,
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
            data: {'action': 'delete', 'puzzle_id': this.puzzleId},
            success: this._deleteSucceeded,
            error: this._deleteFailed,
        })
     }

    setDataChangedHndler(handlerFunc) {
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
        this.puzzleId = result.puzzle_id;
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

    // Must be called by derived classes when data changes
    _dataChanged() {
        if (this.dataChangedHandler) this.dataChangedHandler();
    }

    // Must be populated by derived classes to prepare save data object
    _getDataToSave() {
    }
}