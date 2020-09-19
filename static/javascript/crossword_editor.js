function setEditMode() {
    var msg;
    if ($("#edit-mode").val() == 1) {
        var msg = "Click on a grid square to block it. Re-select to unblock. " +
            "Diametrically opposite square will also be blocked using 180 deg. rotational symmetry.";
        $("#edit-tip").html(msg);
    }
}

function setUIWidgetStates() {
    if (XWord.hasBlocks()) {
        $("#grid-size").prop("disabled", true);
        $("#clear-grid").prop("disabled", false);
    } else {
        $("#grid-size").prop("disabled", false);
        $("#clear-grid").prop("disabled", true);
    }
}

function cellClicked(event) {
    XWord.toggleCellBlock(event.id);
    setUIWidgetStates();
}

function clearGrid() {

}

class CrosswordEditor {

    constructor(xword) {
        if ( !xword ) throw new Error("Argument expected");
        if (typeof(xword) != "Crossword") throw new Error("Object of type Crossword expected");
        this.XWord = xword;
    }
}