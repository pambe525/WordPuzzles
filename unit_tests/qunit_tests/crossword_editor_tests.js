/**
 Tests for Class CrosswordEditor
 */
var gridId = "xw-grid", jqGridId = "#" + gridId
const jqFixtureId = "#qunit-fixture";
const sizeSelectorId = "grid-size", jqSizeSelectorId = "#" + sizeSelectorId;
const modeSelectorId = "edit-toggle", jqModeSelectorId = "#" + modeSelectorId;
const modeTipId = "mode-tip", jqModeTipId = "#" + modeTipId;
const saveBtnId = "save-grid", jqSaveBtnId = "#" + saveBtnId;
const clueFormId = "clue-form", jqClueFormId = "#" + clueFormId;
const clueNumId = "clue-num", jqClueNumId = "#" + clueNumId;
const clueWordId = "clue-word", jqClueWordId = "#" + clueWordId;
const clueTextId = "clue-text", jqClueTextId = "#" + clueTextId;
const clueMsgId = "clue-msg", jqClueMsgId = "#" + clueMsgId;
const clueUpdateId = "clue-update", jqClueUpdateId = "#" + clueUpdateId;
const clueDeleteId = "clue-delete", jqClueDeleteId = "#" + clueDeleteId;
const doneBtnId = "done", jqDoneBtnId = "#" + doneBtnId;

var confirmMessage = "", confirmResponse = false;
window.confirm = function (message) {
    confirmMessage = message;
    return confirmResponse;
}

var editor, assert = QUnit.assert;

QUnit.module('CrosswordEditor', {
    beforeEach: function () {
        $(jqFixtureId).append($("<div></div>").attr('id', gridId));
        $(jqFixtureId).append($("<select></select>").attr('id', sizeSelectorId));
        $(jqSizeSelectorId).append($("<option value=3>3x3</option>"))
            .append($("<option value=5 selected>5x5</option>"));
        $(jqFixtureId).append($("<input type='checkbox'>").attr('id', modeSelectorId));
        $(jqModeSelectorId).append($("<option value=1 selected>Block Mode</option>"))
            .append($("<option value=2>Word Clue Mode</option>"));
        $(jqFixtureId).append($("<div></div>").attr('id', modeTipId));
        $(jqFixtureId).append($("<button></button>").attr('id', saveBtnId));
        $(jqFixtureId).append($("<button></button>").attr('id', doneBtnId));
        var form = $("<div></div>").attr("id", clueFormId);
        $(jqFixtureId).append(form);
        form.append($("<span></span>").attr("id", clueNumId));
        form.append($("<input type='text'>").attr("id", clueWordId));
        form.append($("<span></span>").attr("id", clueMsgId));
        form.append($("<textarea></textarea>").attr("id", clueTextId));
        form.append($("<button></button>").attr("id", clueUpdateId));
        form.append($("<button></button>").attr("id", clueDeleteId));
        editor = new CrosswordEditor(gridId);
    },
});

// initialize tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('initialize: Throws error if any element does not exist', function (assert) {
    editor.IDs["selectorSize"] = "noElemId";
    assert.throws(function () {
            editor.initialize();
        }, /noElemId does not exist/, Error);
});

QUnit.test('initialize: Creates grid using default size', function (assert) {
    assert.equal($(jqGridId).children().length, 0);
    editor.initialize();
    assert.equal($(jqGridId).children().length, 25)
});

QUnit.test('initialize: Sets help text for default block edit mode', function (assert) {
    editor.initialize();
    assert.false($(jqModeSelectorId).is(":checked"));
    assert.true($(jqModeTipId).is(":visible"));
    assert.true($(jqModeTipId).text().indexOf("Diametrically opposite square") > 0);
});

QUnit.test('initialize: Hides clue entry form by default', function (assert) {
    editor.initialize();
    assert.true($(jqClueFormId).is(":hidden"));
});

// setElementId tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('setElementId: Throws exception if element reference key is incorrect', function (assert) {
    assert.throws(function () {
            editor.setElementId("wrongkey", "selectorId");
        },
        /Invalid element reference wrongkey/, Error);
});

QUnit.test('setElementId: Throws exception if element id does not exist', function (assert) {
    assert.throws(function () {
            editor.setElementId("selectSize", "selectorId");
        },
        /Element id selectorId not found/, Error);
});

