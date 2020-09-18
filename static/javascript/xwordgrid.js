function setEditMode() {
    var msg;
    if ($("#edit-mode").val() == 1) {
        msg = "Click on a grid square to block it. Re-select to unblock. Diametrically opposite square " +
            "will also be blocked using 180 deg. rotational symmetry.";
        $("#message").html(msg);
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
