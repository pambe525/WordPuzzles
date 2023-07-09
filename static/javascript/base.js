/**
 * Derived templates use this function to bind their modal dialogs to a button
 */
function bindModalDialogToButton(dialogId, buttonId) {
    const modalDialog = document.querySelector(".modal-dialog#" + dialogId);
    const btn = document.querySelector("#" + buttonId);
    if (btn != null) btn.addEventListener('click', () => {
        modalDialog.showModal();
    });
}

/**
 * Sets up side nav toggle button (hamburger icon)
 */
function setUpNavMenuToggleButton() {
    const toggleButton = document.getElementsByClassName("menu-toggle-button")[0];
    const navbar = document.getElementsByClassName("navbar")[0];
    const glasspane = document.getElementsByClassName("glasspane")[0];
    toggleButton.addEventListener('click', () => {
        navbar.classList.toggle("active");
        glasspane.classList.toggle("active");
    });
    glasspane.addEventListener('click', () => {
        navbar.classList.toggle("active");
        glasspane.classList.toggle("active");
    })
}

/**
 * Highlights the active page in the side nav bar
 */
function highlightActiveNavItem() {
    const activePage = window.location.href;
    document.querySelectorAll(".navbar-links a").forEach(link => {
        if (link.href === activePage) link.classList.add("active");
    })
}

/**
 * Converts all UTC date-time strings in Y-mm-dd h:m:s format to local time for all
 * elements with given class name
 */
function convertUTCDatesToLocal(className) {
    const dates = document.getElementsByClassName(className);
    for (let i = 0; i < dates.length; i++)
        dates[i].innerText = utcToLocalString(dates[i].innerText + "Z");
}

/**
 * Converts a UTC date-time string in Y-mm-dd h:m:s format to local time
 */
function utcToLocalString(utcDateTimeString) {
    let dateString = new Date(utcDateTimeString).toLocaleString()
    dateString = dateString.replace(/:(\d{2})(?=\s[ap]m)/gi, '')
    return (utcDateTimeString) ? dateString : "";
}

/**
 * Constructs a time log string given the parameters in the form:
 * 'Created by <username or me> on <local-date-time> and last edited on <local-date-time>'
 */
function getTimelogString(puzzleData, userName) {
    const name = (puzzleData.editorName === userName) ? "me" : userName;
    const createdAt = utcToLocalString(puzzleData.utcCreatedAt);
    const modifiedAt = utcToLocalString(puzzleData.utcModifiedAt);
    const sharedAt = utcToLocalString(puzzleData.utcSharedAt);
    return (sharedAt) ? "Posted by " + name + " on " + sharedAt :
        "Created by " + name + " on " + createdAt + " and last edited on " + modifiedAt;
}

/**
 * Sets up and shows the modal confirm dialog
 */
function showConfirmDialog(title, message, actionUrl) {
    const dialog = document.getElementById("confirm-dialog")
    dialog.getElementsByClassName("confirm-dialog-form")[0].setAttribute('action', actionUrl)
    dialog.getElementsByClassName("subtitle")[0].textContent = title;
    dialog.getElementsByClassName("confirm-dialog-message")[0].textContent = message;
    dialog.showModal();
}

/**
 * This function should be overloaded by each client page of base.html
 */
function pageInit() {
}
