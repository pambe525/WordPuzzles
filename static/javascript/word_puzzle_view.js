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
    setProgress();
    setTimer();
}

function setClueButtonStates() {
    for (let i = 1; i <= clueSet.length; i++) {
        if (clueSet[i-1].mode === 'SOLVED')
            $('#clue-btn-' + i).addClass('btn-success').removeClass('btn-light');
        else if (clueSet[i-1].mode === 'REVEALED')
            $('#clue-btn-' + i).addClass('btn-secondary').removeClass('btn-light');
    }
}

function setScore() {
    $('#id-score').text("Score: " + activeSession['solved_points'] + ' pts')
}

function setProgress() {
    let totalPoints = activeSession['total_points'];
    let solvedPoints = activeSession['solved_points'];
    let revealedPoints = activeSession['revealed_points'];
    let solvedBarWidth = Math.round(100*solvedPoints/totalPoints) + "%";
    let revealedBarWidth = Math.round(100*revealedPoints/totalPoints) + "%";
    $("#id-solved-pts").width(solvedBarWidth).text(solvedPoints+" pts");
    $("#id-revealed-pts").width(revealedBarWidth).text(revealedPoints+" pts");
}

function setTimer() {
    let timerFormat = new Date(activeSession['elapsed_secs'] * 1000).toISOString().slice(11, 19);
    $('#id-timer').text(timerFormat+'s');
}

function showClue(clickedClueNum) {
    var clue = clueSet[parseInt(clickedClueNum) - 1]
    $('#id-clue').text(getFullClueDesc(clue));
    setActiveClueBtn(clickedClueNum);
    showAnswerByClueMode(clue);
}

function showAnswerByClueMode(clue) {
    if ( clue.mode === 'PRESOLVE' ) $("#id-answer-section").hide();
    else {
        setAnswerIcons(clue);
        showAnswerWithParsing(clue);
        setAnswerBtns(clue);
    }
}

function setAnswerIcons(clue) {
    $("#id-answer-icons").children().hide();
    if (clue.mode === "SOLVED") {
        $("#id-check-icon").show();
        $("#id-answer-msg").text("[" + clue.points + " pts]").show();
    }
    else if (clue.mode === "REVEALED") {
        $("#id-eye-icon").show();
        $("#id-answer-msg").text("[0 pts]").show();
    }
}

function showAnswerWithParsing(clue) {
    let emptyGrid = (clue.mode === 'UNSOLVED');
    $('#id-answer').empty().append(getAnswerGrid(clue.answer, emptyGrid)).show();
    if (clue.parsing === '' || clue.parsing === null) $('#id-parsing').hide();
    else $('#id-parsing').empty().text("Parsing: " + clue.parsing).show();
}

function setAnswerBtns(clue) {
    if (clue.mode === 'UNSOLVED') $("#id-answer-btns").show();
    else $("#id-answer-btns").hide();
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

function getCellAsDiv(hasBorder, left_shift) {
    var cell = $("<div>").addClass('d-inline-block text-center').width('18px').height('18px');
    cell.css('font-size', '12px');
    if (hasBorder) cell.addClass('border border-dark');
    shiftCellLeft(cell, left_shift);
    return cell;
}

function getAnswerGrid(word, isEmpty) {
    if (isEmpty === undefined) isEmpty = false;
    var chain = $("<div>"), index = 0, hasBorder, cell;
    for (const letter of word) {
        hasBorder = (letter !== '-' && letter !== ' ');
        cell = getCellAsDiv(hasBorder);
        if ( !isEmpty ) cell.text(letter);
        else cell.attr('contenteditable', 'true');
        shiftCellLeft(cell, index++);
        $(chain).append(cell);
    }
    return chain;
}

function shiftCellLeft(cell, pixels) {
    cell.css('margin-left', '-' + pixels + 'px').css('margin-right', pixels + 'px')
}
