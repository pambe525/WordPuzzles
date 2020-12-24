/* MAKE SURE TO INCLUDE mock_edit_puzzle_dom.js in QUnitRunner.html before this test*/

// HELPER FUNCTIONS
//====================================================================================================================
function clickOnCellId(cellId) {
    var coord = cellId.split("-")
    var index = parseInt(coord[0]) * parseInt($(jqSizeSelectorId).val()) + parseInt(coord[1]);
    $(jqPuzzleDivId + ">div")[index].click();
}

function doClueFormInput(word, clueText) {
    $(jqClueWordId).val(word);
    $(jqClueTextId).val(clueText);
    $(jqClueUpdateId).click();
}

function assertClueFormFields(clueRef, word, clueText, msg) {
    assert.equal($(jqClueNumId).text(), clueRef);
    assert.equal($(jqClueMsgId).text(), msg);
    assert.equal($(jqClueWordId).val(), word);
    assert.equal($(jqClueTextId).val(), clueText);
}

function mockAjaxMethod(returnId=1, returnMsg="") {
    $.ajax = function (dataObj) {
        dataObj.success({id: returnId, error_message: returnMsg})
    };
}

/**
 Tests for Class CrosswordEditor
 */

var editor, assert = QUnit.assert;

QUnit.module('CrosswordEditor', {
    beforeEach: function () {
        setupDOM();
        editor = new CrosswordEditor();
    },
});

// Blocks Edit Mode tests
//--------------------------------------------------------------------------------------------------------------------

QUnit.test('Block Edit Mode: Switching back to block edit clears hilites', function (assert) {
    editor.initialize();
    $(jqModeToggleId).prop("checked", true).change();
    clickOnCellId("0-4");
    assert.true($(jqPuzzleDivId + "> div").hasClass("xw-hilited"));
    $(jqModeToggleId).prop("checked", false).change();
    assert.false($(jqPuzzleDivId + ">div").hasClass("xw-hilited"));
});

QUnit.test('BlockEdit Mode: Clicking on a cell sets block (in default edit mode)', function (assert) {
    editor.initialize();
    assert.equal($(".xw-blocked").length, 0);
    clickOnCellId("0-4");
    assert.equal($(".xw-blocked").length, 2); // Including symmetric cell
});

// Word/Clue Edit Mode tests
//--------------------------------------------------------------------------------------------------------------------

QUnit.test('Clue Edit Mode: Switching to this mode disables blocking selected cells', function (assert) {
    editor.initialize();
    $(jqModeToggleId).prop("checked", true).change();
    clickOnCellId("1-0");
    assert.equal($(".xw-blocked").length, 0);
});

QUnit.test('Clue Edit Mode: By default first word is hilited and form is initialized', function (assert) {
    editor.initialize();
    $(jqModeToggleId).prop("checked", true).change();
    assertClueFormFields("#1 Across (15)", "", "", "")
});

QUnit.test('Clue Edit Mode: Hiliting a blank grid word sets maxlength of word input field', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    clickOnCellId("0-0");
    clickOnCellId("0-4");
    $(jqModeToggleId).prop("checked", true).change();  // Hilites first across word by default
    assert.equal($(jqClueWordId).attr("maxlength"), "3");
    clickOnCellId("1-1");
    assert.equal($(jqClueWordId).attr("maxlength"), "5");
});

// Word/Clue Edit Form - Update Grid Btn tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Clue Edit Form: Invalid input in clue form shows error message', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    clickOnCellId("0-0");
    clickOnCellId("0-4");
    $(jqModeToggleId).prop("checked", true).change();
    $(jqClueWordId).val("AB");
    $(jqClueUpdateId).click();
    assert.equal($(jqClueMsgId).text(), "Word must be 3 chars");
});

