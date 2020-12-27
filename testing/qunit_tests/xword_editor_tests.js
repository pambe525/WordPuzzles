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
function verifyClueNums(clueNums) {
    let gridCells = getGridCells();
    let keys = Object.keys(clueNums);
    for (const i in keys)
        assert.equal($(gridCells[keys[i]]).children("span.xw-number").text(), clueNums[keys[i]]);
}
function clickOnCell(index) {
    getGridCells()[index].click();
}
function gridCell(index) {
    return $(getGridCells()[index]);
}
function doClueFormInput(clueWord, clueText) {
        $("#clue-word").val(clueWord);
        $("#clue-text").val(clueText);
        $("#clue-update").click();
    }

/**
 * XWordEditor Initialization
 */
(function() {
    QUnit.module("XWordEditor Instantiation", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test("Throws error if puzzleData is null", function (assert) {
        assert.throws(function () {
            new XWordEditor();
        }, /Puzzle data is required/);
    });
    test("Customizes labels on page", function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal($("#size-label").text(), "Grid Size");
        assert.equal($("#radio1-label").text(), "Blocks");
        assert.equal($("#radio2-label").text(), "Clues");
        assert.equal($("#save-ok").prop("hidden"), true);
    });
    test("Sets size selector dropdown with correct options", function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let options = $("#size > option");
        let textVals = $.map(options, function (option) {
            return option.text;
        });
        let values = $.map(options, function (option) {
            return parseInt(option.value);
        });
        assert.equal(options.length, 7);
        assert.deepEqual(textVals, ["5x5", "7x7", "9x9", "11x11", "13x13", "15x15", "17x17"])
        assert.deepEqual(values, [5, 7, 9, 11, 13, 15, 17]);
    });
    test("Sets default size on selector dropdown", function (assert) {
        let puzzleData = {id: 0}
        new XWordEditor(puzzleData);
        assert.equal($("#size").val(), 15);
    });
    test("Sets specified grid size in dropdown", function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal($("#size").val(), puzzleData.size);
    });
    test('Creates grid using specified size in data', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal(getGridCells().length, 25);
    });
    test("Sets correct title and state of widgets on new puzzle", function (assert) {
        let puzzleData = {size: 5};
        new XWordEditor(puzzleData);
        assert.equal($("#page-title").text(), "New Crossword");
        assert.true($("#delete").prop("disabled"));
        assert.true($("#publish").prop("disabled"));
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#radio-1").prop("checked"));
    });
    test("Sets correct title and state of widgets on existing puzzle", function (assert) {
        let puzzleData = {id: 10, size: 5, desc: "xword 10"};     // ID=10 indicates exisiting puzzle edit
        new XWordEditor(puzzleData);
        assert.equal($("#page-title").text(), "Edit Crossword #10");
        assert.false($("#delete").prop("disabled"));
        assert.true($("#publish").prop("disabled"));
        assert.equal($("#desc").text(), "xword 10");
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#radio-1").prop("checked"));
    });
    test('Grid Size change redraws grid to new size', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        $("#size").val(7).change();
        assert.equal(getGridCells().length, 49);
    });
    test('Grid Size change in Clues mode switches to Block mode, hides form', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let radio2 = $("#radio-2");
        radio2.prop("checked", true).change();  // Toggle edit mode
        assert.true(radio2.is(":checked"));
        $("#size").val(7).change();
        assert.false(radio2.is(":checked"));
        assert.true($("#clue-form").is(":hidden"));
    });
    test('Grid Size change after adding blocks shows confirmation box', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let gridCells = getGridCells();
        gridCells[0].click();  // Create a block
        confirmMessage = "";
        confirmResponse = false;
        let selector = $("#size");
        selector.val(7).change();
        assert.equal(confirmMessage, "All changes to grid will be cleared");
        assert.equal(gridCells.length, 25);    // No change to grid
        assert.equal(selector.val(), 5);       // Should revert back to previous selection
    });
    test('Grid Size change after adding blocks resizes after confirmation', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        getGridCells()[0].click();  // Create a block
        confirmResponse = true;
        let selector = $("#size");
        selector.val(7).change();
        assert.equal(getGridCells().length, 49);    // Grid changed
        assert.equal(selector.val(), 7);       // New selection
    });
    test('Grid size change sets dataSaved to false', function (assert) {
        let puzzleData = {id: 0, size: 5}
        let controller = new XWordEditor(puzzleData);
        saveData({});
        $("#size").val(7).change();
        assert.false(controller.view.dataSaved);
    });
    test('Grid has default size (15) if not specified', function (assert) {
        let puzzleData = {};
        new XWordEditor(puzzleData);
        assert.equal(getGridCells().length, 225);
    });
    test('Grid bounding box has correct width & height', function (assert) {
        var gridSize = 5;
        new XWordEditor({size: gridSize});
        assert.equal(getGridCells().length, 25);
        let gridBox = $("#puzzle>div");
        assert.equal(gridBox.width(), (29 * gridSize + 1));
        assert.equal(gridBox.height(), (29 * gridSize + 1));
    });
    test('Grid autonumbers itself', function (assert) {
        var gridSize = 5;
        new XWordEditor({size: gridSize});
        let clueNums = {0:"1",1:"2",2:"3",3:"4",4:"5",5:"6",10:"7",15:"8",20:"9"};
        verifyClueNums(clueNums);
     });
    test('dataSaved is false after description is changed', function (assert) {
        let puzzleData = {id: 0, size: 5}
        let controller = new XWordEditor(puzzleData);
        saveData({});
        $("#desc").text("Some text").change();
        assert.false(controller.view.dataSaved);
    });
    test('Grid is initialized with blocked cells from existing data', function (assert) {
        var gridSize = 5, blockStr = "1,2,7,17,22,23";
        new XWordEditor({size: gridSize, data:{blocks: blockStr}});
        let gridCells = getGridCells();
        let blockedCells = gridCells.filter(".xw-block");
        let blockedIndices = blockStr.split(",");
        assert.equal(blockedCells.length, blockedIndices.length);
        for (var i = 0; i < blockedIndices.length; i++)
            assert.true($(gridCells[parseInt(blockedIndices[i])]).hasClass("xw-block"));
    });
})();

