class XWordGrid {

    cellSize = 29;
    jqGridObj = null;
    size = 15;    /* default size */
    across = {};
    down = {};

    constructor(puzzleData, clickHandler) {
        if ( puzzleData.size !== undefined ) this.size = puzzleData.size;
        this._createGrid(clickHandler);
        if ( puzzleData.data !== undefined ) {
            this._loadBlocks(puzzleData.data.blocks);
            this._storeWordData(puzzleData.data);
        }
        this._autonumberGrid();
    }

    //** PUBLIC METHODS **//
    clearHilite() {
        $(this._getHilitedCells()).removeClass("xw-hilite");
    }
    getHilitedWordData() {
        let wordCells = this._getHilitedCells();
        let wordData = {};
        let clueNum = this._getHilitedClueNum();
        let isAcross = this._isHiliteAcross();
        let clueType = ( isAcross ) ? "Across" : "Down";
        let index = this._cellIndex(wordCells[0]);
        wordData.maxLength = wordCells.length;
        wordData.clueRef = "#" + clueNum + " " + clueType + " (" + wordData.maxLength + ")";
        if ( isAcross ) {
            wordData.clueWord = (this.across[index]) ? this.across[index].word : "";
            wordData.clueText = (this.across[index]) ? this.across[index].clue : "";
        } else {
            wordData.clueWord = (this.down[index]) ? this.down[index].word : "";
            wordData.clueText = (this.down[index]) ? this.down[index].clue : "";
        }
        return wordData;
    }
    getPuzzleHtml() {
        return this.jqGridObj;
    }
    getGridData() {
        let gridData = {blocks:[], across:this.across, down:this.down};
        let gridCells = this._getGridCells();
        for (let i = 0; i < gridCells.length; i++)
            if ( this._isBlocked(gridCells[i]) ) gridData.blocks.push(i);
        gridData.blocks = gridData.blocks.toString();
        return gridData;
    }
    getStatus() {
        let acrossClues = this._countTotalClues(true);
        let downClues = this._countTotalClues(false);
        let acrossDone = this._countDoneClues(true);
        let downDone = this._countDoneClues(false);
        let status = "ACROSS: " + acrossDone + " of " + acrossClues + ", ";
        status += "DOWN: " + downDone + " of " + downClues;
        return status;
    }
    hasBlocks() {
        return (this.jqGridObj.find(".xw-block").length > 0);
    }
    hasClues() {
        return ( Object.keys(this.across).length > 0 || Object.keys(this.down).length > 0 );
    }
    isComplete() {
        return this._countDoneClues() === this._countTotalClues() &&
               this._countDoneClues(false) === this._countTotalClues(false);
    }
    hiliteNextIncomplete() {
        let numberedCells = $(this._getGridCells()).has(".xw-number");
        let hiliteCells;
        for (let i = 0; i < numberedCells.length; i++) {
            if (this._isNextOpen(numberedCells[i])) {
                hiliteCells = this._getWordCells(numberedCells[i]);
                $(hiliteCells).addClass("xw-hilite");
                break;
            }
        }
    }
    removeHilitedWordData() {
        let hilitedCells = this._getHilitedCells();
        let isAcross = this._isHiliteAcross();
        for (let i = 0; i < hilitedCells.length; i++)
            $(hilitedCells[i]).children(".xw-letter").empty();
        let cellIndex = this._cellIndex(hilitedCells[0]);
        if (isAcross) delete this.across[cellIndex];
        else delete this.down[cellIndex];
    }
    setHilitedWordData(wordData) {
        let word = wordData.word.toUpperCase().trim();
        let clue = wordData.clue.trim();
        let hilitedCells = this._getHilitedCells();
        let isAcross = this._isHiliteAcross();
        this._checkWordFit(word, hilitedCells, isAcross);
        clue = this._checkAndFixClue(word, clue);
        for (let i = 0; i < hilitedCells.length; i++)
            $(hilitedCells[i]).children(".xw-letter").text(word[i]);
        let cellIndex = this._cellIndex(hilitedCells[0]);
        if (isAcross) this.across[cellIndex] = {word: word, clue: clue};
        else this.down[cellIndex] = {word: word, clue: clue};
        this._setToolTip(hilitedCells[0]);
        this._setLetterColors(hilitedCells, isAcross);
    }
    displayWordsInGrid() {
        let acrossKeys = Object.keys(this.across), word, index;
        let gridCells = this._getGridCells();
        for (const key of acrossKeys) {
            word = this.across[key].word.toUpperCase();
            index = key;
            for (let i = 0; i < word.length; i++)
                $(gridCells[index++]).children(".xw-letter").text(word[i]);
        }
    }
    toggleBlock(cell) {
        if ($(cell).prop("tagName") !== "DIV") return false;
        let symmCell = this._getSymmCell(cell);
        if (this._hasLetter(cell) || this._hasLetter(symmCell)) return false;
        this._toggleCellBlock(cell);
        if (cell !== symmCell) this._toggleCellBlock(symmCell);
        this._autonumberGrid();
        return true;
    }
    toggleHilite(cell) {
        if (this._isBlocked(cell)) return false;
        let isAcross = true;
        if ($(cell).hasClass("xw-hilite")) isAcross = !(this._isHiliteAcross());
        if ( !this._isInWord(cell, isAcross) ) isAcross = !isAcross;
        let wordCells = this._getWordCells(cell, isAcross);
        this.clearHilite();
        $(wordCells).addClass("xw-hilite");
        return true;
    }