QUnit.test('setElementId: Sets element id correctly if it exists', function (assert) {
    editor.setElementId("selectSize", "edit-toggle");
    assert.equal(editor.IDs["selectSize"], "edit-toggle");
});

// Grid Size Selection change tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Grid Size change redraws grid to new size', function (assert) {
    editor.initialize();
    assert.equal($(jqGridId + " > div").length, 25);
    $(jqSizeSelectorId).val(3).change();
    assert.equal($(jqGridId + " > div").length, 9);
});

QUnit.test('Grid Size change switches to Block edit mode', function (assert) {
    editor.initialize();
    assert.equal($(jqGridId + " > div").length, 25);
    assert.false($(jqModeSelectorId).is(":checked"));
    $(jqModeSelectorId).prop("checked", true).change();  // Toogle edit mode
    assert.true($(jqModeSelectorId).is(":checked"));
    $(jqSizeSelectorId).val(3).change();  // 9x9 grid size
    assert.false($(jqModeSelectorId).is(":checked"));
});

QUnit.test('Grid Size change prompts for confirmation if grid has data', function (assert) {
    editor.initialize();
    clickOnCellId("1-0");
    clickOnCellId("0-1");
    confirmResponse = false;                // Cancel confirmation box
    $(jqSizeSelectorId).val(3).change();    // Change to 3x3 grid size
    assert.true(confirmMessage.indexOf("All changes to grid will be cleared") === 0);
    assert.equal($(".xw-blocked").length, 4);  // No change to grid
    assert.equal($(jqSizeSelectorId).val(), 5);
});

QUnit.test('Grid Size change changes grid if confirmed', function (assert) {
    editor.initialize();
    clickOnCellId("1-0");
    clickOnCellId("0-1");
    confirmResponse = true;
    $(jqSizeSelectorId).val(3).change();       // Change to 3x3 grid size
    assert.equal($(".xw-blocked").length, 0);  // Grid changed
    assert.equal($(jqSizeSelectorId).val(), 3);
    assert.equal(editor.Xword.gridSize, 3)
});

// Blocks Edit Mode tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Block Edit Mode: Switching back to block selection clears hilites', function (assert) {
    editor.initialize();
    $(jqModeSelectorId).prop("checked", true).change();
    clickOnCellId("0-4");
    assert.true($(jqGridId + ">div").hasClass("xw-hilited"));
    $(jqModeSelectorId).prop("checked", false).change();
    assert.false($(jqGridId + ">div").hasClass("xw-hilited"));
});

QUnit.test('BlockEdit Mode: Clicking on a cell sets block (in default edit mode)', function (assert) {
    editor.initialize();
    assert.equal($(".xw-blocked").length, 0);
    clickOnCellId("0-4");
    assert.equal($(".xw-blocked").length, 2); // Including symmetric cell
});

// Word/Clue Edit Mode tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Clue Edit Mode: Help text is correct and form is visible', function (assert) {
    editor.initialize();
    $(jqModeSelectorId).prop("checked", true).change();
    assert.false($(jqClueFormId).is(":hidden"));
    assert.true($(jqModeTipId).text().indexOf("ACROSS or DOWN word and its clue") > 0);
});

QUnit.test('Clue Edit Mode: Switching from word edit to block edit mode hides form', function (assert) {
    editor.initialize();
    $(jqModeSelectorId).prop("checked", true).change();
    $(jqModeSelectorId).prop("checked", false).change();
    assert.true($(jqClueFormId).is(":hidden"));
});

QUnit.test('Clue Edit Mode: Switching to this mode disables blocking selected cells', function (assert) {
    editor.initialize();
    $(jqModeSelectorId).prop("checked", true).change();
    clickOnCellId("1-0");
    assert.equal($(".xw-blocked").length, 0);
});

QUnit.test('Clue Edit Mode: By default first word is hilited and form is initialized', function (assert) {
    editor.initialize();
    $(jqModeSelectorId).prop("checked", true).change();
    assertClueFormFields("#1 Across (5)", "", "", "")
});

QUnit.test('Clue Edit Mode: Hiliting a blank grid word sets maxlength of word input field', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    clickOnCellId("0-0");
    clickOnCellId("0-4");
    $(jqModeSelectorId).prop("checked", true).change();  // Hilites first across word by default
    assert.equal($(jqClueWordId).attr("maxlength"), "3");
    clickOnCellId("1-1");
    assert.equal($(jqClueWordId).attr("maxlength"), "5");
});

