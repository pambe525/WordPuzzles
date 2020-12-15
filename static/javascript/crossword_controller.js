class CrosswordController {

    view = new PuzzleEditView(this);
    sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    xwordGrid = null;
    across = {};
    down = {};

    constructor() {
        this.view.setSizeSelector(this.sizeOptions);
    }

    initialize(puzzleData) {
        if (puzzleData == null) throw new Error("Puzzle data is required for initialization");
        this.view.id = puzzleData.id;
        if (puzzleData.size !== undefined) this.view.size = puzzleData.size;
        this.view.desc = puzzleData.desc;
        this.view.initialize();
    }

    getPuzzle(size) {
        this.xwordGrid = new XWordGrid(size);
        return this.xwordGrid.getGridObj();
    }
}

