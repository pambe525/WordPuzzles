/** Calling script must define variables clueSet and showAnswers */

$(document).ready(function () {
    if (puzzleSession) loadPuzzleSessionState();
    $("#clue-btn-1").click();
})

function getClueDesc(clue) {
    return clue.clue_num + ". " + clue.clue_text + " [" + clue.points + " pts]";
}

function loadPuzzleSessionState() {
    setClueButtonStates();
    setScore();
}

function setClueButtonStates() {
    for (let i = 1; i <= clueSet.length; i++) {
        if (puzzleSession['solved_clues'].includes(i))
            $('#clue-btn-' + i).addClass('btn-success').removeClass('btn-light');
        else if (puzzleSession['revealed_clues'].includes(i))
            $('#clue-btn-' + i).addClass('btn-secondary').removeClass('btn-light');
    }
}

function setScore() {
    $('#id-score').text("Score: " + puzzleSession['score'] + ' pts')
}

function showClue(clickedClueNum) {
    var clue = clueSet[parseInt(clickedClueNum) - 1]
    $('#id-clue').text(getClueDesc(clue));
    setActiveClueBtn(clickedClueNum);
    if (showAnswers) {
        $('#id-answer').empty().append(getWordAsCellChain(clue.answer));
        $('#id-parsing').empty().text("Parsing: " + clue.parsing);
    }
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

function getCellAsDiv(letter, hasBorder) {
    var cell = $("<div>").addClass('d-inline-block text-center').text(letter).width('18px').height('18px');
    cell.css('font-size', '12px');
    if (hasBorder) cell.addClass('border border-dark');
    return cell;
}

function getWordAsCellChain(word) {
    var chain = $("<div>"), index = 0;
    for (const letter of word) {
        var hasBorder = (letter !== '-' && letter !== ' ');
        var cell = getCellAsDiv(letter, hasBorder);
        shiftCellLeft(cell, index++);
        $(chain).append(cell);
    }
    return chain;
}

function shiftCellLeft(cell, pixels) {
    cell.css('margin-left', '-' + pixels + 'px').css('margin-right', pixels + 'px')
}
