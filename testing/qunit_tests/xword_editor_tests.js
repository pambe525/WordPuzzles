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
QUnit.module("XWord Editor", {
    beforeEach: function () {
        setupFixture(EditPuzzlePageHtml);
    }
});

test("Constructor throws error if puzzleData is null", function (assert) {
    assert.throws( function(){ new XWordEditor(); }, /Puzzle data is required/);
});

test("Constructor customizes labels on page", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    assert.equal($("#size-label").text(), "Grid Size");
    assert.equal($("#radio1-label").text(), "Blocks");
    assert.equal($("#radio2-label").text(), "Clues");
    assert.equal($("#save-ok").prop("hidden"), true);
});

test("Constructor sets size selector dropdown with correct options", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    let options = $("#size > option");
    let textVals = $.map(options, function (option) { return option.text; });
    let values = $.map(options, function (option) { return parseInt(option.value); });
    assert.equal(options.length, 7);
    assert.deepEqual(textVals, ["5x5", "7x7", "9x9", "11x11", "13x13", "15x15", "17x17"])
    assert.deepEqual(values, [5, 7, 9, 11, 13, 15, 17]);
});

test("Constructor sets default size on selector dropdown", function (assert) {
    let puzzleData = {id: 0}
    controller = new XWordEditor(puzzleData);
    assert.equal($("#size").val(), 15);
});

test("Constructor sets specified grid size in dropdown", function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    assert.equal($("#size").val(), puzzleData.size);
});

test('Constructor creates grid using specified size in data', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    assert.equal(getGridCells().length, 25);
});

test("New puzzle sets correct title and state of widgets", function (assert) {
    let puzzleData = {size: 5};
    controller = new XWordEditor(puzzleData);
    assert.equal($("#page-title").text(), "New Crossword");
    assert.true($("#delete").prop("disabled"));
    assert.true($("#publish").prop("disabled"));
    assert.true($("#clue-form").is(":hidden"));
    assert.true($("#radio-1").prop("checked"));
});

test("Existing puzzle initialization sets correct title and state of widgets", function (assert) {
    let puzzleData = {id: 10, size: 5, desc:"xword 10"};     // ID=10 indicates exisiting puzzle edit
    controller = new XWordEditor(puzzleData);
    assert.equal($("#page-title").text(), "Edit Crossword #10");
    assert.false($("#delete").prop("disabled"));
    assert.true($("#publish").prop("disabled"));
    assert.equal($("#desc").text(), "xword 10");
    assert.true($("#clue-form").is(":hidden"));
    assert.true($("#radio-1").prop("checked"));
});

test('Grid Size change redraws grid to new size', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    $("#size").val(7).change();
    assert.equal(getGridCells().length, 49);
});

test('Grid Size change in Clues mode switches to Block mode and hides form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    let radio2 = $("#radio-2");
    radio2.prop("checked", true).change();  // Toggle edit mode
    assert.true(radio2.is(":checked"));
    $("#size").val(7).change();
    assert.false(radio2.is(":checked"));
    assert.true($("#clue-form").is(":hidden"));
});

test('Switching to Clues edit mode shows clue edit form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    $("#radio-2").prop("checked", true).change();
    assert.equal($("#clue-form").prop("hidden"), false);
});

test('Switching back to Block edit mode hides clue edit form', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    $("#radio-2").prop("checked", true).change();
    $("#radio-1").prop("checked", true).change();
    assert.true($("#clue-form").is(":hidden"));
});

test('Saving data includes basic data in ajax call for new xword', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
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
    controller = new XWordEditor(puzzleData);
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
    controller = new XWordEditor(puzzleData);
    let descField = $("#desc");
    descField.text("This is a crossword");
    $("#save").click();
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxData.desc, descField.text());
});

test('Saving data successfully enables delete button', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    saveData({});
    assert.equal($("#delete").prop("disabled"), false);
    assert.false($("#save-ok").is(":hidden"));
});

test('Saving data a second time includes puzzle id', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    let saveBtn = $("#save");
    saveData({id: 10, error_message:""});  // First save with id=0, as new puzzle
    saveData({});                          // Second save - id should be updated from first save
    let ajaxData = JSON.parse(ajaxSettings.data.data);
    assert.equal(ajaxData.id, 10);
});

test('Saving data with a trapped error message displays error', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    let msg = "Trapped error";
    saveData({error_message:msg});
    assert.equal(alertMessage, msg);
    assert.equal($("#save-ok").is(":hidden"), true);
    assert.equal($("#delete").prop("disabled"), true);
});

test('Saving data with a system error shows alert with error message', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    ajaxSettings = null;
    $("#save").click();
    let msg = "System error occurred";
    ajaxSettings.error(null, null, msg);
    assert.equal(alertMessage, msg);
});

test('Delete shows confirmation box before deleting. Cancel takes no action.', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    $("#save").click();          // First save the grid to enable Delete btn
    confirmResponse = false;     // Cancel confirmation box
    $("#delete").click();
    assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
    assert.equal(getGridCells().length, 25)
});

test('Delete confirmation makes ajax call to delete puzzle', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
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
    controller = new XWordEditor(puzzleData);
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
    controller = new XWordEditor(puzzleData);
    assert.false(controller.view.dataSaved);
    saveData({});
    assert.true(controller.view.dataSaved);
});

test('dataSaved is false after description is changed', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    saveData({});
    $("#desc").text("Some text").change();
    assert.false(controller.view.dataSaved);
});

test('dataSaved is false after grid is reset', function (assert) {
    let puzzleData = {id: 0, size: 5}
    controller = new XWordEditor(puzzleData);
    saveData({});
    $("#size").val(7).change();
    assert.false(controller.view.dataSaved);
});

// TEST: existing puzzle initialization sets clues edit mode if words/clues exist
// TEST: existing puzzle initialization loads data, blocks and words into grid

/* ----------------------------------------------------------------------------------------------------------*/
QUnit.module("XWord Grid", {
    beforeEach: function () {
        setupFixture(EditPuzzlePageHtml);
    }
});

test('Grid has default size (15) if not specified', function(assert) {
    let puzzleData = {};
    new XWordEditor(puzzleData);
    assert.equal( getGridCells().length, 225 );
});

test('Grid bounding box has correct width & height', function(assert) {
  var gridSize=5;
  new XWordEditor({size:gridSize});
  assert.equal( getGridCells().length, 25 );
  let gridBox = $("#puzzle>div");
  assert.equal( gridBox.width(), (29*gridSize + 1) );
  assert.equal( gridBox.height(), (29*gridSize + 1) );
});

test('Grid initially autonumbers itself', function(assert) {
  var gridSize=5;
  new XWordEditor({size:gridSize});
  let gridCells = getGridCells();
  for (let clueNum = 1; clueNum <= gridSize; clueNum++)
      assert.equal( $(gridCells[clueNum-1]).children("span.xw-number").text(), clueNum );
  for (let clueNum = gridSize+1; clueNum <= gridSize*2-1; clueNum++)
      assert.equal( $(gridCells[(clueNum-gridSize)*gridSize]).children("span.xw-number").text(), clueNum );
});








