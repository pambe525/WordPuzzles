class XWordPuzzle {

    view = null;
    sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    labels = {size:"Grid Size", radio1:"Blocks", radio2:"Clues"};

    cellSize = 29;
    jqGridObj = null;
    id = 0;
    size = 0;
    desc = "";
    sharedAt = null;

    constructor() {
        this.view = new PuzzleEditor(this);
        this.view.setSizeSelector(this.sizeOptions);
        this.view.setUILabels(this.labels);
    }

    initialize(puzzleData) {
        if (puzzleData == null) throw new Error("Puzzle data is required for initialization");
        this.size = puzzleData.size;
        this.jqGridObj = $("<div></div>");
        for (var i = 0; i < this.size * this.size; i++)
            $(this.jqGridObj).append(this._createGridCell());
        this._setGridBoxStyling(this.size);
    }


    getPuzzleContents() {
        return this.jqGridObj;
    }

    getData() {
        return {is_xword: true, id: this.id, size: this.size, desc: this.desc,
            shared_at: this.sharedAt};
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
