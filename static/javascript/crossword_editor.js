class CrosswordEditor {

    IDs = { grid:null, selectSize:'#grid-size', resetBtn:'#reset-grid', selectMode:'#edit-mode',
            modeTip:'#mode-tip', saveBtn:'#save-grid', clueForm:'#clue-form', clueNum:'#clue-num',
            clueWord:'#clue-word', clueHint:'#clue-hint', clueText:'#clue-text', clueMsg:'#clue-msg',
            clueUpdateBtn:'#clue-update', clueDeleteBtn:"#clue-delete"
    };
    gridId = "xw-grid";

    constructor(gridId) {
        this.gridId = gridId;
        this.IDs.grid = "#"+gridId;
    }

    initialize() {
        for (var key in this.IDs)
            if ($(this.IDs[key]).length === 0) throw new Error(this.IDs[key] + " does not exist");
        this._createNewCrossword();
        this._setupHandlers();
        this._setModeHelpText();
        this._setWidgetStates();
        $(this.IDs.clueWord).css("text-transform","uppercase");
    }

    setElementId(elemRef, elemId) {
        if (this.IDs[elemRef] === undefined) throw new Error("Invalid element reference " + elemRef);
        if ($("#"+elemId).length === 0) throw new Error("Element id " + elemId + " not found");
        this.IDs[elemRef] = elemId;
    }

    // PRIVATE FUNCTIONS
    //--------------------------------------------------------------------------------------------------------------------
    #_createNewCrossword() {
        var gridSize = parseInt($(this.IDs.selectSize).val());
        this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
    }

    #_cellClicked = (event) => {
        if ( parseInt($(this.IDs.selectMode).val() ) === 1) {
            this.Xword.toggleCellBlock(event.target.id);
            this._setWidgetStates();
        } else {
            this.Xword.toggleWordHilite(event.target.id);
            $(this.IDs.clueForm).show();
            this._setupClueForm(event.target.id);
       }
    }

    #_setupHandlers() {
        $(this.IDs.selectSize).change(this._sizeSelectionChanged);
        $(this.IDs.selectMode).change(this._modeSelectionChanged);
        $(this.IDs.resetBtn).click(this._resetBtnClicked);
        $(this.IDs.saveBtn).click(this._saveBtnClicked);
        $(this.IDs.clueUpdateBtn).click(this._updateWordDataClicked);
        $(this.IDs.clueDeleteBtn).click(this._deleteWordDataClicked)
        $(this.IDs.clueWord).keyup(this._onEnterKey);
        $(this.IDs.clueText).keyup(this._onEnterKey);
    }

    #_onEnterKey = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            $(this.IDs.clueUpdateBtn).click();
        }
    }

    #_setModeHelpText() {
        var msg;
        var selectMode = parseInt($(this.IDs.selectMode).val());
        if (selectMode === 1)
            msg = "Click on a grid square to block it. Re-select to unblock. " +
                "Diametrically opposite square will also be blocked using 180 deg. rotational symmetry.";
        else
            msg = "Click on a numbered square to edit ACROSS or DOWN word and its clue. " +
            "Clicking ENTER in the clue form updates the word & clue in grid.  Valid clue is shown as a tooltip "+
            "in the grid square.  RED letters indicare missing clues.  BLUE letters indicate clue is complete.";
        $(this.IDs.modeTip).text(msg);
    }

    #_setWidgetStates() {
        if ( this.Xword.hasData() ) {
            $(this.IDs.selectSize).prop("disabled", true);
            $(this.IDs.resetBtn).prop("disabled", false);
        } else {
            $(this.IDs.selectSize).prop("disabled", false);
            $(this.IDs.resetBtn).prop("disabled", true);
        }
        var editModeSelection = parseInt($(this.IDs.selectMode).val());
        if ( editModeSelection === 1 ) {
            $(this.IDs.clueForm).hide();
            this.Xword.clearHilites();
        } else if ( editModeSelection === 2 ) {
            $(this.IDs.clueForm).show();
            this._hiliteNextAndLoadForm();
        }
   }

    #_sizeSelectionChanged = () => {
        var gridSize = parseInt($(this.IDs.selectSize).val());
        this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
        $(this.IDs.selectMode).val(1);
        this._setWidgetStates();
    }

    _modeSelectionChanged = () => {
        this._setModeHelpText();
        this._setWidgetStates();
    }

    #_resetBtnClicked = () => {
        var msg = "All changes to grid will be cleared. Please confirm or cancel."
        if ( confirm(msg) ) {
            var gridSize = parseInt($(this.IDs.selectSize).val());
            this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
            this._setWidgetStates();
        }
    }

    #_updateWordDataClicked = () => {
        var word = $(this.IDs.clueWord).val();
        var clue = $(this.IDs.clueText).val().replace(/\n/g,"");
        var cellId = this.Xword.getFirstHilitedCellId();
        var isAcross = this.Xword.isHiliteAcross();
        try {
            $(this.IDs.clueMsg).text("");
            this.Xword.setWordData(cellId, word, clue, isAcross);
            this._setWidgetStates();
        } catch(err) {
            $(this.IDs.clueMsg).text(err.message);
        }
    }

    #_deleteWordDataClicked = () => {
        var cellId = this.Xword.getFirstHilitedCellId();
        var isAcross = this.Xword.isHiliteAcross();
        this.Xword.deleteWordData(cellId, isAcross);
        $(this.IDs.clueWord).val("");
        $(this.IDs.clueText).val("");
        $(this.IDs.clueMsg).text("");
    }

    #_saveBtnClicked = () => {
        var reqData = JSON.stringify(this.Xword.getGridData());
        $.ajax({
            method: "POST",
            data: {'data': reqData},
            dataType: "json",
            success: this._saveSuccess,
            error: this._saveError
        })
    }

    #_hiliteNextAndLoadForm() {
        this.Xword.hiliteNextIncomplete();
        var cellId = this.Xword.getFirstHilitedCellId();
        if (cellId === null) $(this.IDs.clueForm).hide();
        else this._setupClueForm(cellId);
    }

    #_getClueRefText (clueNum, maxLength, isAcross) {
       var label = (isAcross) ? "Across" : "Down";
       return ("#" + clueNum + " " + label + " (" + maxLength + ")");
    }

    #_setupClueForm(cellId) {
        var isAcross = this.Xword.isHiliteAcross();
        var formFields = this._gatherClueFormData(cellId, isAcross);
        $(this.IDs.clueNum).text(formFields.clueRef);
        $(this.IDs.clueWord).val(formFields.word);
        $(this.IDs.clueText).val(formFields.clue);
        $(this.IDs.clueWord).attr("maxlength", formFields.maxLength);
        $(this.IDs.clueMsg).text("");
        (formFields.word === "") ? $(this.IDs.clueWord).focus() : $(this.IDs.clueText).focus()
    }

    #_gatherClueFormData(cellId, isAcross) {
        var formFields = {clueRef:null, word:"", clue:"", maxLength:null};
        var gridWord = this.Xword.readWord(cellId, isAcross);
        formFields.maxLength = gridWord.length;
        formFields.clueNum = this.Xword.getClueNum(cellId, isAcross);
        formFields.clueRef = this._getClueRefText(formFields.clueNum, formFields.maxLength, isAcross);
        var wordData = this.Xword.getWordData(cellId, isAcross);
        if (wordData === null) {
            gridWord = gridWord.replaceAll(" ","");
            if (gridWord.length === formFields.maxLength) formFields.word = gridWord;
        } else {
            formFields.word = wordData.word;
            formFields.clue = wordData.clue;
        }
        return formFields;
    }

    #_saveSuccess = (result) => {
        this.Xword.puzzleId = result.puzzle_id;
        alert("Successfully saved");
    }

    #_saveError = (jqXHR, status, error) => {
        alert(status+":"+jqXHR.responseText);
    }
}
