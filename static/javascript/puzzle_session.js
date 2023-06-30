function pageInit() {
    convertUTCDatesToLocal("timestamp");
    if ( document.getElementById("startSessionBtn") == null ) toggleDescHide();
}

function toggleDescHide() {
    const toggle = document.querySelector(".icon-btn i");
    const panel = document.querySelector("#desc-panel")
    if ( panel.style.display === "none" ) {
        panel.style.display = "block";
        toggle.classList.replace("fa-square-caret-down", "fa-square-caret-up");
    } else {
        panel.style.display = "none";
        toggle.classList.replace("fa-square-caret-up", "fa-square-caret-down");
    }
}

function clueTextClicked(element) {
    const clueNum = element.getAttribute("data-id");
    const clueText = element.textContent;
    const answerDialog = new AnswerInputDialog("answer-dialog", submitAnswer);
    answerDialog.show(clueNum, clueText);
}

function submitAnswer(data) {
    postData("/check_answer")
}

function postData(url, data) {
  fetch(url,{method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)})
      .then(response => response.json())
      .then(data => {})
      .catch(error => {});
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
    }

    show(clueNum, clueText) {
        this.clueNumElement.textContent = clueNum;
        this.clueTextElement.textContent = clueText;
        this.inputElement.value = '';
        this.errMsgElement.textContent = '';
        this.dialog.showModal();
    }

    inputIsValid() {
        const input = this.inputElement.value.trim();
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

    _dialogCloseClicked = () => {
        this.dialog.close();
    }

    _dialogSubmitClicked = () => {
        this.inputIsValid();
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

