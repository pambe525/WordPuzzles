class XWordEditor {

    _sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    _labels = {size:"Grid Size", radio1:"Blocks", radio2:"Clues"};

    view = null;        // type: EditPuzzleView
    xwordGrid = null;   // type: XWordGrid

    constructor(puzzleData) {
        if ( !puzzleData ) throw new Error("Puzzle data is required");
        this.view = new EditPuzzleView(puzzleData);
        this.view.setUILabels(this._labels);
        this.view.bindHandlers(this);
        this._setupNewGrid(puzzleData);
        this.view.setSizeSelector(this._sizeOptions, this.xwordGrid.size);
    }

    //==> PUBLIC EVENT HANDLERS
    onClueUpdateClick = () => {
        let wordData = this.view.getClueFormInput();
        try {
            this.xwordGrid.setHilitedWordData(wordData);
        }
        catch(e) { this.view.setClueMsg(e.message); }
    }
    onGridCellClick = (event) => {
        if ( this.view.isPublished() ) return;
        let cell = event.target;
        if ( this.view.getActiveSwitchLabel() === "Blocks" ) {
            if ( this.xwordGrid.toggleBlock(cell) ) {
                this.view.dataChanged();
                this.view.setStatus( this.xwordGrid.getStatus() );
            }
        } else {
            this.xwordGrid.toggleHilite(cell);
            this.view.hideClueForm(false);
            this.view.setClueForm( this.xwordGrid.getHilitedWordData() );
        }
    }
    onSaveClick = () => {
        let gridData = this.xwordGrid.getGridData();
        this.view.save(gridData);
    }
    onSizeChange = () => {
        let response = true;
        if (this.xwordGrid.hasBlocks()) response = confirm("All changes to grid will be cleared");
        if (response) this._setupNewGrid({size:this.view.getSizeSelection()});
        else this.view.setSize(this.xwordGrid.size);
    }
    onSwitchChange = () => {
        let switchLabel = this.view.getActiveSwitchLabel();
        if (switchLabel === "Blocks") {
            this.view.hideClueForm();
            this.xwordGrid.clearHilite();
        } else {
            if ( !this.xwordGrid.isComplete() ) {
                this.view.hideClueForm(false);
                this.xwordGrid.hiliteNextIncomplete();
                this.view.setClueForm( this.xwordGrid.getHilitedWordData() );
            } else {
                this.view.hideClueForm();
                this.view.disablePublish(false);
            }
        }
    }

    //==> PRIVATE METHODS
    _setupNewGrid(puzzleData) {
        this.xwordGrid = new XWordGrid(puzzleData, this.onGridCellClick);
        this.view.setPuzzleContent(this.xwordGrid.getPuzzleHtml());
        if ( this.xwordGrid.hasClues() ) {
            this.xwordGrid.displayWordsInGrid();
            if (this.view.isPublished()) this.view.setPublishedState();
            else this.view.selectSwitchLabel("Clues");
        }
        else this.view.selectSwitchLabel("Blocks");
        if (puzzleData.data === undefined) this.view.dataChanged();
        this.view.setStatus( this.xwordGrid.getStatus() );
    }
}

