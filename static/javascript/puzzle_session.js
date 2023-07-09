let page = null;

function pageInit() {
    convertUTCDatesToLocal("timestamp");
    page = new PuzzleSessionPage(sessionId, puzzleId, csrfToken);
}

function clueTextClicked(element) {
    const clueNum = element.getAttribute("data-id");
    const clueText = element.textContent;
    page.showAnswerDialog(clueNum, clueText);
}
function revealClicked(element) {
    const clueNum = element.getAttribute("data-id");
    page.revealAnswer(clueNum);
}
class PuzzleSessionPage {
    constructor(sessionId, puzzleId, csrfToken) {
        this.sessionId = sessionId;
        this.puzzleId = puzzleId;
        this.csrfToken = csrfToken;
        this.answerDialog = new AnswerInputDialog("answer-dialog", this._submitAnswer);
        this.btnToggleDesc = document.getElementById("btnToggleDesc");
        this.btnToggleDesc.addEventListener('click', this.toggleDescHide)
        this.iconToggleDesc = document.querySelector(".icon-btn i");
        this.descPanel = document.querySelector("#desc-panel");
        this.btnStartSession = document.getElementById("startSessionBtn");
        if ( this.btnStartSession == null ) this.toggleDescHide();
    }

    toggleDescHide = () => {
        if ( this.descPanel.style.display === "none" ) {
            this.descPanel.style.display = "block";
            this.iconToggleDesc.classList.replace("fa-square-caret-down", "fa-square-caret-up");
        } else {
            this.descPanel.style.display = "none";
            this.iconToggleDesc.classList.replace("fa-square-caret-up", "fa-square-caret-down");
        }
    }

    showAnswerDialog(clueNum, clueText) {
        this.answerDialog.show(clueNum, clueText);
    }

    revealAnswer(clueNum) {
        const data = {clue_num: clueNum, session_id: this.sessionId, puzzle_id: this.puzzleId};
        this._postData("/ajax_answer_request", "reveal", data);
    }

    _submitAnswer = (data) => {
        data.session_id = this.sessionId;
        data.puzzle_id = this.puzzleId;
        this._postData("/ajax_answer_request", "check", data);
    }

    _postData(url, action, data) {
        fetch(url,{
            method: "POST",
            headers: {"X-CSRFToken": this.csrfToken, "Content-Type": 'application/json'},
            body: JSON.stringify({'action': action, 'data': data})
        }).then( response => {
            return response.json();
        }).then( data => {
            if (data['err_msg'] !== '') this.answerDialog.setMsg(data['err_msg']);
            else location.href = "/puzzle_session/" + this.puzzleId + "/";
        }).catch( error => { this.answerDialog.setMsg(error.toString()); } );
    }
}

class AnswerInputDialog {
    constructor(dialogId, submitHandler) {
        this.dialog = document.getElementById(dialogId);
        this.clueNumElement = document.querySelector("#"+dialogId+ " #clue-num");
        this.clueTextElement = document.querySelector("#"+dialogId+ " #clue-text");
        this.errMsgElement = document.querySelector("#"+dialogId+ " #err-msg");
        this.inputElement = document.querySelector("#"+dialogId+ " #answer-input");
        this.submitBtn = document.querySelector("#"+dialogId+ " #btnSubmit");
        this.closeBtn = document.querySelector("#"+dialogId+ " #btnClose");
        this.closeBtn.addEventListener('click', this._dialogCloseClicked);
        this.submitBtn.addEventListener('click', this._dialogSubmitClicked);
        this.submitHandler = submitHandler;
    }

    show(clueNum, clueText) {
        this.clueNumElement.textContent = clueNum;
        this.clueTextElement.textContent = clueText;
        this.inputElement.value = '';
        this.errMsgElement.textContent = '';
        this.dialog.showModal();
    }

    close() {
        this.dialog.close();
    }

    inputIsValid() {
        let input = this._getInputAnswer();
        if (input === '')
            this.errMsgElement.textContent = "Answer cannot be empty."
        else if (this._detectNonAlphabetCharacters(input) != null)
            this.errMsgElement.textContent = "Answer can only contain alphabets, hyphen and/or spaces.";
        else {
            let clueText = this.clueTextElement.textContent;
            let digitsStr = this._extractDigitContentInParenthesis( this._removeWhiteSpace(clueText) );
            if ( !this._hasMatchingLengths(digitsStr, input) )
                this.errMsgElement.textContent = "Answer does not match specified length in clue.";
            else this.errMsgElement.textContent = '';
        }
        return (this.errMsgElement.textContent === '');
    }

    setMsg(msg) {
        this.errMsgElement.textContent = msg;
    }

    _getInputAnswer() {
        // Remove extra spaces between words
        return this.inputElement.value.trim().replace(/\s+/g, " ");
    }

    _dialogCloseClicked = () => {
        this.dialog.close();
    }

    _dialogSubmitClicked = () => {
        const data = {
            clue_num: parseInt(this.clueNumElement.textContent), input_answer: this._getInputAnswer()
        }
        if ( this.inputIsValid() ) this.submitHandler(data);
    }

    _removeWhiteSpace(text) {
        return text.replace(/\s/g, '');
    }

    _extractDigitContentInParenthesis(text) {
        // Matches content within parenthesis at the end of the string if it contains digits
        const match = text.match(/\(([0-9,-]+)\)$/);
        return (match) ? match[1] : null;
    }

    _detectNonAlphabetCharacters(text) {
        // Matches non-alphabet characters excluding hyphen and space
        const match = text.match(/[^a-zA-Z\s\-]/);
        return (match) ? match[0] : null;
    }

    _hasMatchingLengths(digitsStr, answer) {
        answer = answer.replace(" ", ",");
        return (digitsStr === this._replaceWordsWithLengths(answer));
    }
    _replaceWordsWithLengths(text) {
      return text.replace( /\b\w+\b/g, function(match){ return match.length; } );
    }
}

