class WordPuzzlePageView {
    constructor(clueSet, activeSession) {
        this.clueSet = clueSet;
        this.session = activeSession;
        this.cluesList = new CluesList(clueSet, "id-clues-list", this._clueClicked).show();
        this.answerDialog = new AnswerDialog("id-modal-answer-box", this._submitClicked, this._revealClicked);
        if (activeSession) this.sessionProgress = new SessionProgress(activeSession, this._saveTimer);
    }

    _clueClicked = (clueNum) => {
        this.answerDialog.show(this.clueSet[clueNum-1]);
    }

    _submitClicked = (clueNum, answerInput) => {
        let context = {'session_id': this.session.session_id, 'clue_num': clueNum, 'answer_input': answerInput};
        let request = this._postAjax('solve', context, this._updateClueState);
        request.fail(this._answerIncorrect);
    }

    _revealClicked = (clueNum) => {
        let context = {'session_id': this.session.session_id, 'clue_num': clueNum};
        this._postAjax('reveal', context, this._updateClueState);
    }

    _saveTimer = (elapsedSecs) => {
        let context = {'session_id': this.session.session_id, 'elapsed_secs': elapsedSecs};
        this._postAjax("timer", context);
    }

    _postAjax(action, data, successHandler) {
        return $.ajax({
            method: "POST",
            dataType: "json",
            data: {'action': action, 'data': JSON.stringify(data)},
            success: successHandler
        });
    }

    _updateClueState = (json_data) => {
        this.answerDialog.close();
        this.session = json_data['active_session'];
        this.clueSet = JSON.parse(json_data['clues']);
        this.cluesList.update(this.clueSet);
        this.cluesList.click(this.answerDialog.activeClue);
        this.sessionProgress.update(this.session);
        this._saveTimer(this.sessionProgress.getElapsedSecs());
    }

    _answerIncorrect = () => {
        this.answerDialog.showErrorMsg("Incorrect answer");
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
            progress: "#id-progress", numSolved: "#id-num-solved", numRevealed: "#id-num-revealed",
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
        this.score = $(this.ID.score).text("Score: " + this.session['score'] + ' pts');
    }

    _setProgressBar() {
        let num_clues = this.session['num_clues'];
        let num_solved = this.session['num_solved'];
        let num_revealed = this.session['num_revealed'];
        let solvedBarWidth = Math.round(100 * num_solved / num_clues) + "%";
        let revealedBarWidth = Math.round(100 * num_revealed / num_clues) + "%";
        $(this.ID.numSolved).width(solvedBarWidth).text(num_solved);
        $(this.ID.numRevealed).width(revealedBarWidth).text(num_revealed);
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
        return (this.session['num_clues'] === this.session['num_solved'] + this.session['num_revealed']);
    }