QUnit.test('Clue Edit Form: Valid input populates grid word and word data', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    clickOnCellId(("0-0"));
    clickOnCellId(("0-4"));
    $(jqModeToggleId).prop("checked", true).change();
    assertClueFormFields("#1 Across (3)", "", "", "");
    doClueFormInput("abc", "clue text");  // 3 letters across
    assert.equal($(jqClueMsgId).text(), "");
    assert.equal(editor.puzzleInstance.readWord("0-1"), "ABC");
    assert.equal(editor.puzzleInstance.words.across["0-1"].word, "abc");
    assert.equal(editor.puzzleInstance.words.across["0-1"].clue, "clue text (3)");
});

QUnit.test('Clue Edit Form: Existing stored word and clue populated in form if full word', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
    assertClueFormFields("#6 Across (5)", "", "", "");
    clickOnCellId("0-0");
    assertClueFormFields("#1 Across (5)", "abcde", "clue text (5)", "");
});

QUnit.test('Clue Edit Form: Word is populated in form if full word is formed by letters in grid', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
    doClueFormInput("fghij", "clue text"); // 6 ACROSS input updated; next across hilited
    doClueFormInput("klmno", "clue text"); // 7 ACROSS input updated; next across hilited
    doClueFormInput("pqrst", "clue text"); // 8 ACROSS input updated; next across hilited
    doClueFormInput("uvwxy", "clue text"); // 9 ACROSS input updated; next DOWN hilited
    assertClueFormFields("#1 Down (5)", "AFKPU", "", "");
});

QUnit.test('Clue Edit Form: Previous message is cleared when input is valid', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    var cells = $(jqGridId + " > div");
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abc", ""); // short word - error msg
    assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
    doClueFormInput("abcde", ""); // correct input
    assert.equal($(jqClueMsgId).text(), "");
});

QUnit.test('Clue Edit Form: Loading new word in form clears previous message', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abc", ""); // short word - error msg
    assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
    clickOnCellId("1-0");
    assert.equal($(jqClueMsgId).text(), "");
});

QUnit.test('Clue Edit Form: Form is hidden when all words and clues are complete', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
    doClueFormInput("fghij", "clue text"); // 6 ACROSS input updated; next across hilited
    doClueFormInput("klmno", "clue text"); // 7 ACROSS input updated; next across hilited
    doClueFormInput("pqrst", "clue text"); // 8 ACROSS input updated; next across hilited
    doClueFormInput("uvwxy", "clue text"); // 9 ACROSS input updated; next DOWN hilited
    doClueFormInput("afkpu", "clue text"); // 1 DOWN input updated; next across hilited
    doClueFormInput("bglqv", "clue text"); // 2 DOWN input updated; next across hilited
    doClueFormInput("chmrw", "clue text"); // 3 DOWN input updated; next across hilited
    doClueFormInput("dinsx", "clue text"); // 4 DOWN input updated; next across hilited
    doClueFormInput("ejoty", "clue text"); // 5 DOWN input updated; DONE - FORM IS HIDDEN
    assert.false($(jqClueFormId).is(":visible"));
});

// Word/Clue Edit Form - Remove Btn tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Clue Edit Form: Delete Btn removes word from grid', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change(); // By default hilites 1A
    clickOnCellId("0-0");                // Hilite 1D
    doClueFormInput("adown", "clue 1D");  // Enter 1D
    clickOnCellId("0-0");                // Hilite 1A
    doClueFormInput("acros", "clue 1A");  // Enter 1A
    clickOnCellId("0-0");                // Hilite 1A
    $(jqClueDeleteId).click();           // Delete 1A
    assert.equal(editor.puzzleInstance.readWord("0-0", true), "A    ");
    clickOnCellId("0-0");                // Hilite 1D
    $(jqClueDeleteId).click();           // Delete 1D
    assert.equal(editor.puzzleInstance.readWord("0-0", false), "     ");
});

QUnit.test('Clue Edit Form: Delete Btn clears form', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    $(jqSizeSelectorId).val(5).change();
    $(jqModeToggleId).prop("checked", true).change();
    doClueFormInput("abcde", "clue 1A");
    clickOnCellId("0-0");
    $(jqClueDeleteId).click();
    assertClueFormFields("#1 Across (5)", "", "", "");
});

