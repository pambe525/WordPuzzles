class CrosswordEditor extends PuzzleEditor {

    /* THESE METHODS ARE IMPLEMENTED FROM PARENT PuzzleEditor CLASS*/
    _configureUIElements() {
        var sizeOptions = {5:"5x5", 7:"7x7", 9:"9x9", 11:"11x11", 13:"13x13", 15:"15x15"};
        this.setSizeSelector(sizeOptions, 15);
        $(this.IDs.sizeLable).text("Grid Size");
        $(this.IDs.symmToggle).prop("disabled", true);
        //$(this.IDs.modeToggle).bootstrapToggle({on: "Edit Clues", off: "Edit Blocks"});
    }

    _getPuzzleInstance(puzzleData) {
        if (puzzleData === undefined || puzzleData.id == null) {
            var gridSize = this.getSelectedSize();
            return new Crossword(gridSize);
        }
        else {
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

    // PRIVATE METHODS
    //--------------------------------------------------------------------------------------------------------------------
    _checkGridSizeOptionExists(gridSize) {
        if ($(this.IDs.sizeSelect + " option[value='" + gridSize + "']").length === 0)
            throw new Error("Invalid grid size in puzzle data");
    }

    _loadPuzzleData(puzzleData) {
        this.Xword.id = puzzleData.id;
        var indices = puzzleData.grid_blocks.split(","), index, cellId;
        for (var i = 0; i < Math.ceil(indices.length / 2); i++) {
            index = parseInt(indices[i]);
            cellId = Math.floor(index / puzzleData.grid_size) + "-" + (index % puzzleData.grid_size);
            this.Xword.toggleCellBlock(cellId);
        }
        var word, clue;
        for (cellId in puzzleData.across_words) {
            word = puzzleData.across_words[cellId].word;
            clue = puzzleData.across_words[cellId].clue;
            this.Xword.setWordData(cellId, word, clue, true);
        }
        for (cellId in puzzleData.down_words) {
            word = puzzleData.down_words[cellId].word;
            clue = puzzleData.down_words[cellId].clue;
            this.Xword.setWordData(cellId, word, clue, false);
        }
        this._dataSaved();
        $(this.IDs.deleteBtn).prop("disabled", false);
    }

    _puzzleClicked = (event) => {
        if (!$(this.IDs.modeToggle).is(":checked")) {
            this.puzzleInstance.toggleCellBlock(event.target.id);
            this._dataChanged();
        } else {
            this.puzzleInstance.toggleWordHilite(event.target.id);
            $(this.IDs.clueForm).show();
            this._setupClueForm(event.target.id);
        }
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
        //this._dataChanged();
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
            //this._dataChanged();
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
        //this._dataChanged();
    }

    _saveBtnClicked = () => {
        if (this.puzzleInstance.id === 0) $(this.IDs.deleteBtn).prop("disabled", false);
        var reqData = JSON.stringify(this.puzzleInstance.getGridData());
        $.ajax({
            method: "POST",
            data: {'action': 'save', 'data': reqData},
            dataType: "json",
            success: this._saveSuccess,
            error: this._ajaxResponseError
        });
    }

    _deleteBtnClicked = () => {
        var deleteData = true;
        var msg = "All saved data will be permanently deleted.";
        deleteData = confirm(msg);
        if (deleteData) {
            $.ajax({
                method: "POST",
                data: {'action': 'delete', 'id': this.puzzleInstance.id},
                dataType: "json",
                success: this._deleteSuccess,
                error: this._ajaxResponseError
            });
        }
    }

    // This is not unit tested
    _doneBtnClicked = () => {
        window.location.replace("/");
    }

    // This is not unit tested
    _handleUnload = (e) => {
        if (this.dataSaved) return;
        var msg = "Do you really want to leave this page?"
        if (e) e.returnValue = msg;
        return msg;
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

    _saveSuccessHandler = (result) => {
        if (result['error_message']) {
            alert(result['error_message']);
        } else {
            this.puzzleInstance.id = result.id;
            this._dataSaved();
        }
    }

    _deleteSuccessHandler = (result) => {
        this._dataSaved();
        window.location.replace("/");
    }

    _saveFailureHandler = (jqXHR, status, error) => {
        alert(error);
    }
    _deleteFailureHandler = (jqXHR, status, error) => {
        alert(error);
    }

    _dataChanged() {
        $(this.IDs.saveBtn).prop("disabled", false);
        this.dataSaved = false;
    }

    _dataSaved() {
        $(this.IDs.saveBtn).prop("disabled", true);
        this.dataSaved = true;
    }
}
