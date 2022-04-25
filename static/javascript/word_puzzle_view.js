/** Calling script must define variables clueSet and showAnswers */

$(document).ready(function () {
    if (activeSession) loadPuzzleSessionState();
    $("#clue-btn-1").click();
})

window.onfocus = function() {
    sessionTimer.resume();
}

window.onblur = function() {
    sessionTimer.pause();
}

window.onbeforeunload = function() {
    stopAndSaveTimer();
}

function getFullClueDesc(clue) {
    return clue.clue_num + ". " + clue.clue_text + " [" + clue.points + " pts]";
}

function loadPuzzleSessionState() {
    sessionTimer = new SessionTimer("id-timer", activeSession['elapsed_secs']);
    sessionTimer.start();
    setClueButtonStates();
    setScore();
    setProgress();
    setCompletionStatus();
    if ( isSessionComplete() ) sessionTimer.stop();
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

function setCompletionStatus() {
    let completedSection = $("#id-completed");
    if (isSessionComplete()) {
        completedSection.show();
        $("#id-finish-later-btn").hide();
    } else completedSection.hide();
}

function showClueAndAnswer(clickedClueNum) {
    activeClueNum = clickedClueNum;
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
    if ( clue.mode === 'UNSOLVED') $("#id-answer div div:first-child").click();
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
    cell.css('font-size', '14px').css('font-weight', 'bold').css('caret-color','transparent').on('click', hiliteCell);
    if (hasBorder) cell.addClass('border border-dark');
    shiftCellLeft(cell, left_shift);
    return cell;
}

function getAnswerGrid(word, isEmpty) {
    if (isEmpty === undefined) isEmpty = false;
    let grid = $("<div>"), index = 0, hasBorder, cell;
    for (const letter of word) {
        if (letter === '-' || letter === ' ') {
            cell = getCellAsDiv(false).text(letter);
        } else {
            cell = getCellAsDiv(true);
            if (!isEmpty) cell.text(letter);
            else cell.attr('contenteditable', 'true').on('keydown', onKeyDown);
        }
        shiftCellLeft(cell, index++);
        $(grid).append(cell);
    }
    return grid;
}

function shiftCellLeft(cell, pixels) {
    cell.css('margin-left', '-' + pixels + 'px').css('margin-right', pixels + 'px')
}

onKeyDown = (event) => {
    let key = event.keyCode || event.which;
    let keyChar = String.fromCharCode(key);
    event.preventDefault();
    if (/[a-zA-Z]/.test(keyChar)) {
        $(event.target).text(keyChar);
        let nextCell = getNextCell( $(event.target) );
        if (nextCell) setFocusAndHilite(nextCell);
    } else if (key === 8) {
        $(event.target).text('');
        let prevCell = getPrevCell( $(event.target) );
        if (prevCell) setFocusAndHilite(prevCell);
    } else if (key === 13) {
        $("#id-submit-btn").click();
    }
}

hiliteCell = (event) => {
    $("div[contenteditable=true]").css('background', '');
    $(event.target).css('background', 'yellow').focus();
}

function getNextCell(currentCell) {
    let nextCell = currentCell.nextAll("div[contenteditable=true]:first");
    return (nextCell.length > 0) ? nextCell : null;
}

function getPrevCell(currentCell) {
    let prevCell = currentCell.prevAll("div[contenteditable=true]:first");
    return (prevCell.length > 0) ? prevCell : null;
}

function setFocusAndHilite(cell) {
    $("div[contenteditable=true]").css('background', '');
    cell.css('background', 'yellow').focus();
}

clearAllCells = () => {
    $("div[contenteditable=true]").empty();
    $("#id-answer div div:first-child").click()
}

function submitClicked() {
    let answer_input = $("#id-answer").text();
    if (answer_input.length !== clueSet[activeClueNum-1].answer.length) return;
    let context = {'session_id': activeSession.session_id, 'clue_num': activeClueNum, 'answer_input': answer_input};
    let request = $.ajax({
        method: "POST",
        dataType: "json",
        data: {'action': 'solve', 'data': JSON.stringify(context)},
    });
    request.done(updateAnswerState);
    request.fail(answerIncorrect);
}

function stopAndSaveTimer() {
    let elapsedSecs = sessionTimer.stop();
    let context = {'session_id': activeSession.session_id, 'elapsed_secs': elapsedSecs};
    postAjax("timer", context);
}

function postAjax(action, data) {
    $.ajax({
        method: "POST",
        dataType: "json",
        data: {'action': action, 'data': JSON.stringify(data)},
    });
}

function updateAnswerState(json_data) {
    activeSession = json_data['active_session'];
    clueSet = JSON.parse(json_data['clues']);
    setClueButtonStates();
    showClueAndAnswer(activeClueNum);
    setScore();
    setProgress();
    setCompletionStatus();
    if ( isSessionComplete() ) stopAndSaveTimer();
}

function answerIncorrect() {
    $("#id-wrong-icon").show();
    $("#id-answer-msg").text("Incorrect").show();
}

function revealClicked() {
    let context = {'session_id': activeSession.session_id, 'clue_num': activeClueNum};
    let request = $.ajax({
        method: "POST",
        dataType: "json",
        data: {'action': 'reveal', 'data': JSON.stringify(context)},
    });
    request.done(updateAnswerState);
}

function clearClicked() {
    clearAllCells();
    $("#id-wrong-icon").hide();
    $("#id-answer-msg").empty().hide();
}

function isSessionComplete() {
    return (activeSession['total_points'] === activeSession['solved_points'] + activeSession['revealed_points'])
}


class SessionTimer {

    constructor(displayId, startingSecs) {
        this.elapsedSecs = startingSecs;
        this.timerDisplayId = "#"+displayId;
        this.intervalTimerId = null;
        this.timerOn = false;
    }

    start() {
        this._showTime();
        if ( this.intervalTimerId == null ) this.intervalTimerId = setInterval(this._incrementTimer, 1000);
        this.timerOn = true;
    }

    resume() {
        if ( this.intervalTimerId == null && this.timerOn )
            this.intervalTimerId = setInterval(this._incrementTimer, 1000);
    }

    pause() {
        if ( this.intervalTimerId != null ) clearInterval(this.intervalTimerId);
        this.intervalTimerId = null;
    }

    stop() {
        this.pause();
        this.timerOn = false;
        this._showTime();
        return this.elapsedSecs;
    }

    _showTime() {
        let timerFormat = new Date(this.elapsedSecs*1000).toISOString().slice(11, 19);
        $(this.timerDisplayId).text(timerFormat+'s');
    }

    _incrementTimer = () => {
        this.elapsedSecs++;
        this._showTime();
    }
}