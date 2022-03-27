/** Calling script must define variables clueSet and showAnswers */

$(document).ready(function () {
    if (activeSession) loadPuzzleSessionState();
    $("#clue-btn-1").click();
})

function getFullClueDesc(clue) {
    return clue.clue_num + ". " + clue.clue_text + " [" + clue.points + " pts]";
}

function loadPuzzleSessionState() {
    setClueButtonStates();
    setScore();
}

function setClueButtonStates() {
    for (let i = 1; i <= clueSet.length; i++) {
        if (activeSession['solved_clues'].includes(i))
            $('#clue-btn-' + i).addClass('btn-success').removeClass('btn-light');
        else if (activeSession['revealed_clues'].includes(i))
            $('#clue-btn-' + i).addClass('btn-secondary').removeClass('btn-light');
    }
}

function setScore() {
    $('#id-score').text("Score: " + activeSession['score'] + ' pts')
}

function showClue(clickedClueNum) {
    var clue = clueSet[parseInt(clickedClueNum) - 1]
    $('#id-clue').text(getFullClueDesc(clue));
    setActiveClueBtn(clickedClueNum);
    if (activeSession) showAnswerByClueState(clue);
    else showAnswerWithParsing(clue)
}

function showAnswerWithParsing(clue) {
    $('#id-answer').empty().append(getWordAsGrid(clue.answer, false));
    if (clue.parsing == null) $('#id-parsing').hide();
    else $('#id-parsing').empty().text("Parsing: " + clue.parsing).show();
}

function showAnswerByClueState(clue) {
    if ( activeSession.solved_clues.includes(clue.clue_num) ) showAnswerAsSolved(clue);
    else if ( activeSession.revealed_clues.includes(clue.clue_num) ) showAnswerAsRevealed(clue);
//    else showAnswerAsUnsolved(clue);
}

function showAnswerAsSolved(clue) {
    $("#id-answer-icons").show();
    $("#id-check-icon").show();
    $("#id-eye-icon").hide();
    $("#id-wrong-icon").hide();
    $("#id-answer-msg").text("[" + clue.points + " pts]");
    $("#id-answer-btns").hide();
    showAnswerWithParsing(clue);
}

function showAnswerAsRevealed(clue) {
    $("#id-answer-icons").show();
    $("#id-check-icon").hide();
    $("#id-eye-icon").show();
    $("#id-wrong-icon").hide();
    $("#id-answer-msg").text("[0 pts]");
    $("#id-answer-btns").hide();
    showAnswerWithParsing(clue);
}

function setActiveClueBtn(clueNum) {
    $("[id^=clue-btn-]").removeClass('active');
    $("#clue-btn-" + clueNum).addClass('active').focus();
}

function nextClue() {
    var currentClueNum = parseInt($('.active').text());
    var nextClueNum = (currentClueNum < clueSet.length) ? currentClueNum + 1 : 1
    $("#clue-btn-" + nextClueNum).click()
}

function prevClue() {
    var currentClueNum = parseInt($('.active').text());
    var prevClueNum = (currentClueNum > 1) ? currentClueNum - 1 : clueSet.length
    $("#clue-btn-" + prevClueNum).click()
}

function getCellAsDiv(hasBorder) {
    var cell = $("<div>").addClass('d-inline-block text-center').width('18px').height('18px');
    cell.css('font-size', '12px');
    if (hasBorder) cell.addClass('border border-dark');
    return cell;
}

function getWordAsGrid(word, isEmpty) {
    if (isEmpty === undefined) isEmpty = false;
    var chain = $("<div>"), index = 0, hasBorder, cell;
    for (const letter of word) {
        hasBorder = (letter !== '-' && letter !== ' ');
        cell = getCellAsDiv(letter, hasBorder);
        if ( !isEmpty ) cell.text(letter);
        shiftCellLeft(cell, index++);
        $(chain).append(cell);
    }
    return chain;
}

function shiftCellLeft(cell, pixels) {
    cell.css('margin-left', '-' + pixels + 'px').css('margin-right', pixels + 'px')
}
