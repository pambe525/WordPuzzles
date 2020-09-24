class Crossword {

    cellSize = 30;
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

    getWordLength(cellId, isAcross=true) {
        if ( !this._isUnblockedCell(cellId) ) return 0;
        var beginCoord = this._getCellCoord( this._getWordStartCellId(cellId, isAcross) );
        var endCoord   = this._getCellCoord( this._getWordEndCellId(cellId, isAcross) );
        var index = (isAcross) ? 1 : 0;
        return (endCoord[index]-beginCoord[index]+1);
     }

     getClueNum(cellId, isAcross=true) {
        return this._getCellNumber(this._getWordStartCellId(cellId, isAcross));
     }

     getWordData(cellId, isAcross=true) {
        if (this.getWordLength(cellId) <= 1) return null;
        var wordStartCellId = this._getWordStartCellId(cellId, isAcross);
        var wordsDict = (isAcross) ? this.words.across : this.words.down;
        if ( wordsDict[wordStartCellId] === undefined ) return {startCellId: wordStartCellId, word:"",clue:""};
        var resultObj = wordsDict[wordStartCellId];
        resultObj.startCellId = wordStartCellId;
        return resultObj;
     }

     setWordData(wordData, isAcross=true) {
        this._checkWordData(wordData, isAcross);
        wordData.startCellId = this._getWordStartCellId(wordData.startCellId, isAcross)
        var wordsDict = (isAcross) ? this.words.across : this.words.down;
        wordsDict[wordData.startCellId] = {word: wordData.word, clue: wordData.clue};
        var gridWord = this._makeGridWord(wordData.word);
        //this._setGridWord(cellId, isAcross);
        return true;
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
        css += this.gridId + " > div { width:" + this.cellSize + "px; height:" + this.cellSize + "px;" +
            "border:1px solid black; float:left; position: relative }";
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
        return $("#"+cellId + "> .xw-number").text();
    }

    _getWordStartCellId(cellId, isAcross=true) {
        var newId = cellId, beginCellId;
        var rowOffset = (isAcross) ? 0 : -1;
        var colOffset = (isAcross) ? -1 : 0;
        do {
            beginCellId = newId;
            newId = this._getOffsetCellId(beginCellId,rowOffset,colOffset)

        } while ( this._isUnblockedCell(newId) );
        return beginCellId;
    }

    _getWordEndCellId(cellId, isAcross=true) {
        var newId = cellId, endCellId;
        var rowOffset = (isAcross) ? 0 : 1;
        var colOffset = (isAcross) ? 1 : 0;
        do {
            endCellId = newId;
            newId = this._getOffsetCellId(endCellId,rowOffset,colOffset)
        } while ( this._isUnblockedCell(newId) );
        return endCellId;
    }

    _checkWordData(wordData, isAcross=true) {
        if ( wordData.word === "" ) throw new Error("Word cannot be blank");
        if ( !wordData.word.match(/^[a-z- ]+$/i) ) throw new Error("Word must contain letters only");
        var gridWord = this._makeGridWord(wordData.word)
        if ( gridWord.length !== this.getWordLength(wordData.startCellId, isAcross) )
            throw new Error("Word length does not fit");
    }

    _makeGridWord(nativeWord) {
        return nativeWord.replace(/[ -]/g,"").toUpperCase();
    }

    // _setGridWord(startCellId, gridWord, isAcross=true) {
    //     var coord = this._getCellCoord(startCellId), cellId;
    //     var startIndex = (isAcross) ? coord[1] : coord[0];
    //     for (var i = 0; i < gridWord.length; i++) {
    //         cellId = (isAcross) ? this._getCellId(coord[0], i+coord[1])
    //         $("#"+cellId)
    //     }
    // }
}