/**
 * XWordEditor Save/Delete
 */
(function() {
    QUnit.module("XWordEditor Save/Delete", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test('Saving data includes basic data in ajax call for new xword', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
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
        new XWordEditor(puzzleData);
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
        new XWordEditor(puzzleData);
        let descField = $("#desc");
        descField.text("This is a crossword");
        $("#save").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxData.desc, descField.text());
    });
    test('Saving data successfully enables delete button', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        saveData({});
        assert.equal($("#delete").prop("disabled"), false);
        assert.false($("#save-ok").is(":hidden"));
    });
    test('Saving data a second time includes puzzle id', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let saveBtn = $("#save");
        saveData({id: 10, error_message: ""});  // First save with id=0, as new puzzle
        saveData({});                          // Second save - id should be updated from first save
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxData.id, 10);
    });
    test('Saving data with a trapped error message displays error', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let msg = "Trapped error";
        saveData({error_message: msg});
        assert.equal(alertMessage, msg);
        assert.equal($("#save-ok").is(":hidden"), true);
        assert.equal($("#delete").prop("disabled"), true);
    });
    test('Saving data with a system error shows alert with error message', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        ajaxSettings = null;
        $("#save").click();
        let msg = "System error occurred";
        ajaxSettings.error(null, null, msg);
        assert.equal(alertMessage, msg);
    });
    test('Saving data sets dataSaved to true', function (assert) {
        let puzzleData = {id: 0, size: 5}
        let controller = new XWordEditor(puzzleData);
        assert.false(controller.view.dataSaved);
        saveData({});
        assert.true(controller.view.dataSaved);
    });
    test('Delete shows confirm box before deleting. Cancel takes no action.', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        $("#save").click();          // First save the grid to enable Delete btn
        confirmResponse = false;     // Cancel confirmation box
        $("#delete").click();
        assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
        assert.equal(getGridCells().length, 25)
    });
    test('Delete confirmation makes ajax call to delete puzzle', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        saveData({id: 15});           // First save the grid to enable Delete btn
        confirmResponse = true;      // Confirm delete
        $("#delete").click();
        assert.equal(ajaxSettings.method, "POST");
        assert.equal(ajaxSettings.dataType, "json");
        assert.equal(ajaxSettings.data.action, "delete");
        assert.equal(ajaxSettings.data.id, 15);
    });
    test('Delete with system error displays alert message', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        $("#save").click();          // First save the grid to enable Delete btn
        confirmResponse = true;      // Confirm delete
        ajaxSettings = alertMessage = null;
        $("#delete").click();
        let msg = "System error occurred";
        ajaxSettings.error(null, null, msg);
        assert.equal(alertMessage, msg);
    });
})();

/**
 * XWordEditor Block Editing
 */
