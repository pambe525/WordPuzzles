/**
  Tests for Class CrosswordEditor
 */

var jqFixtureId = "#qunit-fixture";
var gridId = "xw-grid", jqGridId = "#"+gridId;
var sizeSelectorId = "grid-size", jqSizeSelectorId = "#"+sizeSelectorId;
var resetBtnId = "reset-grid", jqResetBtnId = "#"+resetBtnId;
var modeSelectorId = "edit-mode", jqModeSelectorId = "#"+modeSelectorId;
var modeTipId = "mode-tip", jqModeTipId = "#"+modeTipId;
var saveBtnId = "save-grid", jqSaveBtnId = "#"+saveBtnId;

var clueFormId = "clue-form", jqClueFormId = "#"+clueFormId;
var clueNumId  = "clue-num", jqClueNumId = "#"+clueNumId;
var clueWordId = "clue-word", jqClueWordId = "#"+clueWordId;
var clueHintId = "clue-hint", jqClueHintId = "#"+clueHintId;
var clueTextId = "clue-text", jqClueTextId = "#"+clueTextId;
var clueMsgId = "clue-msg", jqClueMsgId = "#"+clueMsgId;
var clueUpdateId = "clue-update", jqClueUpdateId= "#"+clueUpdateId;

var confirmMessage = "", confirmResponse=false;
window.confirm = function(message) {
    confirmMessage = message;
    return confirmResponse;
}

var editor;

QUnit.module('CrosswordEditor', {
  beforeEach: function() {
      $(jqFixtureId).append($("<div></div>").attr('id',gridId));
      $(jqFixtureId).append($("<select></select>").attr('id',sizeSelectorId));
      $(jqSizeSelectorId).append($("<option value=3>3x3</option>"))
                         .append($("<option value=5 selected>5x5</option>"));
      $(jqFixtureId).append($("<button></button>").attr('id',resetBtnId));
      $(jqFixtureId).append($("<select></select>").attr('id',modeSelectorId));
      $(jqModeSelectorId).append($("<option value=1 selected>Block Mode</option>"))
                         .append($("<option value=2>Word Clue Mode</option>"));
      $(jqFixtureId).append($("<span></span>").attr('id',modeTipId));
      $(jqFixtureId).append($("<button></button>").attr('id',saveBtnId));
      var form = $("<div></div>").attr("id", clueFormId);
      $(jqFixtureId).append(form);
      form.append($("<span></span>").attr("id", clueNumId));
      form.append($("<input type='text'>").attr("id", clueWordId));
      form.append($("<span></span>").attr("id", clueHintId));
      form.append($("<span></span>").attr("id", clueMsgId));
      form.append($("<textarea></textarea>").attr("id", clueTextId));
      form.append($("<button></button>").attr("id", clueUpdateId));
      editor = new CrosswordEditor(gridId);
  },
});

//--------------------------------------------------------------------------------------------------------------------
// initialize tests
//
QUnit.test('initialize: Throws error if any element does not exist', function(assert) {
    editor.IDs["selectorSize"] = "noElemId";
    assert.throws(function(){ editor.initialize(); },
      /noElemId does not exist/, Error);
});

QUnit.test('initialize: Creates grid using default size', function(assert) {
    assert.equal($(jqGridId).children().length, 0);
    editor.initialize();
    assert.equal($(jqGridId).children().length, 25)
});

QUnit.test('initialize: Sets help text based on select edit mode', function(assert) {
    editor.initialize();
    assert.true($(jqModeTipId).text().indexOf("Diametrically opposite square") > 0);
});

QUnit.test('initialize: Disables reset button by default', function(assert) {
    editor.initialize();
    assert.true($(jqResetBtnId).prop('disabled'));
});

QUnit.test('initialize: Hides clue entry form by default', function(assert) {
    editor.initialize();
    assert.true($(jqClueFormId).is(":hidden"));
});

//--------------------------------------------------------------------------------------------------------------------
// setElementId tests
//
QUnit.test('setElementId: Throws exception if element reference key is incorrect', function(assert) {
    assert.throws(function(){ editor.setElementId("wrongkey","selectorId"); },
      /Invalid element reference wrongkey/, Error);
});

QUnit.test('setElementId: Throws exception if element id does not exist', function(assert) {
    assert.throws(function(){ editor.setElementId("selectSize","selectorId"); },
      /Element id selectorId not found/, Error);
});

QUnit.test('setElementId: Sets element id correctly if it exists', function(assert) {
    editor.setElementId("selectSize","edit-mode");
    assert.equal(editor.IDs["selectSize"], "edit-mode");
});
//--------------------------------------------------------------------------------------------------------------------
// Grid Size Selection change tests
//
QUnit.test('Grid Size change redraws grid to new size', function(assert) {
    editor.initialize();
    assert.equal($(jqGridId + " > div").length, 25);
    $(jqSizeSelectorId).val(3).change();
    assert.equal($(jqGridId + " > div").length, 9);
});

//--------------------------------------------------------------------------------------------------------------------
// Blocks Edit Mode tests
//
QUnit.test('Block Edit Mode: Switching back to block selection clears hilites', function(assert) {
    editor.initialize();
    $(jqModeSelectorId).val(2).change();
    $(jqGridId + " > div")[4].click();
    assert.true($(jqGridId+">div").hasClass("xw-hilited"));
    $(jqModeSelectorId).val(1).change();
    assert.false($(jqGridId+">div").hasClass("xw-hilited"));
});

