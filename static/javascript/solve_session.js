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
    const dialog = document.getElementById("answer-dialog");
    const clueText = document.getElementById("clue-text");
    const input = document.getElementById("answer")
    const errMsg = document.getElementById("err-msg")
    clueText.textContent = clueNum + ". " + element.textContent;
    input.value = '';
    errMsg.textContent = '';
    dialog.showModal();
}
function dialogCloseClicked() {
    const dialog = document.getElementById("answer-dialog");
    dialog.close();
}
function dialogSubmitClicked() {
    let clueText = document.getElementById("clue-text").textContent;
    const msg = document.getElementById("err-msg");
    const input = document.getElementById("answer").value;
    if (detectNonAlphabetCharacters(input) != null)
        msg.textContent = "Answer can only contain alphabets, hyphen and/or spaces.";
    else {
        let digitsStr = extractDigitContentInParenthesis( removeWhiteSpace(clueText) );
        if ( !hasMatchingLengths(digitsStr, input) )
            msg.textContent = "Answer does not match specified length in clue.";
        else msg.textContent = '';
    }
}
function removeWhiteSpace(text) {
    return text.replace(/\s/g, '');
}
function extractDigitContentInParenthesis(text) {
    // Matches content within parenthesis at the end of the string if it contains digits
    const match = text.match(/\(([0-9,-]+)\)$/);
    return (match) ? match[1] : null;
}
function detectNonAlphabetCharacters(text) {
    // Matches non-alphabet characters excluding hyphen and space
    const match = text.match(/[^a-zA-Z\s\-]/);
    return (match) ? match[0] : null;
}
function hasMatchingLengths(digitsStr, answer) {
    answer = answer.replace(" ", ",");
    return (digitsStr === replaceWordsWithLengths(answer));
}
function replaceWordsWithLengths(text) {
  return text.replace(/\b\w+\b/g, function(match) {
    return match.length;
  });
}
