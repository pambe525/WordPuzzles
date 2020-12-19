class XWordEditor {

    _sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    _labels = {size:"Grid Size", radio1:"Blocks", radio2:"Clues"};

    view = null;
    xwordGrid = null;

    constructor(puzzleData) {
        if ( !puzzleData ) throw new Error("Puzzle data is required");
        this.view = new EditPuzzleView(puzzleData);
        this.xwordGrid = new XWordGrid(puzzleData.size);
        this.view.setUILabels(this._labels);
        this.view.setSizeSelector(this._sizeOptions, puzzleData.size);
        this.view.setPuzzleContent(this.xwordGrid.getPuzzleHtml());
        this.view.hideClueForm();
        this.view.bindHandlers(this);
    }

    /* PUBLIC EVENTS HANDLERS */
    onSwitchChange = () => {
        let switchLabel = this.view.getActiveSwitchLabel();
        (switchLabel === "Blocks") ? this.view.hideClueForm() : this.view.hideClueForm(false);
    }

    onSizeChange = () => {
        this.xwordGrid = new XWordGrid( this.view.getSizeSelection() );
        this.view.setPuzzleContent(this.xwordGrid.getPuzzleHtml());
        this.view.setSwitchLabel("Blocks");
        this.view.hideClueForm();
        this.view.dataChanged();
    }

    onSaveClick = () => {
        this.view.save();
    }
}