// Word/Clue Edit Form - Update Grid Btn tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Clue Edit Form: Invalid input in clue form shows error message', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    clickOnCellId("0-0");
    clickOnCellId("0-4");
    $(jqModeSelectorId).prop("checked", true).change();
    $(jqClueWordId).val("AB");
    $(jqClueUpdateId).click();
    assert.equal($(jqClueMsgId).text(), "Word must be 3 chars");
});

QUnit.test('Clue Edit Form: Valid input populates grid word and word data', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    clickOnCellId(("0-0"));
    clickOnCellId(("0-4"));
    $(jqModeSelectorId).prop("checked", true).change();
    assertClueFormFields("#1 Across (3)", "", "", "");
    doClueFormInput("abc", "clue text");  // 3 letters across
    assert.equal($(jqClueMsgId).text(), "");
    assert.equal(editor.Xword.readWord("0-1"), "ABC");
    assert.equal(editor.Xword.words.across["0-1"].word, "abc");
    assert.equal(editor.Xword.words.across["0-1"].clue, "clue text (3)");
});

QUnit.test('Clue Edit Form: Existing stored word and clue populated in form if full word', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change();
    doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
    assertClueFormFields("#6 Across (5)", "", "", "");
    clickOnCellId("0-0");
    assertClueFormFields("#1 Across (5)", "abcde", "clue text (5)", "");
});

QUnit.test('Clue Edit Form: Word is populated in form if full word is formed by letters in grid', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change();
    doClueFormInput("abcde", "clue text"); // 1 ACROSS input updated; next across hilited
    doClueFormInput("fghij", "clue text"); // 6 ACROSS input updated; next across hilited
    doClueFormInput("klmno", "clue text"); // 7 ACROSS input updated; next across hilited
    doClueFormInput("pqrst", "clue text"); // 8 ACROSS input updated; next across hilited
    doClueFormInput("uvwxy", "clue text"); // 9 ACROSS input updated; next DOWN hilited
    assertClueFormFields("#1 Down (5)", "AFKPU", "", "");
});

QUnit.test('Clue Edit Form: Previous message is cleared when input is valid', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    var cells = $(jqGridId + " > div");
    $(jqModeSelectorId).prop("checked", true).change();
    doClueFormInput("abc", ""); // short word - error msg
    assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
    doClueFormInput("abcde", ""); // correct input
    assert.equal($(jqClueMsgId).text(), "");
});

QUnit.test('Clue Edit Form: Loading new word in form clears previous message', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change();
    doClueFormInput("abc", ""); // short word - error msg
    assert.equal($(jqClueMsgId).text(), "Word must be 5 chars");
    clickOnCellId("1-0");
    assert.equal($(jqClueMsgId).text(), "");
});

QUnit.test('Clue Edit Form: Form is hidden when all words and clues are complete', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change();
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
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change(); // By default hilites 1A
    clickOnCellId("0-0");                // Hilite 1D
    doClueFormInput("adown", "clue 1D");  // Enter 1D
    clickOnCellId("0-0");                // Hilite 1A
    doClueFormInput("acros", "clue 1A");  // Enter 1A
    clickOnCellId("0-0");                // Hilite 1A
    $(jqClueDeleteId).click();           // Delete 1A
    assert.equal(editor.Xword.readWord("0-0", true), "A    ");
    clickOnCellId("0-0");                // Hilite 1D
    $(jqClueDeleteId).click();           // Delete 1D
    assert.equal(editor.Xword.readWord("0-0", false), "     ");
});

QUnit.test('Clue Edit Form: Delete Btn clears form', function (assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    $(jqModeSelectorId).prop("checked", true).change();
    doClueFormInput("abcde", "clue 1A");
    clickOnCellId("0-0");
    $(jqClueDeleteId).click();
    assertClueFormFields("#1 Across (5)", "", "", "");
});

// HELPER FUNCTIONS
//====================================================================================================================
function clickOnCellId(cellId) {
    var coord = cellId.split("-")
    var index = parseInt(coord[0]) * parseInt($(jqSizeSelectorId).val()) + parseInt(coord[1]);
    $(jqGridId + ">div")[index].click();
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
