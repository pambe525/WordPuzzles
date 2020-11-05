/* MAKE SURE TO INCLUDE mock_edit_puzzle_dom.js in QUnitRunner.html before this test*/

// HELPER FUNCTIONS
//====================================================================================================================
function clickOnCellId(cellId) {
    var coord = cellId.split("-")
    var index = parseInt(coord[0]) * parseInt($(jqSizeSelectorId).val()) + parseInt(coord[1]);
    $(jqPuzzleDivId + ">div")[index].click();
}

// function doClueFormInput(word, clueText) {
//     $(jqClueWordId).val(word);
//     $(jqClueTextId).val(clueText);
//     $(jqClueUpdateId).click();
// }
//
// function assertClueFormFields(clueRef, word, clueText, msg) {
//     assert.equal($(jqClueNumId).text(), clueRef);
//     assert.equal($(jqClueMsgId).text(), msg);
//     assert.equal($(jqClueWordId).val(), word);
//     assert.equal($(jqClueTextId).val(), clueText);
// }

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

// setElementId tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('setElementId: Throws exception if element reference key is incorrect', function (assert) {
    assert.throws(function () {
            editor.setElementId("wrongkey", "selectorId");
        },
        /Invalid element reference wrongkey/, Error);
});

QUnit.test('setElementId: Throws exception if given id does not exist in DOM', function (assert) {
    assert.throws(function () {
            editor.setElementId("sizeSelect", "selectorId");
        },
        /Element id selectorId not found/, Error);
});

QUnit.test('setElementId: Sets element id correctly if it exists', function (assert) {
    editor.setElementId("sizeSelect", "mode-toggle");
    assert.equal(editor.IDs.sizeSelect, "mode-toggle");
});

// setSizeSelector and getSelectedSize tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('setSizeSelector: Sets select options for size', function (assert) {
    var jsonData = {1: "Option1", 2: "Option2", 3: "Option 3"};
    editor.setSizeSelector(jsonData, 2);
    assert.equal($(editor.IDs.sizeSelect + ">option").length, 3);
    assert.equal(editor.getSelectedSize(), 2);
});

// initialize tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('initialize: No argument throws error', function (assert) {
    assert.throws(function () {
        editor.initialize()
    }, /puzzledDivId cannot be null/, Error)
});

QUnit.test('initialize: Throws error if any predefined element id is not in DOM', function (assert) {
    editor.IDs.sizeSelect = "noElemId";
    assert.throws(function () {
        editor.initialize(puzzleDivId);
    }, /noElemId does not exist/, Error);
});

QUnit.test('initialize: Sets UI elements starting states', function (assert) {
    editor.initialize(puzzleDivId);
    assert.true($(jqSaveOkId).is(":hidden"));       // Check Icon is hidden
    assert.true($(jqDeleteBtnId).prop("disabled")); // Delete button is disabled
    assert.true($(jqClueFormId).is(":hidden"));     // Clue form is hidden
    assert.equal($(jqClueWordId).css("text-transform"), "uppercase");  // Clue entry UPPERCASED
    assert.equal($(jqShareToggleId).prop("disabled"), true);
    assert.true($(jqSaveOkId).is(":hidden"));
});

QUnit.test('initialize: Sets page title for Crossword', function (assert) {
    editor.initialize(puzzleDivId);
    assert.equal($(jqPageTitleId).text(), "New Crossword Puzzle");
});

QUnit.test('initialize: Sets labels specific to Crossword', function (assert) {
    editor.initialize(puzzleDivId);
    assert.equal($(jqSizeLabelId).text(), "Grid Size");
    //assert.equal($(jqModeToggleId).attr("data-off"), "Edit Blocks");
    //assert.equal($(jqModeToggleId).attr("data-on"), "Edit Clues");
});

;QUnit.test('initialize: Creates grid using default size of 15', function (assert) {
    assert.equal($(jqPuzzleDivId).children().length, 0);
    editor.initialize(puzzleDivId);
    assert.equal($(jqPuzzleDivId).children().length, 225)
});

