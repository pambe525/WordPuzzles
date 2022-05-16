class WordPuzzlePageView {
    constructor(clueSet, activeSession) {
        this.clueSet = clueSet;
        this.session = activeSession;
        this.cluesList = new CluesList(clueSet, "id-clues-list", this._clueClicked).show();
        this.answerDialog = new AnswerDialog("id-modal-answer-box", null, null);
        if (activeSession) this.sessionProgress = new SessionProgress(activeSession, this._saveTimer);
    }

    _clueClicked = (clueNum) => {
        this.answerDialog.show(this.clueSet[clueNum-1]);
        this.answerDialog.grid.focus();
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
            this.timer.pause();
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

    show(jqContainerId) {
        $(jqContainerId).empty().append(this._grid).show();
        if (this.isEditable) this.grid.focus();
        return this;
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
        grid.prop('maxlength', this.answer.length);
        grid.css('letter-spacing','6.2px').css('font', '14px consolas, monospace');
        grid.css('width', 14*this.answer.length + 2 + 'px').css('text-indent','2px');
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
        this._setClickHandler();
    }

    show() {
        for (const clue of this.clues) {
            this._setClueRowDetails(clue);
        }
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
        this._clueCell(clue,1).html(this._icon(clue))
        this._clueCell(clue,2).text(clue.clue_num + ".");
        this._clueCell(clue,3).html(this._clueDesc(clue));
        this._clueCell(clue,4).html(this._points(clue));
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

    _clueClicked = (event) => {
        let clueNum = parseInt($(event.target).closest("tr").find("td:nth-child(2)").text());
        let clue = this.clues[clueNum-1];
        let clueCell = this._clueCell(clue, 3);
        if (!this._isDetailHidden(clue))
            if (clueCell.children().length > 1) clueCell.children().not(":first").remove()
            else this._clueCell(clue,3).append(this._answer(clue)).append(this._parsing(clue));
        if (this.clues[clueNum-1].mode === "UNSOLVED") this.clickhandler(clueNum);
    }
}

/**--------------------------------------------------------------------------------------------------------------------
 * ClueBox
 */
class AnswerDialog {
    constructor(modalDialogID, submitAnswerHandler, revealAnswerHandler) {
        this.modalDialog = "#"+modalDialogID;
        this.submitHandler = submitAnswerHandler;
        this.revealHandler = revealAnswerHandler;
        this.answerGrid = null;
        $("#id-submit-btn").on('click', this._submitClicked);
        $("#id-reveal-btn").on('click', this._revealClicked);
        $("#id-clear-btn").on('click', this._clearClicked);
    }

    show(clue) {
        this.answerGrid = new AnswerGrid(clue.answer, true);
        $(this.modalDialog).find(".modal-title").text("Clue #" + clue.clue_num);
        $(this.modalDialog).find("#id-clue-text").empty().html(clue.clue_text);
        $(this.modalDialog).find("#id-answer").empty().append(this.answerGrid.grid);
        $(this.modalDialog).find("#id-err-msg").empty();
        $(this.modalDialog).modal('show');
    }

    _submitClicked = () => {

    }

    _revealClicked = () => {

    }

    _clearClicked = () => {
        this.answerGrid.clear();
        $(this.modalDialog).find("#id-err-msg").empty();
        $(this.answerGrid.grid).focus()
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
        return clue['clue_num'] + ". " + clue['clue_text'];
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
            clueText = clue.clue_text;
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