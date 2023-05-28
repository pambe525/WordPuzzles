/**
 * Derived templates use this function to bind their modal dialogs to a button
 */
function bindModalDialogToButton(dialogId, buttonId) {
    const modalDialog = document.querySelector(".modal-dialog#" + dialogId);
    document.querySelector("#" + buttonId).addEventListener('click', () => {
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
 * Converts a UTC date-time string in Y-mm-dd h:m:s format to local time
 */
function utcToLocalString(utcDateTimeString) {
    return new Date(utcDateTimeString + "Z").toLocaleString();
}

/**
 * Constructs a time log string given the parameters in the form:
 * 'Created by <username or me> on <local-date-time> and last edited on <local-date-time>'
 */
function getTimelogString(editorName, userName, utcCreatedAt, utcModifiedAt) {
    const name = (editorName === userName) ? "me" : userName;
    const createdAt = utcToLocalString(utcCreatedAt);
    const modifiedAt = utcToLocalString(utcModifiedAt);
    return "Created by " + name + " on " + createdAt + " and last edited on " + modifiedAt;
}

/**
 * This function should be overloaded by each client page of base.html
 */
function pageInit() {
}
