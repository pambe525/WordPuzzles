class ListBuilder {

    CRYPTIC_IMAGE = "cryptic-clues.jpg";
    NONCRYPTIC_IMAGE = "non-cryptic-clues.png";
    draftPuzzles = null;
    srcFileDir = null;
    baseUrl = null;

    constructor(draftPuzzles, srcFileDir, baseUrl) {
        this.draftPuzzles = draftPuzzles;
        this.srcFileDir = srcFileDir;
        this.baseUrl = baseUrl;
    }

    buildHtml(containerId) {
        const containerDiv = document.getElementById(containerId);
        containerDiv.innerHTML = "";
        if (this.draftPuzzles.length === 0) containerDiv.innerHTML = "No draft puzzles.";
        else {
            for (var i = 0; i < this.draftPuzzles.length; i++) {
                var badge = this._createBadge(this.draftPuzzles[i]);
                containerDiv.appendChild(badge);
            }
        }
    }

    _createBadge(draftPuzzle) {
        const badge = document.createElement("div");
        const imgFilePath = this.srcFileDir + this._getImageFileName(draftPuzzle.type);
        const linkUrl = this.baseUrl + "/" + draftPuzzle.id + "/";
        const img = this._createBadgeImage(imgFilePath, draftPuzzle.type_text);
        const linkTitle = this._createBadgeTitleLink(draftPuzzle.title, linkUrl);
        const lastEdited = this._createLastEditedDiv(draftPuzzle.utc_modified_at);
        const icon = this._createIcon("fa-trash-can", "Delete");
        const puzzleInfo = this._createPuzzleInfo(linkTitle, lastEdited);
        const iconGroup = this._createIconGroup(icon);
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
    _createIconGroup(icon) {
        const iconGroup = document.createElement("div");
        iconGroup.classList.add("r-float");
        iconGroup.classList.add("icon-group");
        iconGroup.appendChild(icon);
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
        div.innerText = "Last edited on " + new Date(utcDateTime).toLocaleString();
        return div;
    }

    _createBadgeTitleLink(titleText, linkUrl) {
        const title = document.createElement("a");
        title.classList.add("bold-text");
        title.setAttribute("href", linkUrl);
        title.innerText = titleText;
        return title;
    }

    _createIcon(faName, title) {
        const icon = document.createElement("i");
        icon.classList.add("fa-regular");
        icon.classList.add(faName);
        icon.title = title;
        return icon;
    }
}