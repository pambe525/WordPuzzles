/**
 * This class provides methods to build a list of badges for each puzzle in a list
 */
class PuzzlesListBuilder {

    CRYPTIC_IMAGE = "cryptic-clues.jpg";
    NONCRYPTIC_IMAGE = "non-cryptic-clues.png";
    puzzlesList = [];
    srcFileDir = null;
    baseUrl = null;
    badges = [];

    constructor(puzzles, srcFileDir, baseUrl) {
        this.puzzlesList = puzzles;
        this.srcFileDir = srcFileDir;
        this.baseUrl = baseUrl;
    }

    showList(containerId) {
        const containerDiv = document.getElementById(containerId);
        containerDiv.innerHTML = "";
        if (this.puzzlesList.length > 0) {
            if (this.badges.length === 0) this.buildBadges();
            for (let i = 0; i < this.badges.length; i++)
                containerDiv.appendChild(this.badges[i]);
        } else containerDiv.innerHTML = "No puzzles to list.";
    }

    buildBadges() {
        if (this.puzzlesList.length === 0) return;
        this.badges = [];
        for (let i = 0; i < this.puzzlesList.length; i++)
            this.badges.push(this._createBadge(this.puzzlesList[i]));
    }

    addDeleteBtns() {
        let iconGroup = null, iconBtn = null;
        for (let i = 0; i < this.badges.length; i++) {
            iconGroup = this.badges[i].getElementsByClassName("icon-group")[0];
            iconBtn = this._createDeleteBtn(this.puzzlesList[i].id)
            iconGroup.appendChild(iconBtn);
        }
    }

    _createBadge(puzzle) {
        const badge = document.createElement("div");
        const imgFilePath = this.srcFileDir + this._getImageFileName(puzzle.type);
        const img = this._createBadgeImage(imgFilePath, puzzle.type_text);
        const linkTitle = this._createBadgeTitleLink(puzzle);
        const lastEdited = this._createLastEditedDiv(puzzle.utc_modified_at);
        const icon = this._createIconBtn("fa-trash-can", "Delete", puzzle.id);
        const puzzleInfo = this._createPuzzleInfo(linkTitle, lastEdited);
        const iconGroup = this._createIconGroup();
        badge.classList.add("list-badge");
        badge.appendChild(img);
        badge.appendChild(puzzleInfo);
        badge.appendChild(iconGroup);
        return badge;
    }

    _getImageFileName(puzzleType) {
        return (puzzleType === 0) ? this.NONCRYPTIC_IMAGE : this.CRYPTIC_IMAGE;
    }

    _createPuzzleInfo(linkTitle, lastEdited) {
        const puzzleInfo = document.createElement("div");
        puzzleInfo.appendChild(linkTitle);
        puzzleInfo.appendChild(lastEdited);
        return puzzleInfo;
    }

    _createIconGroup() {
        const iconGroup = document.createElement("div");
        iconGroup.classList.add("r-float");
        iconGroup.classList.add("icon-group");
        return iconGroup;
    }

    _createBadgeImage(srcFilePath, titleText) {
        const img = document.createElement("img");
        img.classList.add("thumbnail");
        img.setAttribute("src", srcFilePath);
        img.title = titleText;
        img.setAttribute("alt", titleText);
        return img;
    }

    _createLastEditedDiv(utcDateTime) {
        const div = document.createElement("div");
        div.classList.add("small-text");
        div.innerText = "Last edited on " + this._utc_to_local(utcDateTime);
        return div;
    }

    _createBadgeTitleLink(puzzle) {
        const title = document.createElement("a");
        title.classList.add("bold-text");
        title.setAttribute("href", "/edit_puzzle/"+puzzle.id+"/");
        title.innerText = puzzle.title;
        return title;
    }

    _createIconBtn(faName, title, puzzle_id) {
        const btn = document.createElement("button");
        const icon = document.createElement("i");
        icon.classList.add("fa-regular");
        icon.classList.add(faName);
        icon.title = title;
        btn.appendChild(icon);
        icon.id = "btn" + title + "_" + puzzle_id;
        btn.classList.add("icon-btn");
        return btn;
    }

    _createDeleteBtn(puzzle_id) {
        const link = document.createElement("a");
        const icon = document.createElement("i");
        icon.classList.add("fa-regular");
        icon.classList.add("fa-trash-can");
        icon.title = "Delete";
        link.setAttribute("href", "/delete_puzzle/" + puzzle_id + "/")
        link.appendChild(icon);
        link.classList.add("icon-btn");
        return link;
    }
    _utc_to_local(utc_datetime) {
        return new Date(utc_datetime).toLocaleString();
    }
}