    //** PRIVATE METHODS **//
    _autonumberGrid() {
        this.jqGridObj.find(".xw-number").remove();
        let clueNum = 1, cell;
        for (var i = 0; i < this.size*this.size; i++) {
            cell = this._gridCell(i);
            if (this._isWordStart(cell) || this._isWordStart(cell, false))
                this._setClueNum(cell, clueNum++);
        }
    }
    _cellIndex(cell) {
        return this.jqGridObj.children("div").index(cell);
    }
    _checkWordFit(word, hilitedCells, isAcross) {
        if (hilitedCells.length !== word.length)
            throw new Error("Word must be " + hilitedCells.length + " chars");
        if (!/^[A-Za-z]+$/.test(word)) throw new Error("Word must contain all letters");
        let gridLetter, wordStartCell;
        for (let i = 0; i < hilitedCells.length; i++) {
            gridLetter = $(hilitedCells[i]).children(".xw-letter").text();
            wordStartCell = this._getWordStartCell(hilitedCells[i], !isAcross);
            if (this._getWordData(wordStartCell, !isAcross) !== null && word[i] !== gridLetter)
                throw new Error("Word conflicts with existing letters");
        }
    }
    _checkAndFixClue(word, clue) {
        clue.trim();
        var numbers = clue.match(/\(([^)]*)\)[^(]*$/);  // extracts numbers in parenthesis
        if (numbers === null) {
            if (clue !== "") clue += " (" + word.length + ")";
        } else {
            numbers = numbers[1].split(/,| |-/);
            var parenSum = numbers.reduce((a, b) => parseInt(a) + parseInt(b), 0);
            if (parenSum !== word.length) throw new Error("Incorrect number(s) in parentheses at end of clue");
        }
        return clue;
    }
    _createGrid(clickHandler) {
        this.jqGridObj = $("<div></div>").addClass("xw-grid");
        let nCells = this.size * this.size, cellHtml = "";
        for (var i = 0; i < nCells; i++)
            cellHtml += "<div><span class='xw-letter'></span></div>"
        $(this.jqGridObj).html(cellHtml);
        this.jqGridObj.width(this.cellSize * this.size + 1)
            .height(this.cellSize * this.size + 1);
        $(this.jqGridObj).children("div").click(clickHandler)
            .children(".xw-letter").click(clickHandler);
    }
    _countTotalClues(isAcross=true){
        let numberedCells = $(this._getGridCells()).has(".xw-number");
        let count = 0, nextCellIsOpen, prevCellIsNotOpen;
        for (let i = 0; i < numberedCells.length; i++) {
            nextCellIsOpen = this._isNextOpen(numberedCells[i], isAcross);
            prevCellIsNotOpen = !this._isPrevOpen(numberedCells[i], isAcross);
            if ( nextCellIsOpen && prevCellIsNotOpen ) count++;
        }
        return count;
    }
    _countDoneClues(isAcross=true) {
        let clues = (isAcross) ? this.across : this.down;
        let keys = Object.keys(clues);
        let count = 0;
        for (const key of keys)
            if (clues[key].clue !== "") count++;
        return count;
    }
    _parseCellIndex(cellRef) {
        if (typeof(cellRef) === "number") return cellRef;
        if (!cellRef.includes("-")) return parseInt(cellRef);
        let coord = cellRef.split("-");
        return ( parseInt(coord[0])*this.size + parseInt(coord[1]) );
    }
    _getGridCells() {
        return this.jqGridObj.children("div");
    }
    _getHilitedCells() {
        return $(this._getGridCells()).filter(".xw-hilite");
    }
    _getHilitedClueNum() {
        return parseInt($(this._getHilitedCells()[0]).children(".xw-number").text());
    }
    _getSymmCell(cell) {
        let index = this._cellIndex(cell);
        let symmIndex = this.size * this.size - index - 1;
        return this._gridCell(symmIndex);
    }
    _getToolTipText(wordStartCell, isAcross=true) {
        let label = (isAcross) ? "Across" : "Down";
        let clueNum = parseInt($(wordStartCell).children(".xw-number").text());
        let wordData = this._getWordData(wordStartCell, isAcross);
        return (wordData === null || wordData.clue === "") ? "" : (clueNum + " " + label + ": " + wordData.clue);
    }
    _getWordCells(cell, isAcross=true) {
        let isLoneCell = !this._isNextOpen(cell, isAcross) && !this._isPrevOpen(cell, isAcross);
        if (this._isBlocked(cell) || isLoneCell) return null;
        let gridCells = this._getGridCells();
        let wordStartIndex = this._cellIndex(this._getWordStartCell(cell, isAcross));
        let wordEndIndex = this._cellIndex(this._getWordEndCell(cell, isAcross));
        let incr = (isAcross) ? 1: this.size;
        let wordCells = $();
        for (let i = wordStartIndex; i <= wordEndIndex; i += incr)
            wordCells = wordCells.add(gridCells[i]);
        return wordCells;
    }
    _getWordData(wordStartCell, isAcross) {
        let cellIndex = this._cellIndex(wordStartCell), wordData;
        if (isAcross) wordData = (this.across[cellIndex] === undefined) ?  null : this.across[cellIndex];
        else wordData = (this.down[cellIndex] === undefined) ? null : this.down[cellIndex];
        return wordData;
    }
    _getWordEndCell(cell, isAcross=true) {
        let gridCells = this._getGridCells();
        let cellIndex = this._cellIndex(cell);
        let incr = (isAcross) ? 1 : this.size;
        let currentCell = cell;
        while ( this._isNextOpen(currentCell, isAcross) ) {
            currentCell = gridCells[cellIndex + incr];
            cellIndex = this._cellIndex(currentCell);
        }
        return currentCell;
    }
    _getWordStartCell(cell, isAcross=true) {
        let gridCells = this._getGridCells();
        let cellIndex = this._cellIndex(cell);
        let incr = (isAcross) ? 1 : this.size;
        let currentCell = cell;
        while ( this._isPrevOpen(currentCell, isAcross) ) {
            currentCell = gridCells[cellIndex - incr];
            cellIndex = this._cellIndex(currentCell);
        }
        return currentCell;
    }
    _gridCell(index) {
        return this._getGridCells()[index];
    }
    _hasLetter(cell) {
        return ($(cell).children(".xw-letter").text() !== "");
    }
    _hasClue(wordStartCell, isAcross=true) {
        let hasClue;
        let cellIndex = this._cellIndex(wordStartCell);
        if (isAcross) hasClue = (this.across[cellIndex] !== undefined && this.across[cellIndex].clue !== "");
        else hasClue = (this.down[cellIndex] !== undefined && this.down[cellIndex].clue !== "");
        return hasClue;
    }
    _isBlocked(cell) {
        return !!($(cell).hasClass("xw-block"));
    }
    _isFirst(cellIndex, isAcross=true) {
        if ( isAcross && (cellIndex % this.size) === 0 ) return true;
        return !isAcross && (cellIndex < this.size);
    }
    _isHiliteAcross() {
        let hilitedCells = this._getHilitedCells();
        if (hilitedCells.length === 0) return null;
        let indexDiff = this._cellIndex(hilitedCells[1]) - this._cellIndex(hilitedCells[0]);
        return (indexDiff === 1);
    }
    _isInWord(cell, isAcross=true) {
       return ( this._isNextOpen(cell, isAcross) || this._isPrevOpen(cell, isAcross) );
    }
    _isLast(cellIndex, isAcross=true) {
        if ( isAcross && (cellIndex + 1) % this.size === 0 ) return true;
        return !isAcross && (cellIndex + this.size) >= this.size * this.size;
    }
    _isNextOpen(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell) ;
        if ( this._isLast(cellIndex, isAcross) ) return false;
        let nextCellIndex = (isAcross) ? cellIndex + 1 : cellIndex + this.size;
        return !this._isBlocked(this._gridCell(nextCellIndex));
    }
    _isPrevOpen(cell, isAcross=true) {
        let cellIndex = this._cellIndex(cell) ;
        if ( this._isFirst(cellIndex, isAcross) ) return false;
        let prevCellIndex = (isAcross) ? cellIndex - 1 : cellIndex - this.size;
        return !this._isBlocked(this._gridCell(prevCellIndex));
    }
    _isWordStart(cell, isAcross=true) {
        if (this._isBlocked(cell)) return false;
        return !(!this._isNextOpen(cell, isAcross) || this._isPrevOpen(cell, isAcross));
    }
    _loadBlocks(blocks) {
        let blockedIndices = blocks.split(",");
        let gridCells = this._getGridCells();
        for (var i = 0; i < blockedIndices.length; i++)
            $(gridCells[parseInt(blockedIndices[i])]).addClass("xw-block");
    }
    _setClueNum(cell, clueNum) {
        let span = $("<span></span>").addClass("xw-number").text(clueNum);
        $(cell).append(span);
    }
    _setToolTip(wordStartCell) {
        let acrossToolTip = this._getToolTipText(wordStartCell);
        let downToolTip = this._getToolTipText(wordStartCell, false);
        let wordBreak = (acrossToolTip !== "" && downToolTip !== "") ? "\n" : "";
        $(wordStartCell).prop("title", acrossToolTip + wordBreak + downToolTip);
    }
    _setLetterColors(wordCells, isAcross=true){
        let wordHasClue = this._hasClue(wordCells[0], isAcross);
        let letterIsInXWord, xwordStartCell, letter, isRed;
        if (!wordHasClue) $(wordCells).children(".xw-letter").addClass("xw-red");
        else {
            for (let i = 0; i < wordCells.length; i++) {
                isRed = false;
                letter = $(wordCells[i]).children(".xw-letter");
                letterIsInXWord = this._isInWord(wordCells[i], !isAcross);
                if ( letterIsInXWord ) {
                    xwordStartCell = this._getWordStartCell(wordCells[i], !isAcross);
                    if ( !this._hasClue(xwordStartCell, !isAcross) ) isRed = true;
                }
                (isRed) ? letter.addClass("xw-red") : letter.removeClass("xw-red");
            }
        }
    }
    _storeWordData(data) {
        let acrossKeys = (data.across) ? Object.keys(data.across) : [];
        let downKeys = (data.down) ? Object.keys(data.down) : [];
        for (const key of acrossKeys)
            this.across[this._parseCellIndex(key)] = data.across[key];
        for (const key of downKeys)
            this.down[this._parseCellIndex(key)] = data.down[key];
    }
    _toggleCellBlock(cell) {
        if ( $(cell).hasClass("xw-block") ) $(cell).removeClass("xw-block");
        else $(cell).addClass("xw-block");
    }
}