    _setWindowEventHandlers() {
        window.onfocus = () => {
            this.timer.resume();
        }
        window.onblur = () => {
            this.saveTimerHandler(this.timer.pause());
        }
        window.onbeforeunload = () => {
            this.saveTimerHandler(this.timer.stop());
        }
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * Answer grid
 */
class AnswerGrid {
       constructor(answerText, isEditable) {
        this.answer = answerText;
        this.isEditable = isEditable;
        this._grid = this._createGrid();
    }

    get grid() {
        return this._grid;
    }

    clear() {
        this._grid.val('').focus();
    }

    readInput() {
        return this._grid.val();
    }

    _createGrid() {
        let grid = $("<input/>").attr('type','text');
        grid.css('border','1px solid #ccc').css('background','linear-gradient(to right, #ccc 1px, transparent 0');
        grid.css('background-size', '14px 1px').css('text-transform','uppercase').css('text-align', 'left');
        grid.prop('maxlength', this.answer.length).css('padding-left', '0px');
        grid.css('letter-spacing','6.2px').css('font', '14px consolas, monospace');
        grid.css('width', 14*this.answer.length + 6 + 'px').css('text-indent','4px');
        if (!this.isEditable) grid.prop('readonly', true).val(this.answer);
        return grid;
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * Clues List
 */
class CluesList {
    constructor(clues, tableId, clickHandler) {
        this.clues = clues;
        this.tableID = "#"+tableId;
        this.clickhandler = clickHandler;
        this.activeRow = 0;
        this._setClickHandler();
    }

    show() {
        for (const clue of this.clues) {
            this._setClueRowDetails(clue);
        }
        return this;
    }

    update(clues) {
        this.clues = clues;
        let activeClue = this.clues[this.activeRow-1]
        this._setClueRowDetails(activeClue);
    }

    click(clue) {
        this._clueCell(clue, 3).click();
    }

    _clueCell(clue, colNum) {
        let cells = $(this.tableID + ">tbody>tr").eq(clue.clue_num-1).children();
        return cells.eq(colNum-1);
    }

    _setClickHandler() {
        for (const clue of this.clues)
            if (clue.mode !== 'PREVIEW' && clue.mode !== 'PRESOLVE') {
                this._clueCell(clue, 3).on('click', this._clueClicked);
            }
    }

    _setClueRowDetails(clue) {
        this._clueCell(clue,1).empty().html(this._icon(clue))
        this._clueCell(clue,2).empty().text(clue.clue_num + ".");
        this._clueCell(clue,3).empty().html(this._clueDesc(clue));
        this._clueCell(clue,4).empty().html(this._points(clue));
        if (clue.mode === "PREVIEW") this._showAnswerAndParsing(clue);
    }

    _icon(clue) {
        let icon = $("<i>");
        if (clue.mode === 'SOLVED') icon.addClass("fa fa-check-circle text-success");
        else if (clue.mode === 'REVEALED') icon.addClass("fa fa-eye");
        return (clue.mode !== 'SOLVED' && clue.mode !== 'REVEALED') ? null : icon;
    }

    _clueDesc(clue) {
        let div = $("<div>").text(clue.clue_text);
        if (clue.mode === 'SOLVED' || clue.mode === 'REVEALED') div.addClass("text-secondary");
        else div.addClass("font-weight-bold");
        return div;
    }

    _answer(clue) {
        return new AnswerGrid(clue.answer, false).grid;
    }

    _parsing(clue) {
        let parsing = $("<div>").addClass("h6 text-secondary");
        return (clue.parsing) ? parsing.text("["+clue.parsing+"]") : null;
    }

    _points(clue) {
        let hidden_icon = $("<i>").addClass("fa fa-eye-slash").attr('title','Hidden');
        let points = (clue.mode === "REVEALED") ? 0 : clue.points;
        return (this._isDetailHidden(clue)) ? hidden_icon : points;
    }

    _isDetailHidden(clue) {
        return (clue.mode === 'UNSOLVED' || clue.mode === 'PRESOLVE');
    }

    _showAnswerAndParsing(clue) {
        this._clueCell(clue,3).append(this._answer(clue)).append(this._parsing(clue));
    }

    _clueClicked = (event) => {
        let clueNum = parseInt($(event.target).closest("tr").find("td:nth-child(2)").text());
        this.activeRow = clueNum;
        let clue = this.clues[clueNum-1];
        let clueCell = this._clueCell(clue, 3);
        if (!this._isDetailHidden(clue))
            if (clueCell.children().length > 1) clueCell.children().not(":first").remove()
            else this._showAnswerAndParsing(clue);
        if (this.clues[clueNum-1].mode === "UNSOLVED") this.clickhandler(clueNum);
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * AnswerDialog
 */
class AnswerDialog {
    constructor(modalDialogID, submitAnswerHandler, revealAnswerHandler) {
        this.modalDialog = "#"+modalDialogID;
        this.submitHandler = submitAnswerHandler;
        this.revealHandler = revealAnswerHandler;
        this.answerGrid = null;
        this.activeClue = null;
        $("#id-submit-btn").on('click', this._submitClicked);
        $("#id-reveal-btn").on('click', this._revealClicked);
        $("#id-clear-btn").on('click', this._clearClicked);
    }

    show(clue) {
        this.activeClue = clue;
        this.answerGrid = new AnswerGrid(clue.answer, true);
        $(this.modalDialog).on('shown.bs.modal', () => { $(this.answerGrid.grid).focus(); });
        $(this.modalDialog).find(".modal-title").text("Clue #" + clue.clue_num);
        $(this.modalDialog).find("#id-clue-text").empty().html(clue.clue_text);
        $(this.modalDialog).find("#id-answer").empty().append(this.answerGrid.grid);
        $(this.modalDialog).find("#id-err-msg").empty();
        $(this.modalDialog).modal('show');
    }

    close() {
        $(this.modalDialog).modal('hide');
    }

    showErrorMsg(errMsg) {
        $(this.modalDialog).find("#id-err-msg").empty().text(errMsg);
    }

    _submitClicked = () => {
        let answerInput = this.answerGrid.readInput();
        if (answerInput.length === this.activeClue.answer.length)
            this.submitHandler(this.activeClue.clue_num, answerInput);
        else this.showErrorMsg("Incomplete answer");
    }

    _revealClicked = () => {
        this.revealHandler(this.activeClue.clue_num);
    }

    _clearClicked = () => {
        this.answerGrid.clear();
        $(this.modalDialog).find("#id-err-msg").empty();
        $(this.answerGrid.grid).focus()
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
        return this.elapsedSecs;
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