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
        (switchLabel === "Blocks") ? this.view.hideClueForm() : this.view.hideClueForm(false);
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
        this.xwordGrid.toggleBlock(event.target);
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
}

