class XWordEditor {

    _sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    _labels = {size:"Grid Size", radio1:"Blocks", radio2:"Clues"};

    view = null;
    xwordGrid = null;

    constructor(puzzleData) {
        if ( !puzzleData ) throw new Error("Puzzle data is required");
        this.view = new EditPuzzleView(puzzleData);
        this.view.setUILabels(this._labels);
        this._setupNewGrid(puzzleData);
        this.view.setSizeSelector(this._sizeOptions, this.xwordGrid.size);
        this.view.bindHandlers(this);
    }

    /* PUBLIC EVENTS HANDLERS */
    onSwitchChange = () => {
        let switchLabel = this.view.getActiveSwitchLabel();
        if (switchLabel === "Blocks") {
            this.view.hideClueForm();
            this.xwordGrid.clearHilite();
        } else {
            this.view.hideClueForm(false);
            this.xwordGrid.hiliteNextIncomplete();
            this.view.setClueForm( this._getClueFormFieldsData() );
        }
    }

    onSizeChange = () => {
        let response = true;
        if (this.xwordGrid.hasBlocks()) response = confirm("All changes to grid will be cleared");
        if (response) this._setupNewGrid({size:this.view.getSizeSelection()});
        else this.view.setSize(this.xwordGrid.size);
    }

    onSaveClick = () => {
        this.view.save();
    }

    onGridCellClick = (event) => {
        if (this.view.getActiveSwitchLabel() === "Blocks")
            this.xwordGrid.toggleBlock(event.target);
    }

    onClueUpdateClick = () => {
        let wordData = this.view.getClueFormInput();
        try {
            this.xwordGrid.setHilitedWordData(wordData);
        }
        catch(e) { this.view.setClueMsg(e.message); }
    }

    /* PRIVATE METHODS */
    _setupNewGrid(puzzleData) {
        this.xwordGrid = new XWordGrid(puzzleData, this.onGridCellClick);
        this.xwordGrid.setDataChangeListener(this.view);
        this.view.setPuzzleContent(this.xwordGrid.getPuzzleHtml());
        this.view.setSwitchLabel("Blocks");
        this.view.hideClueForm();
        this.view.dataChanged();
    }
    _getClueFormFieldsData() {
        let formFields = {};
        let clueNum = this.xwordGrid.getHilitedClueNum();
        let isAcross = this.xwordGrid.isHiliteAcross();
        let clueType = (isAcross) ? "Across" : "Down";
        formFields.maxLength = this.xwordGrid.getHilitedCells().length;
        formFields.clueWord = this.xwordGrid.getHilitedClueWord();
        formFields.clueText = this.xwordGrid.getHilitedClueText();
        formFields.clueRef = "#" + clueNum + " " + clueType + " (" + formFields.maxLength + ")";
        return formFields;
    }
}

