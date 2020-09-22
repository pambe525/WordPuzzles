/*
  Tests for Class CrosswordEditor
  */

var jqFixtureId = "#qunit-fixture";
var gridId = "xw-grid", jqGridId = "#"+gridId;
var sizeSelectorId = "gridSize", jqSizeSelectorId = "#"+sizeSelectorId;
var resetBtnId = "resetBtn", jqResetBtnId = "#"+resetBtnId;
var modeSelectorId = "editMode", jqModeSelectorId = "#"+modeSelectorId;
var modeHelpId = "modeHelp", jqModeHelpId = "#"+modeHelpId;
var answerFormId = "answer-form", jqAnswerFormId = "#"+answerFormId;
var answerRefId  = "answer-ref", jqAnswerRefId = "#"+answerRefId;
var answerId = "answer", jqAnswerId = "#"+answerId;
var answerClueId = "answer-clue", jqAnswerClueId = "#"+answerClueId;
var answerUpdateId = "answer-update", jqAnswerUpdate = "#"+answerUpdateId;

var confirmMessage = "", confirmResponse=false;
window.confirm = function(message) {
    confirmMessage = message;
    return confirmResponse;
}

QUnit.module('CrosswordEditor', {
  beforeEach: function() {
      $(jqFixtureId).append($("<div></div>").attr('id',gridId));
      $(jqFixtureId).append($("<select></select>").attr('id',sizeSelectorId));
      $(jqSizeSelectorId).append($("<option value=3>3x3</option>"))
                         .append($("<option value=5 selected>5x5</option>"));
      $(jqFixtureId).append($("<button></button>").attr('id',resetBtnId));
      $(jqFixtureId).append($("<select></select>").attr('id',modeSelectorId));
      $(jqModeSelectorId).append($("<option value=1 selected>Mode 1</option>"))
                         .append($("<option value=2>Mode 2</option>"));
      $(jqFixtureId).append($("<span></span>").attr('id',modeHelpId));
      var form = $("<div></div>").attr("id", answerFormId);
      $(jqFixtureId).append(form);
      form.append($("<span></span>").attr("id", answerRefId));
      form.append($("<input></input>").attr("id", answerId));
      form.append($("<textarea></textarea>").attr("id", answerClueId));
      form.append($("<button></button>").attr("id", answerUpdateId));
      CrosswordEditor.reset();
  },
});

QUnit.test('initialize: Throws errors if divId does not exist', function(assert) {
    assert.throws(function(){ CrosswordEditor.initialize("divId"); },
      /divId does not exist/, Error);
});

QUnit.test('initialize: Throws error if grid size selector is not set', function(assert) {
    assert.throws(function(){ CrosswordEditor.initialize(gridId); }, /Size selector not set/, Error);
});

QUnit.test('setSizeSelectorId: Throws error if selector does not exist', function(assert) {
    assert.throws(function(){ CrosswordEditor.setSizeSelectorId("some-id"); },
        /Size selector does not exist/, Error);
});

QUnit.test('initialize: Creates grid using selected size', function(assert) {
    CrosswordEditor.setSizeSelectorId(sizeSelectorId);
    assert.equal($(jqGridId).children().length, 0);
    CrosswordEditor.initialize(gridId);
    assert.equal($(jqGridId).children().length, 25)
});

QUnit.test('setResetBtnId: Throws error if button does not exist', function(assert) {
    assert.throws(function(){ CrosswordEditor.setResetBtnId("some-id"); },
        /Reset button does not exist/, Error);
});

QUnit.test('modeSelectorId: Throws error if selector does not exist', function(assert) {
    assert.throws(function(){ CrosswordEditor.setModeSelectorId("some-id"); },
        /Mode selector does not exist/, Error);
});

QUnit.test('modeHelpId: Throws error if mode help span does not exist', function(assert) {
    assert.throws(function(){ CrosswordEditor.setModeHelpId("some-id"); },
        /Mode help span does not exist/, Error);
});

QUnit.test('initialize: Sets help text based on select edit mode', function(assert) {
    initializeCrosswordEditor();
    assert.true($(jqModeHelpId).text().indexOf("Diametrically opposite square") > 0);
});