// Save Btn and state tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Save Btn: dataSaved is false when a word or clue is added', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    mockAjaxMethod(5);
    $(jqSaveBtnId).click();   // First save the grid
    $(jqModeToggleId).prop("checked", true).change();
    $(jqClueWordId).val("ABCDEFGHIJKLMNO");
    $(jqClueUpdateId).click();
    assert.false(editor.dataSaved);
});

QUnit.test('Save Btn: dataSaved is false when a word is deleted', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    mockAjaxMethod(5);
    $(jqSaveBtnId).click();   // First save the grid
    $(jqModeToggleId).prop("checked", true).change();
    $(jqClueWordId).val("ABCDEFGHIJKLMNO");
    $(jqClueUpdateId).click();
    $(jqSaveBtnId).click();
    clickOnCellId("0-0");
    $(jqClueDeleteId).click();
    assert.false(editor.dataSaved);
});

QUnit.test('Save Btn: Saves share setting when true', function (assert) {
    editor.initialize();  // NOTE: Grid is 15x15 by default
    mockAjaxMethod(1);
    $(jqShareBtnId).prop("checked", true);
    $(jqSaveBtnId).click();   // First save the grid
    assert.equal(editor.puzzleInstance.sharedAt, new Date().toUTCString());
    $(jqShareBtnId).prop("checked", false);
    $(jqSaveBtnId).click();   // Save the grid
    assert.equal(editor.puzzleInstance.sharedAt, null);
});

// InitializeFromData tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('initialize(with data): Throws exception if puzzle data is not an object', function (assert) {
    assert.throws(function () {
            editor.initialize(5);
        }, /Invalid puzzle data/, Error);
});

QUnit.test('initialize(with data): Throws exception if grid size is not a valid option', function (assert) {
    var puzzleData = {id: 1, size: 4}
    assert.throws(function () {
            editor.initialize(puzzleData);
        }, /Invalid grid size in puzzle data/, Error);
});

QUnit.test('initialize(with data): Creates grid using size in puzzle data', function (assert) {
    var puzzleData = {id: 1, size: 5, data:{blocks:""}}
    editor.initialize(puzzleData);
    assert.equal($(jqPuzzleDivId).children().length, 25)
});

QUnit.test('initialize(with data): Sets puzzle_id in crossword object', function (assert) {
    var puzzleData = {id: 28, size: 5, data:{blocks:""}};
    editor.initialize(puzzleData);
    assert.equal(editor.puzzleInstance.id, 28)
});

QUnit.test('initialize(with data): Sets blocks in grid using puzzle_data', function (assert) {
    var puzzleData = {id: 1, size: 5, data:{blocks: "0,2,11,12,13,22,24"}}
    editor.initialize(puzzleData);
    var blocked_cells = $(jqPuzzleDivId).children(".xw-blocked");
    assert.equal(blocked_cells.length, 7);
    var blocked_ids = ["0-0", "0-2", "2-1", "2-2", "2-3", "4-2", "4-4"];
    for (var i = 0; i < blocked_cells.length; i++)
        assert.true(blocked_ids.includes(blocked_cells[i].id));
});

QUnit.test('initialize(with data): Disables Save btn and enables Delete btn on load', function (assert) {
    var puzzleData = {id: 1, size: 5, data:{blocks: "", across:{}, down:{}}}
    editor.initialize(puzzleData);
    assert.true($(jqSaveBtnId).prop("disabled"));
    assert.false($(jqDeleteBtnId).prop("disabled"));
});

QUnit.test('initialize(with data): Sets correct page title using puzzle id', function (assert) {
    var puzzleData = {id: 3, size: 5, data:{blocks: "", across:{}, down:{}}}
    editor.initialize(puzzleData);
    assert.equal($(jqPageTitleId).text(), "Edit Crossword Puzzle #3");
});



