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
            this.Xword.toggleWordHilite(event.target.id);
            this._loadClueForm(event.target.id);
       }
    }

    _setupHandlers() {
        $(this.IDs.selectSize).change(this._sizeSelectionChanged);
        $(this.IDs.selectMode).change(this._modeSelectionChanged);
        $(this.IDs.resetBtn).click(this._resetBtnClicked);
        $(this.IDs.clueUpdateBtn).click(this._updateClue);
        $(this.IDs.clueWord).keyup(this._onEnterKey);
        $(this.IDs.clueText).keydown(this._onEnterKey);
    }

    _onEnterKey = (event) => {
        if (event.keyCode === 13) {
            event.preventDefault();
            $(this.IDs.clueUpdateBtn).click();
        }
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

    _sizeSelectionChanged = () => {
        var gridSize = parseInt($(this.IDs.selectSize).val());
        this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
    }

    _modeSelectionChanged = () => {
        this._setModeHelpText();
        this._setWidgetStates()
    }

    _resetBtnClicked = () => {
        var msg = "All changes to grid will be lost. Please confirm or cancel."
        if ( confirm(msg) ) {
            var gridSize = parseInt($(this.IDs.selectSize).val());
            this.Xword = new Crossword(this.gridId, this._cellClicked, gridSize);
            this._setWidgetStates();
        }
    }

    _loadClueForm(cellId) {
        var isAcross = this.Xword.isHiliteAcross();
        this._setClueFormFields(cellId, isAcross);
        $(this.IDs.clueWord).focus();
    }

    _updateClue = () => {
        var word = $(this.IDs.clueWord).val();
        var clue = $(this.IDs.clueText).val();
        var cellId = this.Xword.getFirstHilitedCellId();
        var isAcross = this.Xword.isHiliteAcross();
        try {
            this.Xword.setWordData(cellId, word, clue, isAcross);
            this._hiliteNextAndLoadForm();
        } catch(err) {
            $(this.IDs.clueMsg).text(err.message);
        }
    }

    _hiliteNextAndLoadForm() {
        this.Xword.hiliteNextIncomplete();
        var cellId = this.Xword.getFirstHilitedCellId();
        this._loadClueForm(cellId);
    }

    _getClueRefText (clueNum, maxLength, isAcross) {
       var label = (isAcross) ? "Across" : "Down";
       return ("#" + clueNum + " " + label + " (" + maxLength + ")");
    }

    _getWordData(cellId, isAcross) {
        var wordData = this.Xword.getWordData(cellId, isAcross);
        return (wordData === null) ? {word:"", clue:""} : wordData;
    }

    _setClueFormFields(cellId, isAcross) {
        var maxLength = this.Xword.readWord(cellId, isAcross).length;
        var clueNum = this.Xword.getClueNum(cellId, isAcross);
        var clueRef = this._getClueRefText(clueNum, maxLength, isAcross);
        var wordData = this._getWordData(cellId, isAcross);
        $(this.IDs.clueNum).text(clueRef);
        $(this.IDs.clueWord).val(wordData.word);
        $(this.IDs.clueText).val(wordData.clue);
        $(this.IDs.clueWord).attr("maxlength", maxLength);
    }
}
