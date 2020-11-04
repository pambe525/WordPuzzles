/**
 Tests for Class PuzzleEditor
 */
const jqFixtureId = "#qunit-fixture";
const pageTitleId = "page-title", jqPageTitleId = "#" + pageTitleId;
const saveOkId = "save-ok", jqSaveOkId = "#" + saveOkId;
const descId = "desc", jqDescId = "#" + descId;
const shareToggleId = "share-toggle", jqShareToggleId = "#" + shareToggleId;
const saveBtnId = "save", jqSaveBtnId = "#" + saveBtnId;
const deleteBtnId = "delete", jqDeleteBtnId = "#" + deleteBtnId;
const doneBtnId = "done", jqDoneBtnId = "#" + doneBtnId;
const sizeLabelId = "size-label", jqSizeLabelId = "#" + sizeLabelId;
const sizeSelectorId = "size", jqSizeSelectorId = "#" + sizeSelectorId;
const modeToggleId = "mode-toggle", jqModeToggleId = "#" + modeToggleId;
const symmOptionId = "symm-option", jqSymmOptionId = "#" + symmOptionId;
const symmToggleId = "symm-toggle", jqSymmToggleId = "#" + symmToggleId;
const clueFormId = "clue-form", jqClueFormId = "#" + clueFormId;
const clueNumId = "clue-num", jqClueNumId = "#" + clueNumId;
const clueWordId = "clue-word", jqClueWordId = "#" + clueWordId;
const clueTextId = "clue-text", jqClueTextId = "#" + clueTextId;
const clueMsgId = "clue-msg", jqClueMsgId = "#" + clueMsgId;
const clueUpdateId = "clue-update", jqClueUpdateId = "#" + clueUpdateId;
const clueDeleteId = "clue-delete", jqClueDeleteId = "#" + clueDeleteId;
const puzzleDivId = "puzzle", jqPuzzleDivId = "#" + puzzleDivId

// MOCK FUNCTIONS TO REPLACE WINDOWS FUNCTIONS
var confirmMessage = "", confirmResponse = false;
window.confirm = function (message) {
    confirmMessage = message;
    return confirmResponse;
}

var alertMessage = "";
window.alert = function (message) {
    alertMessage = message;
}

var editor, assert = QUnit.assert;

QUnit.module('PuzzleEditor', {
    beforeEach: function () {
        $(jqFixtureId).append($("<div></div>").attr('id', puzzleDivId));
        $(jqFixtureId).append($("<h3></h3>").attr('id', pageTitleId));
        $(jqFixtureId).append($("<span></span>").attr('id', saveOkId));
        $(jqFixtureId).append($("<button></button>").attr('id', saveBtnId));
        $(jqFixtureId).append($("<button></button>").attr('id', deleteBtnId));
        $(jqFixtureId).append($("<button></button>").attr('id', doneBtnId));
        $(jqFixtureId).append($("<input type='text'>").attr('id', descId));
        $(jqFixtureId).append($("<input type='checkbox'>").attr('id', shareToggleId));
        $(jqFixtureId).append($("<label></label>").attr('id', sizeLabelId));
        $(jqFixtureId).append($("<select></select>").attr('id', sizeSelectorId));
        $(jqFixtureId).append($("<input type='checkbox'>").attr('id', modeToggleId));
        $(jqFixtureId).append($("<div></div>").attr('id', symmOptionId));
        $(jqFixtureId).append($("<input type='checkbox'>").attr('id', symmToggleId));
        var form = $("<div></div>").attr("id", clueFormId);
        $(jqFixtureId).append(form);
        form.append($("<span></span>").attr("id", clueNumId));
        form.append($("<input type='text'>").attr("id", clueWordId));
        form.append($("<textarea></textarea>").attr("id", clueTextId));
        form.append($("<span></span>").attr("id", clueMsgId));
        form.append($("<button></button>").attr("id", clueUpdateId));
        form.append($("<button></button>").attr("id", clueDeleteId));
        editor = new PuzzleEditor(puzzleDivId);
    },
});

// Constructor tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Constructor: No argument throws error', function (assert) {
    assert.throws(function () {
        new PuzzleEditor();
    }, /No argument specified on Puzzle/, Error)
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
QUnit.test('initialize: Throws error if any predefined element id is not in DOM', function (assert) {
    editor.IDs.sizeSelect = "noElemId";
    assert.throws(function () {
        editor.initialize();
    }, /noElemId does not exist/, Error);
});

QUnit.test('initialize: Sets UI elements starting states', function (assert) {
    editor.initialize();
    assert.true($(jqSaveOkId).is(":hidden"));       // Check Icon is hidden
    assert.true($(jqDeleteBtnId).prop("disabled")); // Delete button is disabled
    assert.true($(jqClueFormId).is(":hidden"));     // Clue form is hidden
    assert.equal($(jqClueWordId).css("text-transform"), "uppercase");  // Clue entry UPPERCASED
});

QUnit.test('initialize: Sets page tile for Crossword', function (assert) {
    editor.initialize();
});

