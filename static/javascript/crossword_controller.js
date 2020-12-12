class CrosswordController {

    #view = new PuzzleEditView(this);
    sizeOptions = {5: "5x5", 7: "7x7", 9: "9x9", 11: "11x11", 13: "13x13", 15: "15x15", 17: "17x17"};
    xwordGrid = null;
    id = 0;
    size = 0;
    sharedAt = null;
    desc = "";
    acrossWords = {};
    downWords = {};

    constructor() {
        this.#view.setSizeSelector(this.sizeOptions);
    }

    initialize(puzzleData) {
        if (puzzleData == null) throw new Error("Puzzle data is required for initialization");
        this.id = puzzleData.id;
        this.size = puzzleData.size;
        this.#setAsNew(puzzleData.size);
        this.#view.setSize(puzzleData.size);
        this.#setXWordGrid(puzzleData.size);
        this.#view.bindHandlers(this);
    }

    #setXWordGrid(size) {
        this.xwordGrid = new XWordGrid(size);
        this.#view.setPuzzle(this.xwordGrid.getGridObj());
    }

    #setAsNew() {
        this.#view.setTitle("New Crossword Puzzle");
        this.#view.disableDelete();
        this.#view.disablePublish();
        this.#view.hideClueForm();
    }

    onSizeChange = () => {
        this.#setXWordGrid(this.#view.getSize());
        this.#view.setRadio1();
    }

    onSwitchChange = () => {
        (this.#view.getRadioChecked() === "radio-2") ?
            this.#view.showClueForm() : this.#view.hideClueForm();
    }

    onSaveClick = () => {
        let data = {is_xword: true, id: this.id, size: this.size, desc: this.desc, shared_at: this.sharedAt};
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(data)},
        });
     }
}

