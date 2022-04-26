/** Calling script must define variables clueSet and showAnswers */

var activeClueNum = 0, sessionTimer = null, answerGrid = null, btnGroup = null;

$(document).ready(function () {
    btnGroup = new ClueButtonsGroup("id-clue-btns-group", clueSet, showClueAndAnswer).show();
    btnGroup.click(1);
    if (activeSession) loadPuzzleSessionState();
})

window.onfocus = function () {
    if (sessionTimer) sessionTimer.resume();
}
window.onblur = function () {
    if (sessionTimer) sessionTimer.pause();
}
window.onbeforeunload = function () {
    stopAndSaveTimer();
}

function getFullClueDesc(clue) {
    return clue.clue_num + ". " + clue.clue_text + " [" + clue.points + " pts]";
}

function loadPuzzleSessionState() {
    sessionTimer = new SessionTimer("id-timer", activeSession['elapsed_secs']);
    sessionTimer.start();
    setScore();
    setProgress();
    setCompletionStatus();
    if (isSessionComplete()) sessionTimer.stop();
}

function setScore() {
    $('#id-score').text("Score: " + activeSession['solved_points'] + ' pts')
}

function setProgress() {
    let totalPoints = activeSession['total_points'];
    let solvedPoints = activeSession['solved_points'];
    let revealedPoints = activeSession['revealed_points'];
    let solvedBarWidth = Math.round(100 * solvedPoints / totalPoints) + "%";
    let revealedBarWidth = Math.round(100 * revealedPoints / totalPoints) + "%";
    $("#id-solved-pts").width(solvedBarWidth).text(solvedPoints + " pts");
    $("#id-revealed-pts").width(revealedBarWidth).text(revealedPoints + " pts");
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
    let clue = clueSet[clickedClueNum - 1];
    $('#id-clue').text(getFullClueDesc(clue));
    showAnswerByClueMode(clue);
}

function showAnswerByClueMode(clue) {
    if (clue.mode === 'PRESOLVE') $("#id-answer-section").hide();
    else {
        setAnswerIcons(clue);
        showAnswerWithParsing(clue);
        setAnswerBtns(clue);
    }
    if (clue.mode === 'UNSOLVED') $("#id-answer div div:first-child").click();
}

function setAnswerIcons(clue) {
    $("#id-answer-icons").children().hide();
    if (clue.mode === "SOLVED") {
        $("#id-check-icon").show();
        $("#id-answer-msg").text("[" + clue.points + " pts]").show();
    } else if (clue.mode === "REVEALED") {
        $("#id-eye-icon").show();
        $("#id-answer-msg").text("[0 pts]").show();
    }
}

function showAnswerWithParsing(clue) {
    let isEditable = (clue.mode === 'UNSOLVED');
    answerGrid = new AnswerGrid("id-answer", clue.answer, isEditable);
    answerGrid.show();
    if (clue.parsing === '' || clue.parsing === null) $('#id-parsing').hide();
    else $('#id-parsing').empty().text("Parsing: " + clue.parsing).show();
}

function setAnswerBtns(clue) {
    if (clue.mode === 'UNSOLVED') $("#id-answer-btns").show();
    else $("#id-answer-btns").hide();
}

function nextClue() {
    btnGroup.clickNext();
}

function prevClue() {
    btnGroup.clickPrev();
}

function submitClicked() {
    let answer_input = $("#id-answer").text();
    if (answer_input.length !== clueSet[activeClueNum - 1].answer.length) return;
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
    if (sessionTimer) {
        let elapsedSecs = sessionTimer.stop();
        let context = {'session_id': activeSession.session_id, 'elapsed_secs': elapsedSecs};
        postAjax("timer", context);
    }
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
    btnGroup.update(clueSet);
    showClueAndAnswer(activeClueNum);
    setScore();
    setProgress();
    setCompletionStatus();
    if (isSessionComplete()) stopAndSaveTimer();
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
    answerGrid.clear();
    $("#id-wrong-icon").hide();
    $("#id-answer-msg").empty().hide();
}

function isSessionComplete() {
    return (activeSession['total_points'] === activeSession['solved_points'] + activeSession['revealed_points'])
}

/**--------------------------------------------------------------------------------------------------------------------
 * ClueRotator
 */
class ClueRotator {
    constructor(containerId, clueSet, activeSession) {
        this.containerId = containerId;
        this._build();
    }

    _build() {

    }

