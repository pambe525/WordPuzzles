class XWordGrid {

    cellSize = 29;
    jqGridObj = null;
    size = 15;    /* default size */

    constructor(size) {
        if ( size ) this.size = size;
        this._createGrid();
        this._autonumberGrid();
    }

    getPuzzleHtml() {
        return this.jqGridObj;
    }

    //** PRIVATE METHODS **//
    _createGrid() {
        this.jqGridObj = $("<div></div>").addClass("xw-grid");
        for (var i = 0; i < this.size * this.size; i++)
            $(this.jqGridObj).append(this._createGridCell());
        this._setGridBoxStyling(this.size);
    }

    _createGridCell() {
        var cell = $("<div></div>");
        cell.width(this.cellSize).height(this.cellSize);
        cell.css("border-top", "1px solid black").css("border-left", "1px solid black");
        cell.css("float","left").css("box-sizing","border-box");
        return cell;
    }

    _setGridBoxStyling() {
        this.jqGridObj.width(this.cellSize * this.size + 1).height(this.cellSize * this.size + 1);
        this.jqGridObj.css("border-bottom", "1px solid black");
        this.jqGridObj.css("border-right", "1px solid black");
    }

    _gridCell(index) {
        return this.jqGridObj.children("div")[index];
    }

    _autonumberGrid() {
        let clueNum, span;
        for (clueNum = 1; clueNum <= this.size; clueNum++) {
            span = $("<span></span>").addClass("xw-number").text(clueNum);
            $(this._gridCell(clueNum-1)).append(span);
        }
        for (clueNum = this.size+1; clueNum <= this.size*2-1; clueNum++) {
            span = $("<span></span>").addClass("xw-number").text(clueNum);
            $(this._gridCell((clueNum-this.size)*this.size)).append(span);
        }
    }
}
