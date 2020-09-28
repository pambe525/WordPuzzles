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
        if (cellId === null || $("#"+cellId).length === 0 || $("#"+cellId).hasClass("xw-letter")) return false;
        var symmCellId = this._getSymmetricCellId(cellId);
        this._toggleBlock(cellId);
        if (cellId !== symmCellId) this._toggleBlock(symmCellId);
        this._autoNumberCells();
        return true;
    }

    hasBlocks() {
        return ($(".xw-blocked").length !== 0);
    }

    getWordLength(cellId, isAcross = true) {
        if (!this._isUnblockedCell(cellId)) return 0;
        var beginCoord = this._getCellCoord(this._getWordStartCellId(cellId, isAcross));
        var endCoord = this._getCellCoord(this._getWordEndCellId(cellId, isAcross));
        var index = (isAcross) ? 1 : 0;
        return (endCoord[index] - beginCoord[index] + 1);
    }

    getClueNum(cellId, isAcross = true) {
        return this._getCellNumber(this._getWordStartCellId(cellId, isAcross));
    }

    toggleWordHilite(cellId) {
        var jqCellId = "#"+cellId;
        if ( !$(jqCellId).hasClass("xw-hilited") ) {
            if (this._isWordStart(cellId, true)) this._hiliteCellsInWord(cellId, true);
            else if (this._isWordStart(cellId, false)) this._hiliteCellsInWord(cellId, false);
            else if (this._isInWord(cellId, true)) this._hiliteCellsInWord(cellId, true);
            else if (this._isInWord(cellId, false)) this._hiliteCellsInWord(cellId, false);
        } else {
            if( $(jqCellId).hasClass("xw-across") && this._isInWord(cellId, false) )
                this._hiliteCellsInWord(cellId, false);
            else if ( $(jqCellId).hasClass("xw-down") && this._isInWord(cellId, true) )
                this._hiliteCellsInWord(cellId, true);
        }
    }

    clearHilites() {
        $(this.gridId).children(".xw-hilited").removeClass("xw-hilited")
            .removeClass("xw-across").removeClass("xw-down");
    }

    setEditable(isEditable) {
        $(this.gridId).children('div').attr('contenteditable', (isEditable) ? "true" : "false");
    }

    /**
     * NON-PUBLIC METHODS
     */
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
        var css, gridLength = this.gridSize * this.cellSize + 1;
        css = this.gridId + "{border-left:1px solid black; border-top: 1px solid black;" +
            "width:" + gridLength + "px;height:" + gridLength + "px}";
        css += ".xw-blocked {background-color:black;}";
        css += ".xw-number {font-size:9px; top:-2px; left:1px; position:absolute}";
        css += this.gridId + " > div { width:" + this.cellSize + "px; height:" + this.cellSize + "px;" +
            "border-right:1px solid black; border-bottom:1px solid black; float:left; position: relative;" +
            "text-align:center; font-size:17px; text-transform: uppercase}";
        css += ".xw-hilited {background-color:yellow}";
        css += this.gridId + " > div:focus {background-color: #FFFF99; text-align:center}"
        var styleTag = "<style id='xw-style' type='text/css'></style>";
        $(styleTag).html(css).appendTo("head");
    }

    _getCellId(row, col) {
        return (row + "-" + col);
    }

    _createGridCell(row, col) {
        var cellId = this._getCellId(row, col);
        var cell = $("<div></div>");
        cell.click(this.clickHandler).on('keydown', this._onKeyDown).attr('id', cellId);
        return cell;
    }

    /** NEEDS WORK TO HANDLE TAB & SHIFT-TAB **/
    _onKeyDown = (event) => {
        var cellId = event.target.id, jqCellId = "#"+cellId;
        event.preventDefault();
        if (event.keyCode >= 65 && event.keyCode <= 90) {
            $(jqCellId).html($(jqCellId).children());  // Deletes existing letter but leaves number intact
            $(jqCellId).nextAll(".xw-hilited").first().focus();
            $(jqCellId).append(String.fromCharCode(event.keyCode)).addClass("xw-letter");
        } else if (event.keyCode === 8) {
            if ( !$.isNumeric($(jqCellId).text()) ) $(jqCellId).html($(jqCellId).children());
            else $(jqCellId).prevAll(".xw-hilited").first().focus();
        } else if (event.keyCode === 9) {
        } else if (event.shiftKey && event.keyCode === 9) {
        }
    }

    _autoNumberCells() {
        var counter = 0, id;
        $(".xw-number").remove();
        for (var row = 0; row < this.gridSize; row++) {
            for (var col = 0; col < this.gridSize; col++) {
                id = this._getCellId(row, col);
                if (this._isWordStart(id) || this._isWordStart(id, false)) this._setNumberOnCell(id, ++counter);
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

    _isWordStart(cellId, isAcross=true) {
        if (this._isBlockedCell(cellId)) return false;
        var prevCellId = (isAcross) ? this._getOffsetCellId(cellId,0,-1) : this._getOffsetCellId(cellId,-1,0);
        var nextCellId = (isAcross) ? this._getOffsetCellId(cellId,0, 1) : this._getOffsetCellId(cellId, 1,0);
        return ( !this._isUnblockedCell(prevCellId) && this._isUnblockedCell(nextCellId) );
    }

    _getOffsetCellId(cellId, rowOffset, colOffset) {
        var coord = this._getCellCoord(cellId);
        var cellRow = coord[0] + rowOffset;
        var cellCol = coord[1] + colOffset;
        if (!this._isWithinGrid(cellRow, cellCol)) return null;
        return this._getCellId(cellRow, cellCol);
    }

    _getCellCoord(cellId) {
        var coord = cellId.split("-");
        coord[0] = parseInt(coord[0]);
        coord[1] = parseInt(coord[1]);
        return coord;
    }

    _isWithinGrid(row, col) {
        return !(row < 0 || row >= this.gridSize || col < 0 || col >= this.gridSize);
    }

    _isUnblockedCell(cellId) {
        if (cellId === null) return false;
        var coord = this._getCellCoord(cellId);
        return !(this._isBlockedCell(cellId) || !this._isWithinGrid(coord[0], coord[1]));
    }

    _getCellNumber(cellId) {
        return $("#" + cellId + "> .xw-number").text();
    }

    _getWordStartCellId(cellId, isAcross = true) {
        var newId = cellId, startCellId;
        var rowOffset = (isAcross) ? 0 : -1;
        var colOffset = (isAcross) ? -1 : 0;
        do {
            startCellId = newId;
            newId = this._getOffsetCellId(startCellId, rowOffset, colOffset)
        } while (this._isUnblockedCell(newId));
        return startCellId;
    }

    _getWordEndCellId(cellId, isAcross = true) {
        var newId = cellId, endCellId;
        var rowOffset = (isAcross) ? 0 : 1;
        var colOffset = (isAcross) ? 1 : 0;
        do {
            endCellId = newId;
            newId = this._getOffsetCellId(endCellId, rowOffset, colOffset)
        } while (this._isUnblockedCell(newId));
        return endCellId;
    }

    _hasText(cellId) {
        return (cellId === null) ? false : ($("#" + cellId).text().trim().length > 0);
    }

    _isInWord(cellId, isAcross = true) {
        if (!this._isUnblockedCell(cellId)) return false;
        if (isAcross) {
            var lCellId = this._getOffsetCellId(cellId, 0, -1);
            var rCellId = this._getOffsetCellId(cellId, 0, 1);
            return this._isUnblockedCell(rCellId) || this._isUnblockedCell(lCellId);
        } else {
            var tCellId = this._getOffsetCellId(cellId, -1, 0);
            var bCellId = this._getOffsetCellId(cellId, 1, 0);
            return this._isUnblockedCell(tCellId) || this._isUnblockedCell(bCellId);
        }
    }

    _hiliteCellsInWord(cellId, isAcross=true) {
        this.clearHilites();
        var cellsToHilite = this._getCellsInWord(cellId, isAcross);
        var classLabel = (isAcross) ? "xw-across" : "xw-down";
        if (cellsToHilite.length > 1) cellsToHilite.addClass("xw-hilited").addClass(classLabel);
    }

    _getCellsInWord(cellId, isAcross = true) {
        var startCoord = this._getCellCoord(this._getWordStartCellId(cellId, isAcross));
        var endCoord = this._getCellCoord(this._getWordEndCellId(cellId, isAcross));
        var selector = (isAcross) ? "[id^='" + startCoord[0] + "-']" : "[id$='-" + startCoord[1] + "']";
        var inlineCells = $(this.gridId + " > " + selector);
        var startCellIndex = (isAcross) ? startCoord[1] : startCoord[0];
        var endCellIndex   = (isAcross) ? endCoord[1] : endCoord[0];
        return inlineCells.slice(startCellIndex, endCellIndex+1);
    }

    // _checkWordData(wordData, isAcross=true) {
    //     if ( wordData.word === "" ) throw new Error("Word cannot be blank");
    //     if ( !wordData.word.match(/^[a-z- ]+$/i) ) throw new Error("Word must contain letters only");
    //     var gridWord = this._makeGridWord(wordData.word)
    //     if ( gridWord.length !== this.getWordLength(wordData.startCellId, isAcross) )
    //         throw new Error("Word length does not fit");
    // }

    // _makeGridWord(nativeWord) {
    //     return nativeWord.replace(/[ -]/g,"").toUpperCase();
    // }

    // _setGridWord(startCellId, gridWord, isAcross=true) {
    //     var coord = this._getCellCoord(startCellId), cellId;
    //     var startIndex = (isAcross) ? coord[1] : coord[0];
    //     for (var i = 0; i < gridWord.length; i++) {
    //         cellId = (isAcross) ? this._getCellId(coord[0], i+coord[1])
    //         $("#"+cellId)
    //     }
    // }
}