    _getLeftArrowButton() {
        $("<button>").addClass("pr-2 p-0 btn").title("Previous Clue").attr("id", "id-left-caret")
    }

                    //
                    //     <!-- LEFT ARROW -->
                    // <button class="pr-2 p-0 btn" title="Previous clue" id="id-left-caret" onclick="prevClue();">
                    //     <i class="fa fa-caret-left fa-3x"></i>
                    // </button>
                    // <!-- CLUE & ANSWER BOX -->
                    // <div class="col p-2 border border-dark rounded-3" style="line-height:18px">
                    //     <div class="font-weight-bold mb-2" id="id-clue"></div>
                    //     <div id="id-answer-section">
                    //         <div class="m-0 row align-items-center">
                    //             Answer:
                    //             {% if active_session != None %}
                    //                 <div class="m-0 row ml-1" id="id-answer-icons">
                    //                     <div id="id-check-icon"><i class="fa fa-check text-success"></i></div>
                    //                     <div id="id-eye-icon"><i class="fa fa-eye text-secondary"></i></div>
                    //                     <div id="id-wrong-icon"><i class="fa fa-times text-danger"></i></div>
                    //                     <div class="ml-1" id="id-answer-msg">[2 pts]</div>
                    //                 </div>
                    //             {% endif %}
                    //         </div>
                    //         <div id="id-answer"></div>
                    //         {% if active_session != None %}
                    //             <div class="m-0 row mt-2" id="id-answer-btns">
                    //                 <button class="btn-sm btn-dark pt-0 pb-0" id="id-submit-btn"
                    //                         onclick='submitClicked();'>SUBMIT</button>
                    //                 <button class="btn-sm btn-dark pt-0 pb-0 ml-1" id="id-clear-btn"
                    //                         onclick='clearClicked();'>CLEAR</button>
                    //                 <button class="btn-sm btn-danger pt-0 pb-0 ml-auto" id="id-reveal-btn"
                    //                         onclick='revealClicked();'>REVEAL</button>
                    //             </div>
                    //         {% endif %}
                    //         <div class="mt-1" id="id-parsing"></div>
                    //     </div>
                    //
}

/**--------------------------------------------------------------------------------------------------------------------
 * ClueButtonsGroup
 */
class ClueButtonsGroup {
    constructor(containerId, clues, clickHandler) {
        this.onclickHandler = clickHandler;
        this.clueSet = clues;
        this.containerId = "#" + containerId;
        this.btnList = this._createButtons();
        this.activeClueNum = 0;
    }

    show() {
        let group = $("<div>");
        for (const btn of this.btnList) group.append(btn);
        $(this.containerId).empty().append(group);
        return this;
    }

    click(clueNum) {
        this.btnList[clueNum - 1].click();
    }

    clickNext() {
        let nextClueNum = (this.activeClueNum < this.clueSet.length) ? this.activeClueNum + 1 : 1;
        this.click(nextClueNum);
    }

    clickPrev() {
        let prevClueNum = (this.activeClueNum > 1) ? this.activeClueNum - 1 : this.clueSet.length;
        this.click(prevClueNum);
    }

    update(clueSet) {
        this.clueSet = clueSet
        for (const clue of clueSet) {
            let btn = this.btnList[clue.clue_num - 1];
            this._setButtonState(btn, clue.mode);
        }
    }

    _setButtonState(btn, state) {
        if (state === 'SOLVED') btn.addClass('btn-success').removeClass('btn-light');
        else if (state === 'REVEALED') btn.addClass('btn-secondary').removeClass('btn-light');
    }

    _setActive = (event) => {
        $(event.target).addClass('active');
        this.activeClueNum = parseInt($(event.target).text());
    }

    _removeActive = (event) => {
        $(event.target).removeClass('active');
    }

    _buttonClicked = (event) => {
        $(event.target).focus();
        let clueNum = parseInt($(event.target).text());
        this.onclickHandler(clueNum);
    }

    _createButtons() {
        let list = [], btn, clueText;
        for (const clue of this.clueSet) {
            clueText = clue.clue_text + " [" + clue.points + " pts]";
            btn = $("<button>");
            btn.addClass("btn-sm btn-light border border-dark pt-0 pb-0 mr-1");
            btn.attr('id', "clue-btn-" + clue.clue_num).attr('title', clueText).text(clue.clue_num);
            btn.on('click', this._buttonClicked).on('focus', this._setActive).on('blur', this._removeActive);
            this._setButtonState(btn, clue.mode);
            list.push(btn);
        }
        return list;
    }
}


