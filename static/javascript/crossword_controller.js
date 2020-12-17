class CrosswordController {

    view = new PuzzleEditor(this);

    xwordGrid = null;

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
}

