class CrosswordEditor {

    IDs = { grid:null, selectSize:'#grid-size', resetBtn:'#reset-grid', selectMode:'#edit-mode',
            modeTip:'#mode-tip', saveGrid:'#save-grid', clueForm:'#clue-form', clueNum:'#clue-num',
            clueWord:'#clue-word', clueHint:'#clue-hint', clueText:'#clue-text', clueMsg:'#clue-msg',
            clueUpdateBtn:'#clue-update'
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

    //--------------------------------------------------------------------------------------------------------------------
    // PRIVATE FUNCTIONS
    //
    _createNewCrossword() {
        var gridSize = parseInt($(this.IDs.selectSize).val());
        this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
    }

    _cellClicked = (event) => {
        if ( parseInt($(this.IDs.selectMode).val() ) === 1) {
            this.Xword.toggleCellBlock(event.target.id);
            this._setWidgetStates();
        } else {
            this._hiliteWordAndLoadClue(event.target.id);
       }
    }

    _setupHandlers() {
        $(this.IDs.selectSize).change(this._sizeSelectionChanged);
        $(this.IDs.selectMode).change(this._modeSelectionChanged);
        $(this.IDs.resetBtn).click(this._resetBtnClicked);
        $(this.IDs.clueUpdateBtn).click(this._updateClue);
        $(this.IDs.clueWord).keyup(this._onEnterKey);
        $(this.IDs.clueText).keyup(this._onEnterKey);
    }

    _onEnterKey = (event) => {
        if (event.keyCode === 13)
            $(this.IDs.clueUpdateBtn).click();
    }

    _setModeHelpText() {
        var msg;
        var selectMode = parseInt($(this.IDs.selectMode).val());
        if (selectMode === 1)
            msg = "Click on a grid square to block it. Re-select to unblock. " +
                "Diametrically opposite square will also be blocked using 180 deg. rotational symmetry.";
        else
            msg = "Click on a numbered square to edit ACROSS or DOWN word and its clue.";
        $(this.IDs.modeTip).text(msg);
    }

    _setWidgetStates() {
        if (this.Xword.hasBlocks()) {
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
        } else {
            $(this.IDs.clueForm).show();
        }
    }

    _sizeSelectionChanged = () => {
        var gridSize = parseInt($(this.IDs.selectSize).val());
        this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
    }

    _modeSelectionChanged = () => {
        this._setModeHelpText();
        this._setWidgetStates();
    }

    _resetBtnClicked = () => {
        var msg = "All changes to grid will be lost. Please confirm or cancel."
        if ( confirm(msg) ) {
            var gridSize = parseInt($(this.IDs.selectSize).val());
            this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
            this._setWidgetStates();
        }
    }

    _hiliteWordAndLoadClue(cellId) {
        var isAcross = this.Xword.toggleWordHilite(cellId);
        var label = (isAcross) ? "Across" : "Down";
        var clueNum = this.Xword.getClueNum(cellId, isAcross);
        var gridWord = this.Xword.readWord(cellId, isAcross);
        var maxLength = gridWord.length;
        $(this.IDs.clueNum).text("#" + clueNum + " " + label);
        $(this.IDs.clueHint).text("("+ maxLength + ")");
        $(this.IDs.clueMsg).text("");
        $(this.IDs.clueWord).attr("maxlength", maxLength);
        $(this.IDs.clueText).val("");
        $(this.IDs.clueWord).focus();
        var defaultWord = (gridWord.replace(" ","").length !== maxLength) ? "" : gridWord;
        $(this.IDs.clueWord).val(defaultWord);
    }

    _updateClue = () => {
        var word = $(this.IDs.clueWord).val();
        var clue = $(this.IDs.clueText).val();
        var cellId = this.Xword.getFirstHilitedCellId();
        var isAcross = this.Xword.isHiliteAcross();
        try {
            this.Xword.setWordData(cellId, word, clue, isAcross);
        } catch(err) {
            $(this.IDs.clueMsg).text(err.message);
        }
    }
}
