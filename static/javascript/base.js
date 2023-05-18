/* Derived templates use this function to bind their modal dialogs to button */
function bindModalDialogToButton(dialogId, buttonId) {
    const modalDialog = document.querySelector(".modal-dialog#"+dialogId);
    document.querySelector("#"+buttonId).addEventListener('click', () => {
        modalDialog.showModal();
    });
}

function setUpMenuToggleButton() {
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

    /* Highlight active nav link */
    const activePage = window.location.href;
    document.querySelectorAll(".navbar-links a").forEach(link => {
        if (link.href === activePage) link.classList.add("active");
    })
}