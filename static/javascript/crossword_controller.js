class XWordGrid {

    cellSize = 29;
    jqGridObj = null;

    constructor(gridSize) {
        this.jqGridObj = $("<div></div>");
        for (var i = 0; i < gridSize * gridSize; i++)
            $(this.jqGridObj).append(this._createGridCell());
        this._setGridBoxStyling(gridSize);
    }

    getGridObj() {
        return this.jqGridObj;
    }

    _createGridCell() {
        var cell = $("<div></div>");
        cell.width(this.cellSize).height(this.cellSize);
        cell.css("border-top", "1px solid black").css("border-left", "1px solid black");
        cell.css("float","left").css("box-sizing","border-box");
        return cell;
    }

    _setGridBoxStyling(gridSize) {
        this.jqGridObj.width(this.cellSize * gridSize + 1).height(this.cellSize * gridSize + 1);
        this.jqGridObj.css("border-bottom", "1px solid black");
        this.jqGridObj.css("border-right", "1px solid black");
    }
}

class CrosswordController {

    sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    xwordGrid = null;

    constructor() {
        PuzzleEditView.setSizeLabel("Grid Size");
        PuzzleEditView.setRadioSwitch("Blocks","Clues", this._onSwitchChange);
        PuzzleEditView.hideSaveOkIcon();
        PuzzleEditView.setSizeSelector(this.sizeOptions, this._onSizeChange);
    }

    initialize(puzzleData) {
        if (puzzleData == null) throw new Error("Puzzle data is required for initialization");
        this._setAsNew(puzzleData.size);
        PuzzleEditView.setSize(puzzleData.size);
        this._setXWordGrid(puzzleData.size);
    }

    _setXWordGrid(size) {
        this.xwordGrid = new XWordGrid(size);
        PuzzleEditView.setPuzzle(this.xwordGrid.getGridObj());
    }

    _setAsNew() {
        PuzzleEditView.setTitle("New Crossword Puzzle");
        PuzzleEditView.disableDelete();
        PuzzleEditView.disablePublish();
        PuzzleEditView.hideClueForm();
    }

    _onSizeChange = () => {
        this._setXWordGrid(PuzzleEditView.getSize());
        PuzzleEditView.setRadio1();
    }

    _onSwitchChange = () => {
        (PuzzleEditView.getRadioChecked() === "radio-2") ?
            PuzzleEditView.showClueForm() : PuzzleEditView.hideClueForm();
    }
}

