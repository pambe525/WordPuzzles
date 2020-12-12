class XWordGrid {

    cellSize = 29;
    jqGridObj = null;

    constructor(gridSize) {
        this.jqGridObj = $("<div></div>");
        for (var i = 0; i < gridSize * gridSize; i++)
            $(this.jqGridObj).append(this._createGridCell());
        this._setGridBoxStyling(gridSize);
    }

    getGridObj() {
        return this.jqGridObj;
    }

    _createGridCell() {
        var cell = $("<div></div>");
        cell.width(this.cellSize).height(this.cellSize);
        cell.css("border-top", "1px solid black").css("border-left", "1px solid black");
        cell.css("float","left").css("box-sizing","border-box");
        return cell;
    }

    _setGridBoxStyling(gridSize) {
        this.jqGridObj.width(this.cellSize * gridSize + 1).height(this.cellSize * gridSize + 1);
        this.jqGridObj.css("border-bottom", "1px solid black");
        this.jqGridObj.css("border-right", "1px solid black");
    }
}
