/**
 * TEST HELPERS
 */
function getGridCells() {
    return $("#puzzle > div").children("div");
}

function saveData(responseData) {
    ajaxSettings = null;
    $("#save").click();
    ajaxSettings.success(responseData);
}

var controller = null;

/* ----------------------------------------------------------------------------------------------------------*/
QUnit.module("Puzzle Editing", {
    beforeEach: function () {
        setupFixture(EditPuzzlePageHtml);
        controller = new XWordPuzzle();
    }
});

test("Constructor customizes labels on page", function (assert) {
    assert.equal($("#size-label").text(), "Grid Size");
    assert.equal($("#radio1-label").text(), "Blocks");
    assert.equal($("#radio2-label").text(), "Clues");
    assert.equal($("#save-ok").prop("hidden"), true);
});

test("Initialization sets size selector dropdown", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
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

test("Initialization sets specified grid size in dropdown", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal($("#size").val(), puzzleData.size);
});

test('Initialization creates grid using specified size in data', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal(getGridCells().length, 25);
});

test("New puzzle initialization sets correct title and state of widgets", function (assert) {
    let puzzleData = {id: 0, size: 5};
    controller.initialize(puzzleData);
    assert.equal($("#page-title").text(), "New Crossword");
    assert.true($("#delete").prop("disabled"));
    assert.true($("#publish").prop("disabled"));
    assert.true($("#clue-form").is(":hidden"));
    assert.true($("#radio-1").prop("checked"));
});

test("Existing puzzle initialization sets correct title and state of widgets", function (assert) {
    let puzzleData = {id: 10, size: 5, desc:"xword 10"};     // ID=10 indicates exisiting puzzle edit
    controller.initialize(puzzleData);
    assert.equal($("#page-title").text(), "Edit Crossword #10");
    assert.false($("#delete").prop("disabled"));
    assert.true($("#publish").prop("disabled"));
    assert.equal($("#desc").text(), "xword 10");
    assert.true($("#clue-form").is(":hidden"));
    assert.true($("#radio-1").prop("checked"));
});

test('Grid Size change redraws grid to new size', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#size").val(7).change();
    assert.equal(getGridCells().length, 49);
});

test('Grid Size change in Clues mode switches to Block mode and hides form', function (assert) {
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

test('Saving data includes basic data in ajax call for new xword', function (assert) {
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

test('Saving data includes basic data in ajax call for existing xword', function (assert) {
    let puzzleData = {id: 10, size: 5, desc: "xword #10"}
    controller.initialize(puzzleData);
    $("#save").click();
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxSettings.method, "POST");
    assert.equal(ajaxSettings.dataType, "json");
    assert.equal(ajaxSettings.data.action, "save");
    assert.equal(ajaxData.id, puzzleData.id);
    assert.equal(ajaxData.size, puzzleData.size);
    assert.equal(ajaxData.desc, puzzleData.desc);
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
    saveData({});
    assert.equal($("#delete").prop("disabled"), false);
    assert.false($("#save-ok").is(":hidden"));
});

test('Saving data a second time includes puzzle id', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    let saveBtn = $("#save");
    saveData({id: 10, error_message:""});  // First save with id=0, as new puzzle
    saveData({});                          // Second save - id should be updated from first save
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxData.id, 10);
});

test('Saving data with a trapped error message displays error', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    let msg = "Trapped error";
    saveData({error_message:msg});
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
    saveData({id:15});           // First save the grid to enable Delete btn
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

test('dataSaved is true after saving data', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.false(controller.view.dataSaved);
    saveData({});
    assert.true(controller.view.dataSaved);
});

test('dataSaved is false after description is changed', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    saveData({});
    $("#desc").text("Some text").change();
    assert.false(controller.view.dataSaved);
});

test('dataSaved is false after grid is reset', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    saveData({});
    $("#size").val(7).change();
    assert.false(controller.view.dataSaved);
});

// TEST: existing puzzle initialization sets clues edit mode if words/clues exist
// TEST: existing puzzle initialization loads data, blocks and words into grid



