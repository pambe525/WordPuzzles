class WordPuzzlePageView {
    constructor(clueSet, activeSession) {
        this.clueSet = clueSet;
        this.session = activeSession;
        this.btnGroup = new ClueButtonsGroup("id-clue-btns-group", clueSet, this._clueBtnClicked).show();
        this.clueBox = new ClueBox(clueSet, this._submitClicked, this._revealClicked);
        this.btnGroup.click(1);
        if (activeSession) this.sessionProgress = new SessionProgress(activeSession, this._saveTimer);
    }

    _clueBtnClicked = (clueNum) => {
        this.clueBox.showClue(clueNum);
    }

    _submitClicked = (clueNum, answerInput) => {
        let context = {'session_id': this.session.session_id, 'clue_num': clueNum, 'answer_input': answerInput};
        let request = this._postAjax('solve', context);
        request.done(this._updateAnswerState);
        request.fail(this._answerIncorrect);
    }

    _revealClicked = (clueNum) => {
        let context = {'session_id': this.session.session_id, 'clue_num': clueNum};
        let request = this._postAjax('reveal', context);
        request.done(this._updateAnswerState);
    }

    _saveTimer = (elapsedSecs) => {
        let context = {'session_id': this.session.session_id, 'elapsed_secs': elapsedSecs};
        this._postAjax("timer", context);
    }

    _postAjax(action, data) {
        return $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action': action, 'data': JSON.stringify(data)},
        });
    }

    _updateAnswerState = (json_data) => {
        this.session = json_data['active_session'];
        this.clueSet = JSON.parse(json_data['clues']);
        this.btnGroup.update(this.clueSet);
        this.clueBox.updateClueSet(this.clueSet);
        this.sessionProgress.update(this.session);
        this._saveTimer(this.sessionProgress.getElapsedSecs());
    }

    _answerIncorrect = () => {
        this.clueBox.showAnswerIsWrong();
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * SessionProgress
 */
class SessionProgress {
    constructor(activeSession, saveTimerHandler) {
        this.session = activeSession;
        this.saveTimerHandler = saveTimerHandler;
        this.ID = {
            timer: "#id-timer", score: "#id-score", completedSection: "#id-completed",
            progress: "#id-progress", solvedPts: "#id-solved-pts", revealedPts: "#id-revealed-pts",
            finishLaterBtn: "#id-finish-later-btn"
        };
        this.isCompleteOnLoad = this._isSessionComplete();
        this.timer = new SessionTimer(this.ID.timer, activeSession['elapsed_secs']);
        this.timer.start();
        this._setWindowEventHandlers();
        this.update(activeSession);
    }

    update(activeSession) {
        this.session = activeSession;
        this._setScore();
        this._setProgressBar();
        this._setCompletionStatus();
    }

    getElapsedSecs() {
        return this.timer.elapsedSecs;
    }

    _setScore() {
        this.score = $(this.ID.score).text("Score: " + this.session['solved_points'] + ' pts');
    }

    _setProgressBar() {
        let totalPoints = this.session['total_points'];
        let solvedPoints = this.session['solved_points'];
        let revealedPoints = this.session['revealed_points'];
        let solvedBarWidth = Math.round(100 * solvedPoints / totalPoints) + "%";
        let revealedBarWidth = Math.round(100 * revealedPoints / totalPoints) + "%";
        $(this.ID.solvedPts).width(solvedBarWidth).text(solvedPoints + " pts");
        $(this.ID.revealedPts).width(revealedBarWidth).text(revealedPoints + " pts");
    }

    _setCompletionStatus() {
        if (this._isSessionComplete()) {
            $(this.ID.completedSection).show();
            $(this.ID.finishLaterBtn).hide();
            let elapsedSecs = this.timer.stop();
            if (!this.isCompleteOnLoad) this.saveTimerHandler(elapsedSecs);
        } else $(this.ID.completedSection).hide();
    }

    _isSessionComplete() {
        return (this.session['total_points'] === this.session['solved_points'] + this.session['revealed_points']);
    }

    _setWindowEventHandlers() {
        window.onfocus = () => {
            this.timer.resume();
        }
        window.onblur = () => {
            this.timer.pause();
        }
        window.onbeforeunload = () => {
            this.saveTimerHandler(this.timer.stop());
        }
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * ClueBox
 */
class ClueBox {
    constructor(clueSet, submitAnswerHandler, revealAnswerHandler) {
        this.clueSet = clueSet;
        this.activeSession = activeSession;
        this.answerGrid = null;
        this.submitClickHandler = submitAnswerHandler;
        this.revealClickHandler = revealAnswerHandler;
        this.ID = {
            clueText: "#id-clue", answerSection: "#id-answer-section", answerIcons: "#id-answer-icons",
            checkIcon: "#id-check-icon", eyeIcon: "#id-eye-icon", wrongIcon: "#id-wrong-icon",
            answerMsg: "#id-answer-msg", answerText: "#id-answer", parsing: "#id-parsing", submitBtn: "#id-submit-btn",
            clearBtn: "#id-clear-btn", revealBtn: "#id-reveal-btn", answerBtns: "#id-answer-btns"
        };
        if ($(this.ID.submitBtn)) $(this.ID.submitBtn).on('click', this._submitBtnClicked);
        if ($(this.ID.clearBtn)) $(this.ID.clearBtn).on('click', this._clearBtnClicked);
        if ($(this.ID.revealBtn)) $(this.ID.revealBtn).on('click', this._revealBtnClicked);
        this.activeClueNum = 0;
    }

    showClue(clueNum) {
        let clue = this.clueSet[clueNum - 1];
        $(this.ID.clueText).text(this._getFullClueDesc(clue));
        this._showAnswerByClueMode(clue);
        this.activeClueNum = clueNum;
    }

    updateClueSet(clueSet) {
        this.clueSet = clueSet;
        this.showClue(this.activeClueNum);
    }

    showAnswerIsWrong() {
        $(this.ID.wrongIcon).show();
        $(this.ID.answerMsg).text("Incorrect").show();
    }

    _showAnswerByClueMode(clue) {
        if (clue.mode === 'PRESOLVE') $(this.ID.answerSection).hide();
        else {
            this._setAnswerIcons(clue);
            this._showAnswerWithParsing(clue);
            this._setAnswerBtns(clue);
        }
    }

    _setAnswerIcons(clue) {
        $(this.ID.answerIcons).children().hide();
        if (clue.mode === "SOLVED") {
            $(this.ID.checkIcon).show();
            $(this.ID.answerMsg).text("[" + clue.points + " pts]").show();
        } else if (clue.mode === "REVEALED") {
            $(this.ID.eyeIcon).show();
            $(this.ID.answerMsg).text("[0 pts]").show();
        }
    }

    _showAnswerWithParsing(clue) {
        let isEditable = (clue.mode === 'UNSOLVED');
        this.answerGrid = new AnswerGrid(clue.answer, isEditable).show(this.ID.answerText);
        if (clue.parsing === '' || clue.parsing === null) $(this.ID.parsing).hide();
        else $(this.ID.parsing).empty().text("Parsing: " + clue.parsing).show();
    }

    _setAnswerBtns(clue) {
        if (clue.mode === 'UNSOLVED') $(this.ID.answerBtns).show();
        else $(this.ID.answerBtns).hide();
    }

    _getFullClueDesc(clue) {
        return clue['clue_num'] + ". " + clue['clue_text'] + " [" + clue['points'] + " pts]";
    }

    _submitBtnClicked = () => {
        let answerInput = this.answerGrid.readInput();
        if (answerInput.length === this.clueSet[this.activeClueNum - 1].answer.length)
            this.submitClickHandler(this.activeClueNum, answerInput);
    }

    _revealBtnClicked = () => {
        this.revealClickHandler(this.activeClueNum);
    }

    _clearBtnClicked = () => {
        this.answerGrid.clear();
        $(this.ID.wrongIcon).hide();
        $(this.ID.answerMsg).empty().hide();
    }
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
        $("#id-right-caret").on('click', this.clickNext);
        $("#id-left-caret").on('click', this.clickPrev)
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

    clickNext = () => {
        let nextClueNum = (this.activeClueNum < this.clueSet.length) ? this.activeClueNum + 1 : 1;
        this.click(nextClueNum);
    }

    clickPrev = () => {
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
            btn.addClass("btn-sm btn-light border border-dark p-0 mr-1");
            btn.attr('id', "clue-btn-" + clue.clue_num).attr('title', clueText).text(clue.clue_num);
            btn.css('width','25px');
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
    constructor(answerText, isEditable) {
        this.answer = answerText;
        this.isEditable = isEditable;
        this.grid = this._createGrid();
    }

    show(jqContainerId) {
        $(jqContainerId).empty().append(this.grid).show();
        this._setEditFocusOnFirstCell();
        return this;
    }

    clear() {
        $("div[contenteditable=true]").empty();
        this._setEditFocusOnFirstCell();
    }

    readInput() {
        return this.grid.text();
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
        cell.css('font-size', '13px').css('caret-color', 'transparent');
        if (hasBorder) cell.addClass('border border-secondary');
        return cell;
    }

    _setEditable(cell) {
        cell.attr('contenteditable', 'true').on('keydown', this._onKeyDown);
        cell.on('blur', this._removeHilite).on('focus', this._setHilite);
    }

    _setEditFocusOnFirstCell() {
        if (this.isEditable) this.grid.children(":first-child").focus();
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
    constructor(jqContainerId, startingSecs) {
        this.elapsedSecs = startingSecs;
        this.timerDisplayId = jqContainerId;
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