/**--------------------------------------------------------------------------------------------------------------------
 * AnswerGrid
 */
class AnswerGrid {
    constructor(containerId, answerText, isEditable) {
        this.gridDisplayId = "#" + containerId;
        this.answer = answerText;
        this.isEditable = isEditable;
        this.grid = this._createGrid();
    }

    show() {
        $(this.gridDisplayId).empty().append(this.grid).show();
        this._setEditFocusOnFirstCell();
    }

    clear() {
        $("div[contenteditable=true]").empty();
        this._setEditFocusOnFirstCell();
    }

    _createGrid() {
        let grid = $("<div>"), index = 0, cell, hasBorder;
        for (const letter of this.answer) {
            hasBorder = (!(letter === '-' || letter === ' '));
            cell = this._getCellAsDiv(hasBorder);
            if (!this.isEditable || !hasBorder) cell.text(letter);
            else this._setEditable(cell);
            this._shiftCellToLeft(cell, index++);
            $(grid).append(cell);
        }
        return grid;
    }

    _getCellAsDiv(hasBorder) {
        let cell = $("<div>").addClass('d-inline-block text-center').width('18px').height('18px');
        cell.css('font-size', '13px').css('font-weight', 'bold').css('caret-color', 'transparent');
        if (hasBorder) cell.addClass('border border-secondary');
        return cell;
    }

    _setEditable(cell) {
        cell.attr('contenteditable', 'true').on('keydown', this._onKeyDown);
        cell.on('blur', this._removeHilite).on('focus', this._setHilite);
    }

    _setEditFocusOnFirstCell() {
        if (this.isEditable) $(this.gridDisplayId + " div div:first-child").focus();
    }

    _getNextCell(currentCell) {
        let nextCell = currentCell.nextAll("div[contenteditable=true]:first");
        return (nextCell.length > 0) ? nextCell : null;
    }

    _getPrevCell(currentCell) {
        let prevCell = currentCell.prevAll("div[contenteditable=true]:first");
        return (prevCell.length > 0) ? prevCell : null;
    }

    _shiftCellToLeft(cell, pixels) {
        cell.css('margin-left', '-' + pixels + 'px').css('margin-right', pixels + 'px')
    }

    _onKeyDown = (event) => {
        let key = event.keyCode || event.which;
        let keyChar = String.fromCharCode(key);
        event.preventDefault();
        if (/[a-zA-Z]/.test(keyChar)) this._setTextAndMoveToNextCell($(event.target), keyChar);
        else if (key === 8) this._setTextAndMoveToPrevCell($(event.target), '');
        else if (key === 13) $("#id-submit-btn").click();
    }

    _removeHilite = (event) => {
        $(event.target).css('background', '');
    }

    _setHilite = (event) => {
        $(event.target).css('background', 'yellow');
    }

    _setTextAndMoveToNextCell(cell, keyChar) {
        cell.text(keyChar);
        let nextCell = this._getNextCell(cell);
        if (nextCell) nextCell.focus();
    }

    _setTextAndMoveToPrevCell(cell, keyChar) {
        cell.text(keyChar);
        let prevCell = this._getPrevCell(cell);
        if (prevCell) prevCell.focus();
    }
}


/**--------------------------------------------------------------------------------------------------------------------
 * SessionTimer
 */
class SessionTimer {
    constructor(containerId, startingSecs) {
        this.elapsedSecs = startingSecs;
        this.timerDisplayId = "#" + containerId;
        this.intervalTimerId = null;
        this.timerOn = false;
    }

    start() {
        this._showTime();
        if (this.intervalTimerId == null) this.intervalTimerId = setInterval(this._incrementTimer, 1000);
        this.timerOn = true;
    }

    resume() {
        if (this.intervalTimerId == null && this.timerOn)
            this.intervalTimerId = setInterval(this._incrementTimer, 1000);
    }

    pause() {
        if (this.intervalTimerId != null) clearInterval(this.intervalTimerId);
        this.intervalTimerId = null;
    }

    stop() {
        this.pause();
        this.timerOn = false;
        this._showTime();
        return this.elapsedSecs;
    }

    _showTime() {
        let timerFormat = new Date(this.elapsedSecs * 1000).toISOString().slice(11, 19);
        $(this.timerDisplayId).text(timerFormat + 's');
    }

    _incrementTimer = () => {
        this.elapsedSecs++;
        this._showTime();
    }
}