// Grid Size Selection change tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Event: Grid Size change redraws grid to new size', function (assert) {
    editor.initialize(puzzleDivId);
    assert.equal($(jqPuzzleDivId + " > div").length, 225);
    $(jqSizeSelectorId).val(5).change();
    assert.equal($(jqPuzzleDivId + " > div").length, 25);
});

QUnit.test('Grid Size change switches to Block edit mode', function (assert) {
    editor.initialize(puzzleDivId);
    assert.equal($(jqPuzzleDivId + " > div").length, 225);
    assert.false($(jqModeToggleId).is(":checked"));
    $(jqModeToggleId).prop("checked", true).change();  // Toogle edit mode
    assert.true($(jqModeToggleId).is(":checked"));
    $(jqSizeSelectorId).val(5).change();  // 5x5 grid size
    assert.false($(jqModeToggleId).is(":checked"));
});

QUnit.test('Grid Size change prompts for confirmation if grid has data', function (assert) {
    editor.initialize(puzzleDivId);
    clickOnCellId("1-0");   // Set a block
    clickOnCellId("0-1");   // Set a block
    confirmResponse = false;                // Cancel confirmation box
    $(jqSizeSelectorId).val(7).change();    // Change to 7x7 grid size
    assert.true(confirmMessage.indexOf("All changes to grid will be cleared") === 0);
    assert.equal($(".xw-blocked").length, 4);   // No change to grid
    assert.equal($(jqSizeSelectorId).val(), 15); // Should revert back to previous selection
});

QUnit.test('Event: Grid Size change redraws new grid if confirmed', function (assert) {
    editor.initialize(puzzleDivId);
    clickOnCellId("1-0");
    clickOnCellId("0-1");
    confirmResponse = true;
    $(jqSizeSelectorId).val(3).change();       // Change to 3x3 grid size
    assert.equal($(".xw-blocked").length, 0);  // Grid changed
    assert.equal(editor.puzzleInstance.size, 3);
    assert.equal(editor.getSelectedSize(), 3)
});

