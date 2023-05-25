class ListBuilder {

    CRYPTIC_IMAGE = "cryptic-clues.jpg";
    NONCRYPTIC_IMAGE = "non-cryptic-clues.png";
    CRYPTIC_TITLE = "Cryptic Clues";
    NONCRYPTIC_TITLE = "Non-cryptic Clues";

    constructor(draftPuzzles) {

    }

    _createBadge(draftPuzzle, srcFileDir, baseUrl) {
        const badge = document.createElement("div");
        const imgFilePath = srcFileDir + this._getImageFileName(draftPuzzle.type);
        const linkUrl = baseUrl + "/" + draftPuzzle.id + "/";
        const img = this._createBadgeImage(imgFilePath, this._getImageTitle(draftPuzzle.type));
        const linkTitle = this._createBadgeTitleLink(draftPuzzle.title, linkUrl);
        const lastEdited = this._createLastEditedDiv(draftPuzzle.modified_at);
        const icon = this._createIcon("fa-trash-can", "Delete");
        const puzzleInfo = document.createElement("div").appendChild(linkTitle).appendChild(lastEdited);
        const iconGroup = this._createIconGroup(icon);
        badge.classList.add("list-badge");
        badge.appendChild(img).appendChild(puzzleInfo).appendChild(iconGroup);
    }

    _getImageFileName(puzzleType) {
        return (puzzleType === 0) ? this.NONCRYPTIC_IMAGE : this.CRYPTIC_IMAGE;
    }

    _getImageTitle(puzzleType) {
        return (puzzleType === 0) ? this.NONCRYPTIC_TITLE : this.CRYPTIC_TITLE;
    }

    _createIconGroup(icon) {
        const iconGroup = document.createElement("div");
        iconGroup.classList.add("r-float").add("icon-group");
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
        div.innerText = new Date(utcDateTime+"Z").toLocaleString();
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
        icon.classList.add("fa-regular").add(faName);
        icon.title = title;
        return icon;
    }
}