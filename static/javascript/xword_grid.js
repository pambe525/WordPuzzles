class XWordGrid {

    cellSize = 29;
    jqGridObj = null;
    size = 15;    /* default size */
    _dataChangeListener = null;

    constructor(puzzleData, clickHandler) {
        if ( puzzleData.size !== undefined ) this.size = puzzleData.size;
        this._createGrid(clickHandler);
        if ( puzzleData.data !== undefined ) this._loadBlocks(puzzleData.data.blocks);
        this._autonumberGrid();
    }

    getPuzzleHtml() {
        return this.jqGridObj;
    }

    toggleBlock(cell) {
        if ($(cell).prop("tagName") !== "DIV") return;
        let symmCell = this._getSymmCell(cell);
        if (this._hasLetter(cell) || this._hasLetter(symmCell)) return;
        this._toggleCellBlock(cell);
        if (cell !== symmCell) this._toggleCellBlock(symmCell);
        this._autonumberGrid();
        this._dataChangeListener.dataChanged();
    }

    hasBlocks() {
        return (this.jqGridObj.find(".xw-block").length > 0);
    }

    setDataChangeListener(listener) {
        this._dataChangeListener = listener;
    }

    hiliteNextIncomplete() {
        let hiliteCells = this._getGridCells().slice(0, this.size);
        $(hiliteCells).addClass("xw-hilite");
    }

    getHilitedCells() {
        return this._getGridCells().filter(".xw-hilite");
    }

    isHiliteAcross() {
        let hilitedCells = this.getHilitedCells();
        if (hilitedCells.length === 0) return null;
        let indexDiff = this._cellIndex(hilitedCells[1]) - this._cellIndex(hilitedCells[0]);
        return ( indexDiff === 1 ) ? "Across" : "Down";
    }

    getHilitedClueNum() {
        return parseInt($(this.getHilitedCells()[0]).children(".xw-number").text());
    }

    getHilitedClueWord() {
        return "";
    }

    getHilitedClueText() {
        return "";
    }

    clearHilite() {
        $(this.getHilitedCells()).removeClass("xw-hilite");
    }

    setHilitedWordData(wordData) {
        let word = wordData.word.toUpperCase().trim();
        let hilitedCells = this.getHilitedCells();
        this._checkWordFit(word, hilitedCells);
        for (let i = 0; i < hilitedCells.length; i++)
            $(hilitedCells[i]).children(".xw-letter").text(word[i]);
    }

    //** PRIVATE METHODS **//
    _createGrid(clickHandler) {
        this.jqGridObj = $("<div></div>").addClass("xw-grid");
        for (var i = 0; i < this.size * this.size; i++)
            $(this.jqGridObj).append(this._createGridCell(clickHandler));
        this._setGridBoxStyling(this.size);
    }

    _createGridCell(clickHandler) {
        var cell = $("<div><span class='xw-letter'></span></div>").click(clickHandler);
        $(cell).children(".xw-letter").click(clickHandler);
        cell.width(this.cellSize).height(this.cellSize);
        cell.css("border-top", "1px solid black").css("border-left", "1px solid black");
        cell.css("float","left").css("box-sizing","border-box");
        return cell;
    }

    _setGridBoxStyling() {
        this.jqGridObj.width(this.cellSize * this.size + 1).height(this.cellSize * this.size + 1);
        this.jqGridObj.css("border-bottom", "1px solid black");
        this.jqGridObj.css("border-right", "1px solid black");
    }

    _getGridCells() {
        return this.jqGridObj.children("div");
    }

    _gridCell(index) {
        return this._getGridCells()[index];
    }

    _hasLetter(cell) {
        return ($(cell).children(".xw-letter").text() !== "");
    }

    _cellIndex(cell) {
        return this.jqGridObj.children("div").index(cell);
    }

    _autonumberGrid() {
        this.jqGridObj.find(".xw-number").remove();
        let clueNum = 1, cell;
        for (var i = 0; i < this.size*this.size; i++) {
            cell = this._gridCell(i);
            if (this._isWordStart(cell) || this._isWordStart(cell, false))
                this._setClueNum(cell, clueNum++);
        }
    }

    _getSymmCell(cell) {
        let index = this._cellIndex(cell);
        let symmIndex = this.size * this.size - index - 1;
        return this._gridCell(symmIndex);
    }

    _toggleCellBlock(cell) {
        if ( $(cell).hasClass("xw-block") ) $(cell).removeClass("xw-block");
        else $(cell).addClass("xw-block");
    }

    _isBlocked(cell) {
        return !!($(cell).hasClass("xw-block"));
    }

    _setClueNum(cell, clueNum) {
        let span = $("<span></span>").addClass("xw-number").text(clueNum);
        $(cell).append(span);
    }

    _isWordStart(cell, isAcross=true) {
        if (this._isBlocked(cell)) return false;
        return !(!this._isNextOpen(cell, isAcross) || this._isPrevOpen(cell, isAcross));
    }

    _isNextOpen(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell) ;
        if ( this._isLast(cell, isAcross) ) return false;
        let nextCellIndex = (isAcross) ? cellIndex + 1 : cellIndex + this.size;
        return !this._isBlocked(this._gridCell(nextCellIndex));
    }

    _isPrevOpen(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell) ;
        if ( this._isFirst(cell, isAcross) ) return false;
        let prevCellIndex = (isAcross) ? cellIndex - 1 : cellIndex - this.size;
        return !this._isBlocked(this._gridCell(prevCellIndex));
    }

    _isLast(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell);
        if ( isAcross && (cellIndex + 1) % this.size === 0 ) return true;
        return !isAcross && (cellIndex + this.size) > this.size * this.size;

    }

    _isFirst(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell);
        if ( isAcross && (cellIndex % this.size) === 0 ) return true;
        if ( !isAcross && (cellIndex < this.size ) ) return true;
    }

    _loadBlocks(blocks) {
        let blockedIndices = blocks.split(",");
        let gridCells = this._getGridCells();
        for (var i = 0; i < blockedIndices.length; i++)
            $(gridCells[parseInt(blockedIndices[i])]).addClass("xw-block");
    }

    _checkWordFit(word, hilitedCells) {
        if (hilitedCells.length !== word.length)
            throw new Error("Word must be " + hilitedCells.length + " chars");
        if (!/^[A-Za-z]+$/.test(word)) throw new Error("Word must contain all letters");
    }
}
