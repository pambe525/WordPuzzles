class Crossword {

    cellSize = 30;
    clickHandler = null;
    words = {across: {}, down: {}};

    constructor(divId, clickHandler, gridSize) {
        this.puzzleId = 0;
        this.gridSize = gridSize;
        this.gridId = "#" + divId;
        this.clickHandler = clickHandler;
        this._validateArgs();
        this._makeGrid();
        this._setStyle();
    }

    hasBlocks() {
        return ($(".xw-blocked").length !== 0);
    }

    hasData() {
        var acrossWords = Object.keys(this.words.across).length;
        var downWords = Object.keys(this.words.down).length;
        return (this.hasBlocks() || acrossWords !== 0 || downWords !== 0);
    }

    getClueNum(cellId, isAcross = true) {
        return this._getCellNumber(this._getWordStartCellId(cellId, isAcross));
    }

    getFirstHilitedCellId() {
        var hilitedCells = $(this.gridId + ">.xw-hilited");
        return (hilitedCells.length === 0) ? null : hilitedCells[0].id;
    }

    getWordData(cellId, isAcross = true) {
        if (!this._isUnblockedCell(cellId)) return null;
        var startCellId = this._getWordStartCellId(cellId, isAcross);
        var key = (isAcross) ? "across" : "down";
        return (this.words[key][startCellId] === undefined) ? null : this.words[key][startCellId];
    }

    clearHilites() {
        $(this.gridId).children(".xw-hilited").removeClass("xw-hilited")
            .removeClass("xw-across").removeClass("xw-down");
    }

    setEditable(isEditable) {
        $(this.gridId).children('div').attr('contenteditable', (isEditable) ? "true" : "false");
    }

    setWordData(cellId, word, clue, isAcross = true) {
        if (!this._isUnblockedCell(cellId) || !this._isInWord(cellId, isAcross)) throw new Error("Invalid cell id");
        var wordCells = this._getCellsInWord(cellId, isAcross);
        this._checkWordFitToGrid(cellId, word, wordCells, isAcross);
        clue = this._checkAndFixClue(word, clue);
        var key = (isAcross) ? "across" : "down";
        var startCellId = this._getWordStartCellId(cellId, isAcross);
        this.words[key][startCellId] = {word: word, clue: clue};
        this._setGridWord(word, wordCells);
        this._setToolTip(startCellId, isAcross);
        this._setWordColor(startCellId, isAcross);
    }

    readWord(cellId, isAcross = true) {
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

    deleteWordData(cellId, isAcross=true) {
        var wordData = this.getWordData(cellId, isAcross);
        if ( !this._isUnblockedCell(cellId) || wordData === null ) return false;
        var key = (isAcross) ? "across" : "down";
        var startCellId = this._getWordStartCellId(cellId, isAcross);
        delete this.words[key][startCellId];
        var wordCells = this._getCellsInWord(cellId, isAcross);
        var xyColorClass = (isAcross) ? "xw-xblue" : "xw-yblue";
        for (var i = 0; i < wordCells.length; i++) {
            if ( !this.getWordData(wordCells[i].id, !isAcross) ) {
                $(wordCells[i]).children(".xw-letter").empty();
                $(wordCells[i]).children(".xw-letter").removeClass("xw-blue");
            }
            else $(wordCells[i]).children(".xw-letter").removeClass(xyColorClass);
        }
        this._setToolTip(startCellId, isAcross);
        return true;
    }

    isHiliteAcross() {
        var isAcross = false, hilitedCells = $(".xw-across");
        if (hilitedCells.length > 0) isAcross = true;
        else hilitedCells = $(".xw-down");
        return (hilitedCells.length === 0) ? null : isAcross;
    }

    hiliteNextIncomplete() {
        var currentFirstCellId = this.getFirstHilitedCellId(), cellId;
        var isAcross = this.isHiliteAcross();
        isAcross = (isAcross === null) ? true : isAcross;
        cellId = this._nextIncompleteWordFirstCellId(currentFirstCellId, isAcross);
        if (cellId === null) {
            isAcross = !isAcross;
            cellId = this._nextIncompleteWordFirstCellId(null, isAcross);
        }
        if (cellId !== null) this._hiliteCellsInWord(cellId, isAcross);
        else this.clearHilites();
    }

    toggleCellBlock(cellId) {
        if (cellId === null || $("#" + cellId).length === 0 || this._hasText(cellId)) return false;
        var symmCellId = this._getSymmetricCellId(cellId);
        if (this._isBlockedCell(cellId) &&
            (this._hasInlineLetterInNeighbor(cellId) || this._hasInlineLetterInNeighbor(symmCellId))) return false;
        this._toggleBlock(cellId);
        if (cellId !== symmCellId) this._toggleBlock(symmCellId);
        this._autoNumberCells();
        return true;
    }

    toggleWordHilite(cellId) {
        if (this._isBlockedCell(cellId)) return null;
        var jqCellId = "#" + cellId, isAcross = null;
        if (!$(jqCellId).hasClass("xw-hilited")) {
            if (this._isWordStart(cellId, true)) isAcross = true;
            else if (this._isWordStart(cellId, false)) isAcross = false;
            else if (this._isInWord(cellId, true)) isAcross = true;
            else if (this._isInWord(cellId, false)) isAcross = false;
            this._hiliteCellsInWord(cellId, isAcross);
        } else {
            if ( $(jqCellId).hasClass("xw-across") ) isAcross = !this._isInWord(cellId, false);
            else isAcross = this._isInWord(cellId, true);
            this._hiliteCellsInWord(cellId, isAcross);
        }
        return isAcross;
    }

    getGridData() {
        var blocks = [], cells = $(this.gridId+">div");
        for (var i = 0; i < cells.length; i++)
            if ($(cells[i]).hasClass("xw-blocked")) blocks.push(i);
        blocks = blocks.toString();
        var dataObj = { puzzle_id: this.puzzleId, grid_size: this.gridSize, is_ready: this._isComplete(),
                        content: {blocks:blocks, words: this.words} };
        return dataObj;
    }

    // PRIVATE METHODS
    //--------------------------------------------------------------------------------------------------------------------
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

    _createGridCell(row, col) {
        var cellId = this._getCellId(row, col);
        var cell = $("<div><span class='xw-letter'></span></div>");
        cell.on("click", this.clickHandler).attr('id', cellId).attr('contenteditable', 'false');
        $(cell).children(".xw-letter").on("click", this.clickHandler);
        return cell;
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

    _nextIncompleteWordFirstCellId(currentFirstCellId, isAcross=true) {
        var currentCellIndex = 0;
        if (currentFirstCellId !== null) currentCellIndex = this.getClueNum(currentFirstCellId, isAcross);
        var numberedCells = $(".xw-number").parent();
        var nextCellIndex, nextCellId;
        for (var i = 0; i < numberedCells.length; i++) {
            nextCellIndex = (i + currentCellIndex) % numberedCells.length;
            nextCellId = numberedCells[nextCellIndex].id;
            if (this._isWordStart(nextCellId, isAcross) && !this._hasToolTip(nextCellId, isAcross)) return nextCellId;
        }
        return null;
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
            "text-align:center;}";
        css += ".xw-hilited {background-color:yellow}";
        css += ".xw-letter {font-size:16px; pointer-events:none; color: red; font-weight:bold}";
        css += ".xw-letter.xw-blue, .xw-letter.xw-xblue.xw-yblue {color:blue;}"
        var styleTag = "<style id='xw-style' type='text/css'></style>";
        $(styleTag).html(css).appendTo("head");
    }

    _setNumberOnCell(id, number) {
        var cellNumber = $("<span></span>").text(number);
        cellNumber.addClass("xw-number");
        $("#" + id).append(cellNumber);
    }

    _setToolTip(startCellId, isAcross) {
        var wordDataA = (this._isWordStart(startCellId, true)) ? this.getWordData(startCellId, true) : null;
        var wordDataD = (this._isWordStart(startCellId, false)) ? this.getWordData(startCellId, false) : null;
        var toolTipText="";
        if (wordDataA) toolTipText = this._getToolTipText(startCellId, wordDataA.clue, true);
        if (wordDataD) toolTipText += this._getToolTipText(startCellId, wordDataD.clue, false);
        $("#" + startCellId).prop("title", toolTipText);
    }

    _setGridWord(word, wordCells) {
        var gridWord = word.toUpperCase();
        for (var i = 0; i < gridWord.length; i++)
            $(wordCells[i]).children(".xw-letter").text(gridWord[i]);
    }

    // NOT CURRENTLY USED - MAY NEED WORK TO HANDLE TAB & SHIFT-TAB **/
    //--------------------------------------------------------------------------------------------------------------------

    _onKeyDown = (event) => {
        var cellId = event.target.id, jqCellId = "#" + cellId;
        event.preventDefault();
        if (event.keyCode >= 65 && event.keyCode <= 90) {
            $(jqCellId).html($(jqCellId).children());  // Deletes existing letter but leaves number intact
            $(jqCellId).nextAll(".xw-hilited").first().focus();
            $(jqCellId).append(String.fromCharCode(event.keyCode)).addClass("xw-letter");
        } else if (event.keyCode === 8) {
            if (!$.isNumeric($(jqCellId).text())) $(jqCellId).html($(jqCellId).children());
            else $(jqCellId).prevAll(".xw-hilited").first().focus();
        } else if (event.keyCode === 9) {
        } else if (event.shiftKey && event.keyCode === 9) {
        }
    }

    _getCellId(row, col) {
        return (row + "-" + col);
    }

    _getSymmetricCellId(cellId) {
        var coord = cellId.split("-");
        var symmRow = this.gridSize - parseInt(coord[0]) - 1;
        var symmCol = this.gridSize - parseInt(coord[1]) - 1;
        return this._getCellId(symmRow, symmCol);
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

    _getCellNumber(cellId) {
        if (cellId === null) return 0;
        var cellNumText = $("#" + cellId + "> .xw-number").text();
        return (cellNumText) ? parseInt(cellNumText) : 0;
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

    _getCellsInWord(cellId, isAcross = true) {
        var startCoord = this._getCellCoord(this._getWordStartCellId(cellId, isAcross));
        var endCoord = this._getCellCoord(this._getWordEndCellId(cellId, isAcross));
        var selector = (isAcross) ? "[id^='" + startCoord[0] + "-']" : "[id$='-" + startCoord[1] + "']";
        var inlineCells = $(this.gridId + " > " + selector);
        var startCellIndex = (isAcross) ? startCoord[1] : startCoord[0];
        var endCellIndex = (isAcross) ? endCoord[1] : endCoord[0];
        return inlineCells.slice(startCellIndex, endCellIndex + 1);
    }

    _getToolTipText(firstCellId, clue, isAcross) {
        var label = (isAcross) ? "Across" : "Down";
        var clueNum = this._getCellNumber(firstCellId);
        var toolTipText = (clue !== "") ? (clueNum + " " + label + ": " + clue) : "";
        if (label === "Across" && toolTipText !== "") toolTipText += "\n";
        return toolTipText;
    }

    _hasInlineLetterInNeighbor(cellId) {
        var coords = [[0, 1], [0, -1], [1, 0], [-1, 0]], neighborId, isAcross;
        for (var index in coords) {
            neighborId = this._getOffsetCellId(cellId, coords[index][0], coords[index][1]);
            isAcross = (index <= 1);
            if ( this.getWordData(neighborId, isAcross) ) return true;
        }
        return false;
    }

    _hasText(cellId) {
        return (!this._isUnblockedCell(cellId)) ? false : ($("#" + cellId + "> .xw-letter").text() !== "");
    }

    _hasToolTip(cellId, isAcross=true) {
        var toolTip = $("#"+cellId).prop("title");
        var label = (isAcross) ? " Across:" : " Down:";
        if (toolTip.trim().length === 0) return false;
        return (toolTip.includes(label));
    }

    _hiliteCellsInWord(cellId, isAcross = true) {
        this.clearHilites();
        if (cellId === null) return;
        var cellsToHilite = this._getCellsInWord(cellId, isAcross);
        var classLabel = (isAcross) ? "xw-across" : "xw-down";
        if (cellsToHilite.length > 1) cellsToHilite.addClass("xw-hilited").addClass(classLabel);
    }

    _isBlockedCell(cellId) {
        if (cellId === null) return true;
        return !!($("#" + cellId).hasClass("xw-blocked"));
    }

    _isWordStart(cellId, isAcross = true) {
        if (this._isBlockedCell(cellId)) return false;
        var prevCellId = (isAcross) ? this._getOffsetCellId(cellId, 0, -1) : this._getOffsetCellId(cellId, -1, 0);
        var nextCellId = (isAcross) ? this._getOffsetCellId(cellId, 0, 1) : this._getOffsetCellId(cellId, 1, 0);
        return (!this._isUnblockedCell(prevCellId) && this._isUnblockedCell(nextCellId));
    }

    _isWithinGrid(row, col) {
        return !(row < 0 || row >= this.gridSize || col < 0 || col >= this.gridSize);
    }

    _isUnblockedCell(cellId) {
        if (cellId === null) return false;
        var coord = this._getCellCoord(cellId);
        return !(this._isBlockedCell(cellId) || !this._isWithinGrid(coord[0], coord[1]));
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

    _isComplete() {
        if ( $(this.gridId+">div>.xw-letter:empty").length !== 0 ) return false;
        else {
            var cells = $(this.gridId+">div").has(".xw-number");
            for (var i = 0; i < cells.length; i++) {
                if (this._isWordStart(cells[i].id, true) && (this.words.across[cells[i].id] === undefined ||
                    this.words.across[cells[i].id].clue === "")) return false;
                if (this._isWordStart(cells[i].id, false) && (this.words.down[cells[i].id] === undefined ||
                    this.words.down[cells[i].id].clue === "")) return false;
            }
            return true;
        }
    }

    _checkWordFitToGrid(cellId, word, wordCells, isAcross = true) {
        if (!/^[A-Za-z]+$/.test(word)) throw new Error("Word must contain all letters");
        if (word.length !== wordCells.length) throw new Error("Word must be " + wordCells.length + " chars");
        var allCapsWord = word.toUpperCase(), gridLetter;
        for (var i = 0; i < wordCells.length; i++) {
            gridLetter = $(wordCells[i]).children(".xw-letter").text();
            if (this.getWordData(wordCells[i].id, !isAcross) !== null && allCapsWord[i] !== gridLetter)
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

    _setWordColor(cellId, isAcross=true) {
        var wordData = this.getWordData(cellId, isAcross), colorFlag = false;
        if (wordData && wordData["clue"] !== "") colorFlag = true;
        var cells = this._getCellsInWord(cellId, isAcross);
        var isXYCell, xyColorClass = (isAcross) ? "xw-xblue" : "xw-yblue";
        for (var i = 0; i < cells.length; i++) {
            isXYCell = !!(this._isInWord(cells[i].id, !isAcross));
            if (!isXYCell && colorFlag) $(cells[i]).children("span.xw-letter").addClass("xw-blue");
            else if (!isXYCell && !colorFlag) $(cells[i]).children("span.xw-letter").removeClass("xw-blue");
            else if (isXYCell && colorFlag) $(cells[i]).children("span.xw-letter").addClass(xyColorClass);
            else $(cells[i]).children("span.xw-letter").removeClass(xyColorClass);
        }
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
}