(function() {
    var controller = null;
    QUnit.module("XWordEditor Block Editing", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            controller = new XWordEditor({id: 0, size: 5});       }
    });
    test('Block Edit mode enables cell blocking', function (assert) {
        clickOnCell(0);
        assert.true($(gridCell(0)).hasClass("xw-block"));
    });
    test('Numbering in cell is cleared when blocked', function (assert) {
        clickOnCell(0);
        assert.equal(gridCell(0).children("span.xw-number").length, 0);
    });
    test('Reseting grid size retains block editing', function (assert) {
        $("#size").val(7).change();
        clickOnCell(0);
        assert.true(gridCell(0).hasClass("xw-block"));
    });
    test('Re-clicking cell toggles block', function (assert) {
        clickOnCell(1);
        clickOnCell(1);   // Second click
        assert.false(gridCell(1).hasClass("xw-block"));
    });
    test('Symmetric cell is also blocked', function (assert) {
        clickOnCell(6);
        assert.true(gridCell(18).hasClass("xw-block"));
        clickOnCell(23);
        assert.true(gridCell(1).hasClass("xw-block"));
    });
    test('Center cell in grid is properly blocked', function (assert) {
        clickOnCell(12);   // Center cell
        assert.true(gridCell(12).hasClass("xw-block"));
    });
    test('Grid is auto-numbered after cell block/unblock', function (assert) {
        clickOnCell(0);   // corner cells
        clickOnCell(4);   // corner cells
        clickOnCell(12);  // center cell
        let clueNums = {1:"1",2:"2",3:"3",5:"4",9:"5",10:"6",13:"7",15:"8",17:"9",21:"10"};
        verifyClueNums(clueNums);
    });
    test('Blocking/unblocking a grid cell sets dataSaved to false', function (assert) {
        saveData({});
        clickOnCell(8);   // block a cell
        assert.false(controller.view.dataSaved);
        saveData({});
        clickOnCell(8);   // unblock cell
        assert.false(controller.view.dataSaved);
    });
    test("Does not block cell if it or symm cell contains a letter", function(assert) {
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("trial", "");
        $("#radio-1").prop("checked", true).change();
        clickOnCell(0);
        assert.false($(gridCell(0)).hasClass("xw-block"));
        clickOnCell(23);
        assert.false($(gridCell(1)).hasClass("xw-block"));
    });
})();

/**
 * XWordEditor Clue Editing
 */
(function() {
    function assertClueFormFields(clueRef, word, clueText, msg) {
    assert.equal($("#clue-ref").text(), clueRef);
    assert.equal($("#clue-word").val(), word);
    assert.equal($("#clue-text").val(), clueText);
    assert.equal($("#clue-msg").text(), msg);
}
    function readLetterInCell(cell) {
        return $(cell).children(".xw-letter").text();
    }
    QUnit.module("XWordEditor Clue Edit Mode", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            new XWordEditor({id: 0, size: 5});
            $("#radio-2").prop("checked", true).change();
        }
    });
    test('Shows clue edit form', function (assert) {
        assert.equal($("#clue-form").prop("hidden"), false);
    });
    test('Switching back to Block edit mode hides clue edit form', function (assert) {
        $("#radio-1").prop("checked", true).change();  // Switch back to Block edit mode
        assert.true($("#clue-form").is(":hidden"));
    });
    test('Disables blocking selected cells', function (assert) {
        getGridCells()[0].click();
        assert.false($(getGridCells()[0]).hasClass("xw-block"));
    });
    test('Highlights first incomplete across clue in an unblocked grid', function (assert) {
        let hilitedCells = getGridCells().slice(0,5);
        assert.true($(hilitedCells).hasClass("xw-hilite"));
    });
    test('Initializes clue form with hilited word data', function (assert) {
        assertClueFormFields("#1 Across (5)", "", "", "")
    });
    test('Sets maxlength of word input field', function (assert) {
        assert.equal($("#clue-word").attr("maxlength"), "5");
    });
    test('Switching back to block edit mode clears hilite', function (assert) {
        $("#radio-1").prop("checked", true).change();
        assert.equal(getGridCells().filter(".xw-hilite").length, 0);
    });
    test('Throws error if word input does not fit grid', function (assert) {
        let word = "abcd ";
        let gridCells = getGridCells();
        let msgField = $("#clue-msg");
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must be 5 chars");
        word = "abcdef";
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must be 5 chars");
        for (let i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), "");
    });
    test('Throws error if word input does not contain alphabets', function (assert) {
        let word = "ab5cd";
        let gridCells = getGridCells();
        let msgField = $("#clue-msg");
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must contain all letters");
        word = "ab cd";
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must contain all letters");
        for (var i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), "");
    });
    test('Valid word input is trimmed, capitalized and added to grid', function (assert) {
        let word ="trial";
        doClueFormInput(" "+word+" ", "");
        assert.equal($("#clue-msg").text(), "");
        let gridCells = getGridCells();
        for (let i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), word[i].toUpperCase());
    });
    test('Updating word replaces existing chars in grid', function (assert) {
        let word = "chnge";
        doClueFormInput("trial", "");
        doClueFormInput(word, "");  // Update the word
        assert.equal($("#clue-msg").text(), "");
        let gridCells = getGridCells();
        for (var i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), word[i].toUpperCase() );
    });

    // Clueform is updated with saved clue and error is cleared
    // Clue is shown as tool tip
    // Clue is checked for no of letters in parenthesis
    // No. of letters added to clue if missing
    // Check if word conflicts with other letters
    // Check letter colors
    // Replaces tool tip if clue is updated
})();

// TEST: existing puzzle initialization sets clues edit mode if words/clues exist
// TEST: existing puzzle initialization loads data, blocks and words into grid








