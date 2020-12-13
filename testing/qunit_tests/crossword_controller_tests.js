/**
 * TEST HELPERS
 */
function getGridCells() {
    return $("#puzzle > div").children("div");
}

var controller = null;

/* ----------------------------------------------------------------------------------------------------------*/
QUnit.module("New Crossword", {
    beforeEach: function () {
        setupFixture(EditPuzzlePageHtml);
        controller = new CrosswordController();
    }
});

test("Constructor customizes labels on page", function (assert) {
    assert.equal($("#size-label").text(), "Grid Size");
    assert.equal($("#radio1-label").text(), "Blocks");
    assert.equal($("#radio2-label").text(), "Clues");
    assert.equal($("#save-ok").prop("hidden"), true);
});

test("Constructor sets size selector dropdown", function (assert) {
    let options = $("#size > option");
    let textVals = $.map(options, function (option) { return option.text; });
    let values = $.map(options, function (option) { return parseInt(option.value); });
    assert.equal(options.length, 7);
    assert.deepEqual(textVals, ["5x5", "7x7", "9x9", "11x11", "13x13", "15x15", "17x17"])
    assert.deepEqual(values, [5, 7, 9, 11, 13, 15, 17]);
});

test("Initialization without puzzleData throws error", function (assert) {
    assert.throws(
        function () { controller.initialize();}, /Puzzle data is required for initialization/
    )
});

test("initialize sets title and initial state of widgets", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal($("#page-title").text(), "New Crossword Puzzle");
    assert.equal($("#delete").prop("disabled"), true);
    assert.equal($("#publish").prop("disabled"), true);
    assert.true($("#clue-form").is(":hidden"));
    assert.equal($("#radio-1").prop("checked"), true);
});

test("Initialize sets grid size dropdown and given size", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal($("#size").val(), puzzleData.size);
});

test('Initialize creates grid using specified size in data', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal(getGridCells().length, 25);
});

test('Grid Size change redraws grid to new size', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#size").val(7).change();
    assert.equal(getGridCells().length, 49);
});

test('Grid Size change in Clues edit mode switches to Block edit and hides form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    let radio2 = $("#radio-2");
    radio2.prop("checked", true).change();  // Toggle edit mode
    assert.true(radio2.is(":checked"));
    $("#size").val(7).change();
    assert.false(radio2.is(":checked"));
    assert.true($("#clue-form").is(":hidden"));
});

test('Switching to Clues edit mode shows clue edit form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#radio-2").prop("checked", true).change();
    assert.equal($("#clue-form").prop("hidden"), false);
});

test('Switching back to Block edit mode hides clue edit form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#radio-2").prop("checked", true).change();
    $("#radio-1").prop("checked", true).change();
    assert.true($("#clue-form").is(":hidden"));
});

test('Saving data includes basic data in ajax call', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxSettings.method, "POST");
    assert.equal(ajaxSettings.dataType, "json");
    assert.equal(ajaxSettings.data.action, "save");
    assert.equal(ajaxData.id, puzzleData.id);
    assert.equal(ajaxData.size, puzzleData.size);
    assert.equal(ajaxData.is_xword, true);
    assert.equal(ajaxData.shared_at, null);
});

test('Saving data includes desc in ajax call', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    let descField = $("#desc");
    descField.text("This is a crossword");
    $("#save").click();
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxData.desc, descField.text());
});

test('Saving data successfully enables delete button', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();
    ajaxSettings.success({});
    assert.equal($("#delete").prop("disabled"), false);
    assert.false($("#save-ok").is(":hidden"));
});

test('Saving data a second time includes puzzle id', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    let saveBtn = $("#save");
    saveBtn.click();   // First save (id=0) as new puzzle
    ajaxSettings.success({id: 10, error_message:""});
    saveBtn.click();   // Second save - id should be updated from first save
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxData.id, 10);
});

test('Saving data with a trapped error message displays error', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();
    let msg = "Trapped error";
    alertMessage = null;
    ajaxSettings.success({error_message:msg});
    assert.equal(alertMessage, msg);
    assert.equal($("#save-ok").is(":hidden"), true);
    assert.equal($("#delete").prop("disabled"), true);
});

test('Saving data with a system error shows alert with error message', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    ajaxSettings = null;
    $("#save").click();
    let msg = "System error occurred";
    ajaxSettings.error(null, null, msg);
    assert.equal(alertMessage, msg);
});

test('Delete shows confirmation box before deleting. Cancel takes no action.', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();          // First save the grid to enable Delete btn
    confirmResponse = false;     // Cancel confirmation box
    $("#delete").click();
    assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
    assert.equal(getGridCells().length, 25)
});

test('Delete confirmation makes ajax call to delete puzzle', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();          // First save the grid to enable Delete btn
    ajaxSettings.success({id:15});
    confirmResponse = true;      // Confirm delete
    $("#delete").click();
    assert.equal(ajaxSettings.method, "POST");
    assert.equal(ajaxSettings.dataType, "json");
    assert.equal(ajaxSettings.data.action, "delete");
    assert.equal(ajaxSettings.data.id, 15);
});

test('Delete with system error displays alert message', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#save").click();          // First save the grid to enable Delete btn
    confirmResponse = true;      // Confirm delete
    ajaxSettings = alertMessage = null;
    $("#delete").click();
    let msg = "System error occurred";
    ajaxSettings.error(null, null, msg);
    assert.equal(alertMessage, msg);
});