// // Blocks Edit Mode tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Block Edit Mode: Switching back to block selection clears hilites', function (assert) {
//     editor.initialize();
//     $(jqModeSelectorId).prop("checked", true).change();
//     clickOnCellId("0-4");
//     assert.true($(jqGridId + ">div").hasClass("xw-hilited"));
//     $(jqModeSelectorId).prop("checked", false).change();
//     assert.false($(jqGridId + ">div").hasClass("xw-hilited"));
// });
//
// QUnit.test('BlockEdit Mode: Clicking on a cell sets block (in default edit mode)', function (assert) {
//     editor.initialize();
//     assert.equal($(".xw-blocked").length, 0);
//     clickOnCellId("0-4");
//     assert.equal($(".xw-blocked").length, 2); // Including symmetric cell
// });
//
// // Word/Clue Edit Mode tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Clue Edit Mode: Help text is correct and form is visible', function (assert) {
//     editor.initialize();
//     $(jqModeSelectorId).prop("checked", true).change();
//     assert.false($(jqClueFormId).is(":hidden"));
//     assert.true($(jqModeTipId).text().indexOf("ACROSS or DOWN word and its clue") > 0);
// });
//
// QUnit.test('Clue Edit Mode: Switching from word edit to block edit mode hides form', function (assert) {
//     editor.initialize();
//     $(jqModeSelectorId).prop("checked", true).change();
//     $(jqModeSelectorId).prop("checked", false).change();
//     assert.true($(jqClueFormId).is(":hidden"));
// });
//
// QUnit.test('Clue Edit Mode: Switching to this mode disables blocking selected cells', function (assert) {
//     editor.initialize();
//     $(jqModeSelectorId).prop("checked", true).change();
//     clickOnCellId("1-0");
//     assert.equal($(".xw-blocked").length, 0);
// });
//
// QUnit.test('Clue Edit Mode: By default first word is hilited and form is initialized', function (assert) {
//     editor.initialize();
//     $(jqModeSelectorId).prop("checked", true).change();
//     assertClueFormFields("#1 Across (5)", "", "", "")
// });
//
// QUnit.test('Clue Edit Mode: Hiliting a blank grid word sets maxlength of word input field', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     clickOnCellId("0-0");
//     clickOnCellId("0-4");
//     $(jqModeSelectorId).prop("checked", true).change();  // Hilites first across word by default
//     assert.equal($(jqClueWordId).attr("maxlength"), "3");
//     clickOnCellId("1-1");
//     assert.equal($(jqClueWordId).attr("maxlength"), "5");
// });
//
// // Word/Clue Edit Form - Update Grid Btn tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Clue Edit Form: Invalid input in clue form shows error message', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     clickOnCellId("0-0");
//     clickOnCellId("0-4");
//     $(jqModeSelectorId).prop("checked", true).change();
//     $(jqClueWordId).val("AB");
//     $(jqClueUpdateId).click();
//     assert.equal($(jqClueMsgId).text(), "Word must be 3 chars");
// });
//
// QUnit.test('Clue Edit Form: Valid input populates grid word and word data', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     clickOnCellId(("0-0"));
//     clickOnCellId(("0-4"));
//     $(jqModeSelectorId).prop("checked", true).change();
//     assertClueFormFields("#1 Across (3)", "", "", "");
//     doClueFormInput("abc", "clue text");  // 3 letters across
//     assert.equal($(jqClueMsgId).text(), "");
//     assert.equal(editor.Xword.readWord("0-1"), "ABC");
//     assert.equal(editor.Xword.words.across["0-1"].word, "abc");
//     assert.equal(editor.Xword.words.across["0-1"].clue, "clue text (3)");
// });
//
// QUnit.test('Clue Edit Form: Existing stored word and clue populated in form if full word', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
//     assertClueFormFields("#6 Across (5)", "", "", "");
//     clickOnCellId("0-0");
//     assertClueFormFields("#1 Across (5)", "abcde", "clue text (5)", "");
// });
//
// QUnit.test('Clue Edit Form: Word is populated in form if full word is formed by letters in grid', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
//     doClueFormInput("fghij", "clue text"); // 6 ACROSS input updated; next across hilited
//     doClueFormInput("klmno", "clue text"); // 7 ACROSS input updated; next across hilited
//     doClueFormInput("pqrst", "clue text"); // 8 ACROSS input updated; next across hilited
//     doClueFormInput("uvwxy", "clue text"); // 9 ACROSS input updated; next DOWN hilited
//     assertClueFormFields("#1 Down (5)", "AFKPU", "", "");
// });
//
// QUnit.test('Clue Edit Form: Previous message is cleared when input is valid', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     var cells = $(jqGridId + " > div");
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abc", ""); // short word - error msg
//     assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
//     doClueFormInput("abcde", ""); // correct input
//     assert.equal($(jqClueMsgId).text(), "");
// });
//
// QUnit.test('Clue Edit Form: Loading new word in form clears previous message', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abc", ""); // short word - error msg
//     assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
//     clickOnCellId("1-0");
//     assert.equal($(jqClueMsgId).text(), "");
// });
//
// QUnit.test('Clue Edit Form: Form is hidden when all words and clues are complete', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
//     doClueFormInput("fghij", "clue text"); // 6 ACROSS input updated; next across hilited
//     doClueFormInput("klmno", "clue text"); // 7 ACROSS input updated; next across hilited
//     doClueFormInput("pqrst", "clue text"); // 8 ACROSS input updated; next across hilited
//     doClueFormInput("uvwxy", "clue text"); // 9 ACROSS input updated; next DOWN hilited
//     doClueFormInput("afkpu", "clue text"); // 1 DOWN input updated; next across hilited
//     doClueFormInput("bglqv", "clue text"); // 2 DOWN input updated; next across hilited
//     doClueFormInput("chmrw", "clue text"); // 3 DOWN input updated; next across hilited
//     doClueFormInput("dinsx", "clue text"); // 4 DOWN input updated; next across hilited
//     doClueFormInput("ejoty", "clue text"); // 5 DOWN input updated; DONE - FORM IS HIDDEN
//     assert.false($(jqClueFormId).is(":visible"));
// });
//
// // Word/Clue Edit Form - Remove Btn tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Clue Edit Form: Delete Btn removes word from grid', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change(); // By default hilites 1A
//     clickOnCellId("0-0");                // Hilite 1D
//     doClueFormInput("adown", "clue 1D");  // Enter 1D
//     clickOnCellId("0-0");                // Hilite 1A
//     doClueFormInput("acros", "clue 1A");  // Enter 1A
//     clickOnCellId("0-0");                // Hilite 1A
//     $(jqClueDeleteId).click();           // Delete 1A
//     assert.equal(editor.Xword.readWord("0-0", true), "A    ");
//     clickOnCellId("0-0");                // Hilite 1D
//     $(jqClueDeleteId).click();           // Delete 1D
//     assert.equal(editor.Xword.readWord("0-0", false), "     ");
// });
//
// QUnit.test('Clue Edit Form: Delete Btn clears form', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $(jqModeSelectorId).prop("checked", true).change();
//     doClueFormInput("abcde", "clue 1A");
//     clickOnCellId("0-0");
//     $(jqClueDeleteId).click();
//     assertClueFormFields("#1 Across (5)", "", "", "");
// });
//
// // Save Btn and state tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Save Btn: Is enabled by default and dataSaved is false', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved)
// });
//
// QUnit.test('Save Btn: Is disabled and dataSaved is true on successful save', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({id:1}) };
//     $(jqSaveBtnId).click();
//     assert.true($(jqSaveBtnId).prop("disabled"));
//     assert.true(editor.dataSaved);
// });
//
// QUnit.test('Save Btn: On first save, delete btn is enabled', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({id:1}) };
//     $(jqSaveBtnId).click();
//     assert.false($(jqDeleteBtnId).prop("disabled"));
// });
//
// QUnit.test('Save Btn: On successful save saved puzzle id is assigned to xword', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     assert.equal(editor.Xword.id, null);
//     $.ajax = function(dataObj) { dataObj.success({id: 5}) };
//     $(jqSaveBtnId).click();
//     assert.equal(editor.Xword.id, 5);
// });
//
// QUnit.test('Save Btn: Is re-enabled when a cell is blocked or unblocked', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();   // First save the grid to disable Save btn
//     clickOnCellId("0-0");     // Block cell
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved);
//     $(jqSaveBtnId).click(); // Save again to disable Save btn
//     assert.true($(jqSaveBtnId).prop("disabled"));
//     assert.true(editor.dataSaved);
//     clickOnCellId("0-0");   // Unblock cell
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved);
// });
//
// QUnit.test('Save Btn: Is re-enabled when a word or clue is added', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();   // First save the grid to disable Save btn
//     $(jqModeSelectorId).prop("checked", true).change();
//     $(jqClueWordId).val("ABCDE");
//     $(jqClueUpdateId).click();
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved);
// });
//
// QUnit.test('Save Btn: Is re-enabled when a word is deleted', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();   // First save the grid to disable Save btn
//     $(jqModeSelectorId).prop("checked", true).change();
//     $(jqClueWordId).val("ABCDE");
//     $(jqClueUpdateId).click();
//     $(jqSaveBtnId).click();
//     clickOnCellId("0-0");
//     $(jqClueDeleteId).click();
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved);
// });
//
// QUnit.test('Save Btn: Is re-enabled when grid size is changed', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();   // First save the grid to disable Save btn
//     $(jqSizeSelectorId).val(3).change();
//     assert.false($(jqSaveBtnId).prop("disabled"));
//     assert.false(editor.dataSaved);
// });
//
// QUnit.test('Save Btn: After ajax returns with error message', function (assert) {
//     editor.initialize();  // NOTE: Grid is 5x5 by default
//     $.ajax = function(dataObj) { dataObj.success({error_message: "Error occurred"}) }; // Mock Ajax call
//     $(jqSaveBtnId).click();   // First save the grid to disable Save btn
//     assert.equal(alertMessage, "Error occurred");
// });
//
// // InitializeFromData tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('initialize(with data): Throws exception if puzzle data is not an object', function (assert) {
//     assert.throws(function () {
//             editor.initialize(5);
//         }, /Invalid puzzle data/, Error);
// });
//
// QUnit.test('initialize(with data): Throws exception if grid size is not a valid option', function (assert) {
//     var puzzleData = {id: 1, size: 7}
//     assert.throws(function () {
//             editor.initialize(puzzleData);
//         }, /Invalid grid size in puzzle data/, Error);
// });
//
// QUnit.test('initialize(with data): Creates grid using size in puzzle data', function (assert) {
//     var puzzleData = {id: 1, size: 3, data:{blocks:""}}
//     editor.initialize(puzzleData);
//     assert.equal($(jqGridId).children().length, 9)
// });
//
// QUnit.test('initialize(with data): Sets puzzle_id in crossword object', function (assert) {
//     var puzzleData = {id: 28, size: 5, data:{blocks:""}};
//     editor.initialize(puzzleData);
//     assert.equal(editor.Xword.id, 28)
// });
//
// QUnit.test('initialize(with data): Sets blocks in grid using puzzle_data', function (assert) {
//     var puzzleData = {id: 1, size: 5, data:{blocks: "0,2,11,12,13,22,24"}}
//     editor.initialize(puzzleData);
//     var blocked_cells = $(jqGridId).children(".xw-blocked");
//     assert.equal(blocked_cells.length, 7);
//     var blocked_ids = ["0-0", "0-2", "2-1", "2-2", "2-3", "4-2", "4-4"];
//     for (var i = 0; i < blocked_cells.length; i++)
//         assert.true(blocked_ids.includes(blocked_cells[i].id));
// });
//
// QUnit.test('initialize(with data): Sets words in grid using puzzle_data', function (assert) {
//     var puzzleData = {id: 1, size: 5, data:{blocks: "", across:{}, down:{}}}
//     editor.initialize(puzzleData);
//     assert.true(true);
// });
//
// QUnit.test('initialize(with data): Disables Save btn and enables Delete btn on load', function (assert) {
//     var puzzleData = {id: 1, size: 5, data:{blocks: "", across:{}, down:{}}}
//     editor.initialize(puzzleData);
//     assert.true($(jqSaveBtnId).prop("disabled"));
//     assert.false($(jqDeleteBtnId).prop("disabled"));
// });
//
// // Delete btn tests
// //--------------------------------------------------------------------------------------------------------------------
// QUnit.test('Delete Btn: Show confirmation box', function (assert) {
//     editor.initialize();
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();   // First save the grid to enable Delete btn
//     confirmResponse = false;                // Cancel confirmation box
//     $(jqDeleteBtnId).click();    // Change to 3x3 grid size
//     assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
//     assert.equal($(jqGridId).children().length, 25)
// });
//
// QUnit.test('Delete Btn: Show confirmation box (cancel)', function (assert) {
//     editor.initialize();
//     $.ajax = function(dataObj) { dataObj.success({puzzle_id: 5}) };
//     $(jqSaveBtnId).click();      // First save the grid to enable Delete btn
//     confirmResponse = false;     // Cancel confirmation box
//     $(jqDeleteBtnId).click();
//     assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
//     assert.equal($(jqGridId).children().length, 25)
// });


