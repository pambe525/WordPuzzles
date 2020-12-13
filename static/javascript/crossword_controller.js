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
        this.#view.initialize();
        this.#view.setSize(puzzleData.size);
        this.#setXWordGrid(puzzleData.size);
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
        this.#view.hideClueForm();
    }

    onSwitchChange = () => {
        (this.#view.getRadioChecked() === "radio-2") ?
            this.#view.hideClueForm(false) : this.#view.hideClueForm();
    }

    onSaveClick = () => {
        this.desc = this.#view.getDesc();
        let data = {is_xword: true, id: this.id, size: this.size, desc: this.desc, shared_at: this.sharedAt};
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action':'save', 'data': JSON.stringify(data)},
            success: this.onSaveSuccess,
            error: this.onSaveError,
        });
    }

    onSaveSuccess = (result) => {
        if (result['error_message'] !== undefined && result['error_message'] !== "") {
            alert(result['error_message']);
        } else {
            this.id = result.id;
            this.#view.showSaveOKIcon();
            this.#view.disableDelete(false);
        }
    }

    onSaveError = (xhr, status, error) => {
        alert(error);
    }

    onDeleteClick = () =>{
        var msg = "All saved data will be permanently deleted.";
        var response = confirm(msg);
        if ( !response ) return;
        $.ajax({
            method: "POST",
            dataType: "json",
            data: {action: 'delete', id: this.id},
            success: this.onDeleteSuccess,
            error: this.onDeleteError,
        });
    }

    onDeleteSuccess = (result) => {
        window.location.replace("/");
    }

    onDeleteError = (xhr, status, error) => {
        alert(error);
    }

    onBeforeUnload = (e) => {

    }
}