QUnit.test('BlockEdit Mode: Clicking on a cell sets block (in default edit mode)', function(assert) {
    editor.initialize();
    assert.equal($(".xw-blocked").length, 0);
    $(jqGridId + " > div")[4].click();
    assert.equal($(".xw-blocked").length, 2); // Including symmetric cell
});

QUnit.test('BlockEdit Mode: Blocking a cell enables Reset button and disables size selector', function(assert) {
    editor.initialize();
    assert.true($(jqResetBtnId).prop('disabled'));
    assert.false($(jqSizeSelectorId).prop('disabled'));
    $(jqGridId + " > div")[4].click();
    assert.false($(jqResetBtnId).prop('disabled'));
    assert.true($(jqSizeSelectorId).prop('disabled'));
});
//--------------------------------------------------------------------------------------------------------------------
// Reset button tests
//
QUnit.test('Reset Grid button clicked: ClickHandler asks for confirmation', function(assert) {
    editor.initialize();
    $(jqGridId + " > div")[5].click();
    $(jqGridId + " > div")[1].click();
    confirmResponse = false;
    $(jqResetBtnId).click();
    assert.true(confirmMessage.indexOf("All changes to grid will be lost") === 0);
    assert.equal($(".xw-blocked").length, 4);
});

QUnit.test('Reset Grid button clicked: Resets grid if confirmed', function(assert) {
    editor.initialize();
    $(jqGridId + " > div")[5].click();
    confirmResponse = true;
    $(jqResetBtnId).click();
    assert.equal($(".xw-blocked").length, 0); // Including symmetric cell
});

QUnit.test('Reset Grid button clicked: Deactives Reset button after grid is reset', function(assert) {
    editor.initialize();
    $(jqGridId + " > div")[5].click();
    confirmResponse = true;
    $(jqResetBtnId).click();
    assert.true($(jqResetBtnId).prop('disabled'));
    assert.false($(jqSizeSelectorId).prop('disabled'));
});

//--------------------------------------------------------------------------------------------------------------------
// Word/Clue Edit Mode tests
//
QUnit.test('Clue Edit Mode: In this mode help text is correct and form is visible', function(assert) {
    editor.initialize();
    $(jqModeSelectorId).val(2).change();
    assert.true($(jqModeTipId).text().indexOf("Click on a numbered square") === 0);
    assert.false($(jqClueFormId).is(":hidden"));
});

QUnit.test('Clue Edit Mode: Switching away from this mode hides form', function(assert) {
    editor.initialize();
    $(jqModeSelectorId).val(2).change();
    $(jqModeSelectorId).val(1).change();
    assert.true($(jqClueFormId).is(":hidden"));
});

QUnit.test('Clue Edit Mode: Switching to this mode disables blocking selected cells', function(assert) {
    editor.initialize();
    $(jqModeSelectorId).val(2).change();
    $(jqGridId + " > div")[5].click();
    assert.equal($(".xw-blocked").length, 0);
});

QUnit.test('Clue Edit Mode: Hiliting a blank grid word initializes form', function(assert) {
    editor.initialize();
    $(jqModeSelectorId).val(2).change();
    $(jqGridId + " > div")[0].click();
    assert.equal($(jqClueNumId).text(), "#1 Across");
    assert.equal($(jqClueHintId).text(), "(5)");
    assert.equal($(jqClueMsgId).text(), "");
    assert.equal($(jqClueWordId).val(), "");
    assert.equal($(jqClueTextId).val(), "");
});

QUnit.test('Clue Edit Mode: Hiliting a blank grid word sets maxlength of word input field', function(assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    var cells = $(jqGridId + " > div");
    cells[0].click();
    cells[4].click();
    $(jqModeSelectorId).val(2).change();
    cells[1].click();
    assert.equal($(jqClueWordId).attr("maxlength"), "3");
    cells[7].click();
    assert.equal($(jqClueWordId).attr("maxlength"), "5");
});

QUnit.test('Clue Edit Mode: Invalid input in clue form shows error message', function(assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    var cells = $(jqGridId + " > div");
    cells[0].click();
    cells[4].click();
    $(jqModeSelectorId).val(2).change();
    cells[1].click();
    $(jqClueWordId).val("AB");
    $(jqClueUpdateId).click();
    assert.equal($(jqClueMsgId).text(), "Word must be 3 chars");
});

QUnit.test('Clue Edit Mode: Valid input populates grid word', function(assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    var cells = $(jqGridId + " > div");
    cells[0].click();
    cells[4].click();
    $(jqModeSelectorId).val(2).change();
    cells[1].click();
    $(jqClueWordId).val("abc");
    $(jqClueUpdateId).click();
    assert.equal($(jqClueMsgId).text(), "");
    assert.equal($(cells[1]).children(".xw-letter").text(), "A");
    assert.equal($(cells[2]).children(".xw-letter").text(), "B");
    assert.equal($(cells[3]).children(".xw-letter").text(), "C");
});

QUnit.test('Clue Edit Mode: Existing letters are populated in form for full word', function(assert) {
    editor.initialize();  // NOTE: Grid is 5x5 by default
    var cells = $(jqGridId + " > div");
    $(jqModeSelectorId).val(2).change();
    cells[0].click();  // Cell to be populated first
    $(jqClueWordId).val("abcde");
    $(jqClueUpdateId).click();
    cells[6].click();  // Click another cell
    cells[0].click();  // Click populated cell
    assert.equal($(jqClueWordId).val(), "ABCDE");
});