/** Calling script must define variables clueSet and showAnswers */

$(document).ready(function () {
    $("#clue-btn-1").click();
})

function getClueDesc(clue) {
    return clue.clue_num + ". " + clue.clue_text + " [" + clue.points + " pts]";
}

function showClue(clickedClueNum) {
    var clue = clueSet[parseInt(clickedClueNum) - 1]
    $('#id-clue').text(getClueDesc(clue));
    $('#id-answer').empty().append(getWordAsCellChain(clue.answer).prepend("Answer:&nbsp;"));
    $('#id-parsing').empty().text("Parsing: " + clue.parsing);
    $("[id^=clue-btn-]").removeClass('active');
    $("#clue-btn-" + clickedClueNum).addClass('active').focus();
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
    var cell = $("<div>").addClass('d-inline text-center').text(letter).width('18px').height('18px');
    cell.css('font-size', '12px');
    if (hasBorder) cell.addClass('border border-dark');
    return cell;
}

function getWordAsCellChain(word) {
    var chain = $("<div>").addClass('m-0 row'), index = 0;
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