QUnit.test('initialize: Disables reset button by default', function(assert) {
    initializeCrosswordEditor();
    assert.true($(jqResetBtnId).prop('disabled'));
});

QUnit.test('setSizeSelectorId: Changehandler redraws grid to new size', function(assert) {
    initializeCrosswordEditor();
    assert.equal($(jqGridId + " > div").length, 25);
    $(jqSizeSelectorId).val(3).change();
    assert.equal($(jqGridId + " > div").length, 9);
});

QUnit.test('modeSelectorId: Changehandler updates help text for new mode', function(assert) {
    initializeCrosswordEditor();
    $(jqModeSelectorId).val(2).change();
    assert.true($(jqModeHelpId).text().indexOf("Click on a numbered square") === 0);
});

QUnit.test('Clicking on a cell sets block (in default edit mode)', function(assert) {
    initializeCrosswordEditor();
    assert.equal($(".xw-blocked").length, 0);
    $(jqGridId + " > div")[4].click();
    assert.equal($(".xw-blocked").length, 2); // Including symmetric cell
});

QUnit.test('Blocking a cell enables Reset button and disables size selector', function(assert) {
    initializeCrosswordEditor();
    assert.true($(jqResetBtnId).prop('disabled'));
    assert.false($(jqSizeSelectorId).prop('disabled'));
    $(jqGridId + " > div")[4].click();
    assert.false($(jqResetBtnId).prop('disabled'));
    assert.true($(jqSizeSelectorId).prop('disabled'));
});

QUnit.test('resetBtnId: ClickHandler asks for confirmation', function(assert) {
    initializeCrosswordEditor();
    $(jqGridId + " > div")[5].click();
    $(jqGridId + " > div")[1].click();
    confirmResponse = false;
    $(jqResetBtnId).click();
    assert.true(confirmMessage.indexOf("All changes to grid will be lost") === 0);
    assert.equal($(".xw-blocked").length, 4);
});

QUnit.test('resetBtnId: ClickHandler resets grid if confirmed', function(assert) {
    initializeCrosswordEditor();
    $(jqGridId + " > div")[5].click();
    confirmResponse = true;
    $(jqResetBtnId).click();
    assert.equal($(".xw-blocked").length, 0); // Including symmetric cell
});

QUnit.test('resetBtnId: ClickHandler deactives Reset after grid is reset', function(assert) {
    initializeCrosswordEditor();
    $(jqGridId + " > div")[5].click();
    confirmResponse = true;
    $(jqResetBtnId).click();
    assert.true($(jqResetBtnId).prop('disabled'));
    assert.false($(jqSizeSelectorId).prop('disabled'));
});

QUnit.test('Changing edit mode does not block selected cells', function(assert) {
    initializeCrosswordEditor();
    $(jqModeSelectorId).val(2).change();
    $(jqGridId + " > div")[5].click();
    assert.equal($(".xw-blocked").length, 0);
});

QUnit.test('Answers input area is not shown by default', function(assert) {
    initializeCrosswordEditor();
    assert.true($(jqAnswerFormId).prop('hidden'));
    $(jqModeSelectorId).val(2).change();
    assert.true($(jqAnswerFormId).prop('hidden'));
});

QUnit.test('Selecting first numbered cell in answers input mode hilites first row', function(assert) {
    initializeCrosswordEditor();
    var firstRowCells = parseInt($(jqSizeSelectorId).val());
    $(jqModeSelectorId).val(2).change();
    $(jqGridId + " > div")[0].click();
    assert.equal($(".hilite").length, firstRowCells);
    assert.true($(jqGridId + " > div:lt("+firstRowCells+")").hasClass("hilite"));
});

/* HELPER FUNCTIONS */
function initializeCrosswordEditor() {
    CrosswordEditor.setModeSelectorId(modeSelectorId);
    CrosswordEditor.setSizeSelectorId(sizeSelectorId);
    CrosswordEditor.setModeHelpId(modeHelpId);
    CrosswordEditor.setResetBtnId(resetBtnId);
    CrosswordEditor.initialize(gridId);
}
