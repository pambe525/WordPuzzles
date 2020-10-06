class Crossword {

    cellSize = 30;
    clickHandler = null;
    words = {across:{}, down:{}};

    constructor(divId, clickHandler, gridSize) {
        this.gridSize = gridSize;
        this.gridId = "#" + divId;
        this.clickHandler = clickHandler;
        this._validateArgs();
        this._makeGrid();
        this._setStyle();
    }

    toggleCellBlock(cellId) {
        if (cellId === null || $("#"+cellId).length === 0 || this._hasText(cellId)) return false;
        var symmCellId = this._getSymmetricCellId(cellId);
        if ( this._isBlockedCell(cellId) &&
            (this._hasLetterInNeighbor(cellId) || this._hasLetterInNeighbor(symmCellId)) ) return false;
        this._toggleBlock(cellId);
        if (cellId !== symmCellId) this._toggleBlock(symmCellId);
        this._autoNumberCells();
        return true;
    }

    hasBlocks() {
        return ($(".xw-blocked").length !== 0);
    }

    getClueNum(cellId, isAcross = true) {
        return this._getCellNumber(this._getWordStartCellId(cellId, isAcross));
    }

    toggleWordHilite(cellId) {
        if (this._isBlockedCell(cellId)) return null;
        var jqCellId = "#"+cellId, isAcross = null;
        if ( !$(jqCellId).hasClass("xw-hilited") ) {
            if (this._isWordStart(cellId, true)) isAcross = true;
            else if (this._isWordStart(cellId, false)) isAcross = false;
            else if (this._isInWord(cellId, true)) isAcross = true;
            else if (this._isInWord(cellId, false)) isAcross = false;
            this._hiliteCellsInWord(cellId, isAcross);
        } else {
            if( $(jqCellId).hasClass("xw-across") && this._isInWord(cellId, false) ) isAcross = false;
            else if ( $(jqCellId).hasClass("xw-down") && this._isInWord(cellId, true) ) isAcross = true;
            this._hiliteCellsInWord(cellId, isAcross);
        }
        return isAcross;
    }

    clearHilites() {
        $(this.gridId).children(".xw-hilited").removeClass("xw-hilited")
            .removeClass("xw-across").removeClass("xw-down");
    }

    setEditable(isEditable) {
        $(this.gridId).children('div').attr('contenteditable', (isEditable) ? "true" : "false");
    }

    readWord(cellId, isAcross=true) {
        if (!this._isUnblockedCell(cellId) || !this._isInWord(cellId, isAcross)) return null;
        var cells = this._getCellsInWord(cellId, isAcross)
        var word = "", letter;
        for (var i = 0; i < cells.length; i++) {
            letter = $(cells[i]).children(".xw-letter").text();
            if (letter === "") letter = " ";
            word += letter;
        }
        return word;
    }

    getWordData(cellId, isAcross=true) {
        if ( !this._isUnblockedCell(cellId) ) return null;
        var startCellId = this._getWordStartCellId(cellId, isAcross);
        var key = (isAcross) ? "across" : "down";
        return (this.words[key][startCellId] === undefined) ? null : this.words[key][startCellId];
    }

    setWordData(cellId, word, clue, isAcross=true) {
        if ( !this._isUnblockedCell(cellId) || !this._isInWord(cellId, isAcross) ) throw new Error("Invalid cell id");
        var wordCells = this._getCellsInWord(cellId, isAcross);
        this._checkWordFitToGrid(cellId, word, wordCells, isAcross);
        clue = this._checkAndFixClue(word, clue);
        var key = (isAcross) ? "across" : "down";
        var startCellId = this._getWordStartCellId(cellId, isAcross);
        this.words[key][startCellId] = {word:word, clue:clue};
        this._setGridWord(word, wordCells);
        this._setToolTip(cellId, isAcross);
    }

    getFirstHilitedCellId() {
        var hilitedCells = $(this.gridId+">.xw-hilited");
        return (hilitedCells.length === 0) ? null : hilitedCells[0].id;
    }

    isHiliteAcross() {
        var isAcross = false;
        var hilitedCells = $(this.gridId+">.xw-across");
        if (hilitedCells.length > 0) isAcross = true;
        return (hilitedCells.length === 0) ? null : isAcross;
    }

    //--------------------------------------------------------------------------------------------------------------------
    // PRIVATE METHODS
    //
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
            "border-right:1px solid black; border-bottom:1px solid black; float:left; position: relative;"+
            "text-align:center;}";
        css += ".xw-hilited {background-color:yellow}";
        css += ".xw-letter {font-size:16px;}; .xw-red {font-weight:bold; color:red;}"
        //css += this.gridId + " > div:focus {background-color: #FFFF99; text-align:center}"
        var styleTag = "<style id='xw-style' type='text/css'></style>";
        $(styleTag).html(css).appendTo("head");
    }

    _getCellId(row, col) {
        return (row + "-" + col);
    }

    _createGridCell(row, col) {
        var cellId = this._getCellId(row, col);
        var cell = $("<div><span class='xw-letter'></span></div>");
        cell.on("click", this.clickHandler).attr('id', cellId).attr('contenteditable','false');
        $(cell).children(".xw-letter").on("click", this.clickHandler);
        return cell;
    }

    /** NOT CURRENTLY USED - MAY NEED WORK TO HANDLE TAB & SHIFT-TAB **/
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
        if (this._isBlockedCell(cellId))
            $(jqCellId).removeClass("xw-blocked");
        else {
            $(jqCellId).addClass("xw-blocked");
            $(jqCellId + " > .xw-number").remove();
        }
    }

    _hasLetterInNeighbor(cellId) {
        var coords = [[0,1],[0,-1],[1,0],[-1,0]], neighborId;
        for (var index in coords) {
            neighborId = this._getOffsetCellId(cellId, coords[index][0], coords[index][1]);
            if (this._hasText(neighborId)) return true;
        }
        return false;
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
        return ( !this._isUnblockedCell(cellId) ) ? false : ($("#"+cellId+"> .xw-letter").text() !== "");
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

    _checkWordFitToGrid(cellId, word, wordCells, isAcross=true) {
        if ( !/^[A-Za-z]+$/.test(word) ) throw new Error("Word must contain all letters");
        if (word.length !== wordCells.length) throw new Error("Word must be "+wordCells.length+" chars");
        var allCapsWord = word.toUpperCase(), gridLetter;
        for (var i = 0; i < wordCells.length; i++ ) {
            gridLetter = $(wordCells[i]).children(".xw-letter").text();
            if ( this.getWordData(wordCells[i].id, !isAcross) !== null && allCapsWord[i] !== gridLetter )
                throw new Error("Word conflicts with existing letters");
        }
        return true;
    }

    _checkAndFixClue(word, clue) {
        clue.trim();
        var numbers = clue.match(/\(([^)]*)\)[^(]*$/);
        if (numbers === null) {
            if (clue !== "") clue += " (" + word.length + ")";
        } else {
            numbers = numbers[1].split(/,| |-/);
            var parenSum = numbers.reduce((a, b) => parseInt(a) + parseInt(b), 0);
            if (parenSum !== word.length) throw new Error("Incorrect number(s) in parentheses at end of clue");
        }
        return clue;
    }

    _setGridWord(word, wordCells) {
        var gridWord = word.toUpperCase();
        for (var i = 0; i < gridWord.length; i++)
            $(wordCells[i]).children(".xw-letter").text(gridWord[i]);
    }

    _setToolTip(cellId, isAcross) {
        var firstCellId = this._getWordStartCellId(cellId, isAcross);
        var wordDataA = this.getWordData(cellId, true);
        var wordDataD = this.getWordData(cellId, false);
        var toolTipText;
        if (wordDataA !== null) toolTipText = this._getToolTipText(firstCellId, wordDataA.clue, true);
        if (wordDataD !== null) toolTipText += this._getToolTipText(firstCellId, wordDataD.clue, false);
        $("#"+firstCellId).prop("title", toolTipText);
    }

    _getToolTipText(firstCellId, clue, isAcross) {
        var label = (isAcross) ? "Across" : "Down";
        var clueNum = this.getClueNum(firstCellId);
        return (clue !== "") ? (clueNum + " " + label + ": " + clue + "\n") : "";
    }
}

