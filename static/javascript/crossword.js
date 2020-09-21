class Crossword {

    cellSize = 30;

    constructor(divId, clickHandler, gridSize) {
        this.gridSize = gridSize;
        this.gridId = "#" + divId;
        this.clickHandler = clickHandler;
        this._validateArgs();
        this._makeGrid();
        this._setStyle();
    }

    toggleCellBlock(cellId) {
        if (cellId === null || $("#" + cellId).length === 0) return false;
        var symmCellId = this._getSymmetricCellId(cellId);
        this._toggleBlock(cellId);
        if (cellId !== symmCellId) this._toggleBlock(symmCellId);
        this._autoNumberCells();
        return true;
    }

    hasBlocks() {
        return ($(".xw-blocked").length !== 0);
    }

    // NON-PUBLIC METHODS

    _validateArgs() {
        if (typeof (this.gridSize) != "number") throw new Error("gridSize must be a number");
        if ($(this.gridId).length === 0) throw new Error("divId does not exist");
        if (typeof (this.clickHandler) != "function") throw new Error("clickHandler must be a function");
    }

    _makeGrid() {
        $(this.gridId).empty();
        for (var row = 0; row < this.gridSize; row++)
            for (var col = 0; col < this.gridSize; col++)
                $(this.gridId).append(this._createGridCell(row, col));
        this._autoNumberCells();
    }

    _setStyle() {
        $("#xw-style").remove();
        var css, gridLength = this.gridSize * this.cellSize + 2;
        css = this.gridId + "{border:1px solid black;" +
            "width:" + gridLength + "px;height:" + gridLength + "px}";
        css += ".xw-blocked {background-color:black;}";
        css += ".xw-number {font-size:9px; top:-2px; left:1px; position:absolute}";
        css += this.gridId + " > div {width:" + this.cellSize + "px; height:" + this.cellSize + "px;" +
            "border:1px solid black; float:left; position: relative}";
        var styleTag = "<style id='xw-style' type='text/css'></style>";
        $(styleTag).html(css).appendTo("head");
    }

    _getCellId(row, col) {
        return (row + "-" + col);
    }

    _createGridCell(row, col) {
        var cellId = this._getCellId(row, col);
        return $("<div></div>").click(this.clickHandler).attr('id', cellId);
    }

    _autoNumberCells() {
        var counter = 0, id;
        $(".xw-number").remove();
        for (var row = 0; row < this.gridSize; row++) {
            for (var col = 0; col < this.gridSize; col++) {
                id = this._getCellId(row, col);
                if (this._cellIsStartOfWord(id)) this._setNumberOnCell(id, ++counter);
            }
        }
    }

    _setNumberOnCell(id, number) {
        var cellNumber = $("<span></span>").text(number);
        cellNumber.addClass("xw-number");
        $("#" + id).append(cellNumber);
    }

    _getSymmetricCellId(cellId) {
        var coord = cellId.split("-");
        var symmRow = this.gridSize - parseInt(coord[0]) - 1;
        var symmCol = this.gridSize - parseInt(coord[1]) - 1;
        return this._getCellId(symmRow, symmCol);
    }

    _isBlockedCell(cellId) {
        if (cellId === null) return true;
        return !!($("#" + cellId).hasClass("xw-blocked"));
    }

    _toggleBlock(cellId) {
        var jqCellId = "#" + cellId;
        if (this._isBlockedCell(cellId)) $(jqCellId).removeClass("xw-blocked");
        else {
            $(jqCellId).addClass("xw-blocked");
            $(jqCellId + " > .xw-number").remove();
        }
    }

    _cellIsStartOfWord(cellId) {
        if (this._isBlockedCell(cellId)) return false;
        var lCellId = this._getOffsetCellId(cellId, -1, 0);
        var rCellId = this._getOffsetCellId(cellId, 1, 0);
        var tCellId = this._getOffsetCellId(cellId, 0, -1);
        var bCellId = this._getOffsetCellId(cellId, 0, 1);
        if (this._isBlockedCell(lCellId) && !this._isBlockedCell(rCellId)) return true;
        return !!(this._isBlockedCell(tCellId) && !this._isBlockedCell(bCellId));
    }

    _getOffsetCellId(cellId, rowOffset, colOffset) {
        var coord = cellId.split("-");
        var cellRow = parseInt(coord[0]) + rowOffset;
        var cellCol = parseInt(coord[1]) + colOffset;
        if (!this._isWithinGrid(cellRow, cellCol)) return null;
        return this._getCellId(cellRow, cellCol);
    }

    _isWithinGrid(row, col) {
        return !(row < 0 || row >= this.gridSize || col < 0 || col >= this.gridSize);
    }
}
