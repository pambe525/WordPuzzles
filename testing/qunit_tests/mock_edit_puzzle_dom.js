/**
 * Mock DOM for edit_puzzle.html
 */

const jqFixtureId = "#qunit-fixture";
const pageTitleId = "page-title", jqPageTitleId = "#" + pageTitleId;
const saveOkId = "save-ok", jqSaveOkId = "#" + saveOkId;
const descId = "desc", jqDescId = "#" + descId;
const shareBtnId = "share", jqShareBtnId = "#" + shareBtnId;
const saveBtnId = "save", jqSaveBtnId = "#" + saveBtnId;
const deleteBtnId = "delete", jqDeleteBtnId = "#" + deleteBtnId;
const homeBtnId = "home", jqHomeBtnId = "#" + homeBtnId;
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

function setupDOM() {
    $(jqFixtureId).append($("<button></button>").attr('id', homeBtnId));
    $(jqFixtureId).append($("<div></div>").attr('id', puzzleDivId));
    $(jqFixtureId).append($("<h3></h3>").attr('id', pageTitleId));
    $(jqFixtureId).append($("<span></span>").attr('id', saveOkId));
    $(jqFixtureId).append($("<button></button>").attr('id', saveBtnId));
    $(jqFixtureId).append($("<button></button>").attr('id', deleteBtnId));
    $(jqFixtureId).append($("<button></button>").attr('id', shareBtnId));
    $(jqFixtureId).append($("<input type='text'>").attr('id', descId));
    $(jqFixtureId).append($("<label></label>").attr('id', sizeLabelId));
    $(jqFixtureId).append($("<select></select>").attr('id', sizeSelectorId));
    $(jqFixtureId).append($("<input type='checkbox'>").attr('id', modeToggleId));
    $(jqFixtureId).append($("<div></div>").attr('id', symmOptionId));
    $(jqFixtureId).append($("<input type='checkbox'>").attr('id', symmToggleId));
    var form2 = $("<div></div>").attr("id", clueFormId);
    $(jqFixtureId).append(form2);
    form2.append($("<span></span>").attr("id", clueNumId));
    form2.append($("<input type='text'>").attr("id", clueWordId));
    form2.append($("<textarea></textarea>").attr("id", clueTextId));
    form2.append($("<span></span>").attr("id", clueMsgId));
    form2.append($("<button></button>").attr("id", clueUpdateId));
    form2.append($("<button></button>").attr("id", clueDeleteId));
}

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
