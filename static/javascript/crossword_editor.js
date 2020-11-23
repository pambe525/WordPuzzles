class CrosswordEditor extends PuzzleEditor {

    /* THESE METHODS ARE IMPLEMENTED FROM PARENT PuzzleEditor CLASS*/
    _configureUIElements() {
        var sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15"};
        this.setSizeSelector(sizeOptions, 15);
        $(this.IDs.sizeLable).text("Grid Size");
        $(this.IDs.symmToggle).prop("disabled", true);
        //$(this.IDs.modeToggle).bootstrapToggle({on: "Edit Clues", off: "Edit Blocks"});
    }

    _getPuzzleInstance(puzzleData) {
        if (puzzleData === undefined || puzzleData.id == null) {
            var gridSize = this.getSelectedSize();
            return new Crossword(gridSize);
        } else {
            this._checkGridSizeOptionExists(puzzleData.size);
            $(this.IDs.sizeSelect).val(puzzleData.size);
            return new Crossword(puzzleData);
        }
    }

    _sizeSelectionChanged = () => {
        var changeGrid = true;
        if (this.puzzleInstance.hasData()) {
            var msg = "All changes to grid will be cleared. Please confirm or cancel."
            changeGrid = confirm(msg);
        }
        if (changeGrid) this._changeGridSize();
        else $(this.IDs.sizeSelect).val(this.puzzleInstance.size);
        $(this.IDs.modeToggle).prop("checked", false);   // Switch mode selector to default
    }

    _puzzleClicked = (event) => {
        if (!$(this.IDs.modeToggle).is(":checked")) {
            this.puzzleInstance.toggleCellBlock(event.target.id);
        } else {
            this.puzzleInstance.toggleWordHilite(event.target.id);
            $(this.IDs.clueForm).show();
            this._setupClueForm(event.target.id);
        }
    }
    _modeSelectionChanged = () => {
        //this._setModeHelpText();
        this._setWidgetStates();
    }

    _updateWordDataClicked = () => {
        var word = $(this.IDs.clueWord).val();
        var clue = $(this.IDs.clueText).val().replace(/\n/g, "");
        var cellId = this.puzzleInstance.getFirstHilitedCellId();
        var isAcross = this.puzzleInstance.isHiliteAcross();
        try {
            $(this.IDs.clueMsg).text("");
            this.puzzleInstance.setWordData(cellId, word, clue, isAcross);
            this._hiliteNextAndLoadForm();
        } catch (err) {
            $(this.IDs.clueMsg).text(err.message);
        }
    }

    _deleteWordDataClicked = () => {
        var cellId = this.puzzleInstance.getFirstHilitedCellId();
        var isAcross = this.puzzleInstance.isHiliteAcross();
        this.puzzleInstance.deleteWordData(cellId, isAcross);
        $(this.IDs.clueWord).val("");
        $(this.IDs.clueText).val("");
        $(this.IDs.clueMsg).text("");
    }

    // PRIVATE METHODS
    //--------------------------------------------------------------------------------------------------------------------
    _checkGridSizeOptionExists(gridSize) {
        if ($(this.IDs.sizeSelect + " option[value='" + gridSize + "']").length === 0)
            throw new Error("Invalid grid size in puzzle data");
    }

    _setWidgetStates() {
        var editMode = $(this.IDs.modeToggle).is(":checked");
        if (!editMode) {
            $(this.IDs.clueForm).hide();
            this.puzzleInstance.clearHilites();
        } else {
            $(this.IDs.clueForm).show();
            this._hiliteNextAndLoadForm();
        }
    }

    _changeGridSize() {
        this.puzzleInstance = this._getPuzzleInstance(this.getSelectedSize());
        this._setupPuzzleEventHandlers();
        this.puzzleInstance.show(this.puzzleDivId);
        this._setWidgetStates();
        this._dataChangedHandler();
    }

    _hiliteNextAndLoadForm() {
        this.puzzleInstance.hiliteNextIncomplete();
        var cellId = this.puzzleInstance.getFirstHilitedCellId();
        if (cellId === null) $(this.IDs.clueForm).hide();
        else this._setupClueForm(cellId);
    }

    _getClueRefText(clueNum, maxLength, isAcross) {
        var label = (isAcross) ? "Across" : "Down";
        return ("#" + clueNum + " " + label + " (" + maxLength + ")");
    }

    _setupClueForm(cellId) {
        var isAcross = this.puzzleInstance.isHiliteAcross();
        var formFields = this._gatherClueFormData(cellId, isAcross);
        $(this.IDs.clueNum).text(formFields.clueRef);
        $(this.IDs.clueWord).val(formFields.word);
        $(this.IDs.clueText).val(formFields.clue);
        $(this.IDs.clueWord).attr("maxlength", formFields.maxLength);
        $(this.IDs.clueMsg).text("");
        (formFields.word === "") ? $(this.IDs.clueWord).focus() : $(this.IDs.clueText).focus()
    }

    _gatherClueFormData(cellId, isAcross) {
        var formFields = {clueRef: null, word: "", clue: "", maxLength: null};
        var gridWord = this.puzzleInstance.readWord(cellId, isAcross);
        formFields.maxLength = gridWord.length;
        formFields.clueNum = this.puzzleInstance.getClueNum(cellId, isAcross);
        formFields.clueRef = this._getClueRefText(formFields.clueNum, formFields.maxLength, isAcross);
        var wordData = this.puzzleInstance.getWordData(cellId, isAcross);
        if (wordData === null) {
            gridWord = gridWord.replaceAll(" ", "");
            if (gridWord.length === formFields.maxLength) formFields.word = gridWord;
        } else {
            formFields.word = wordData.word;
            formFields.clue = wordData.clue;
        }
        return formFields;
    }

    /* EVENT HANDLERS */
    // _setModeHelpText() {
    //     var msg;
    //     var editMode = $(this.IDs.selectMode).is(":checked");
    //     if (!editMode)
    //         msg = "Click on a grid square to block it. Re-select to unblock. Diametrically opposite square " +
    //             "will also be blocked or unblocked using 180 deg. rotational symmetry.";
    //     else
    //         msg = "Click on a square to toggle editing ACROSS or DOWN word and its clue. Clicking ENTER in " +
    //             "the clue form updates the word & clue in grid.  Valid clue is shown as a tooltip in the grid " +
    //             "square. RED letters indicare missing clues.  BLUE letters indicate clue is complete.";
    //     $(this.IDs.modeTip).text(msg);
    // }
}
