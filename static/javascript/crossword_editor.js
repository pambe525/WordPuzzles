CrosswordEditor = (function() {

    var gridId = null;
    var selectSizeId = null;
    var btnResetId = null;
    var selectModeId = null;
    var spanModeHelpId = null;
    var XWord = null;

    /* PRIVATE METHODS */
    function setModeHelpText() {
        var msg;
        var selectMode = parseInt($(selectModeId).val());
        if (selectMode === 1)
            msg = "Click on a grid square to block it. Re-select to unblock. " +
                "Diametrically opposite square will also be blocked using 180 deg. rotational symmetry.";
        else
            msg = "Click on a numbered square to edit ACROSS or DOWN answer. " +
                "Re-select to toggle between ACROSS and DOWN answers if applicable";
        $(spanModeHelpId).text(msg);
    }

    function setWidgetStates() {
        if (XWord.hasBlocks()) {
            $(selectSizeId).prop("disabled", true);
            $(btnResetId).prop("disabled", false);
        } else {
            $(selectSizeId).prop("disabled", false);
            $(btnResetId).prop("disabled", true);
        }
    }

    function sizeSelectionChanged() {
        var gridSize = parseInt($(selectSizeId).val());
        XWord = new Crossword(gridId, cellClicked, gridSize);
    }

    function resetBtnClicked() {
        var msg = "All changes to grid will be lost. Please confirm or cancel."
        if ( confirm(msg) ) {
            var gridSize = parseInt($(selectSizeId).val());
            XWord = new Crossword(gridId, cellClicked, gridSize);
            setWidgetStates();
        }
    }

    function modeSelectionChanged() {
        setModeHelpText();
    }

    function cellClicked(event) {
        if ( parseInt($(selectModeId).val()) === 1) {
            XWord.toggleCellBlock(event.target.id);
            setWidgetStates();
        }
    }

    /* PUBLIC METHODS */
    return {
        reset: function() {
            gridId = null;
            selectSizeId = null;
            btnResetId = null;
            selectModeId = null;
            spanModeHelpId = null;
            XWord = null;
        },

        initialize: function(divId) {
            if ($("#" + divId).length === 0) throw new Error("divId does not exist");
            gridId = divId;
            if ( !selectSizeId ) throw new Error("Size selector not set");
            var gridSize = parseInt($(selectSizeId).val());
            XWord = new Crossword(gridId, cellClicked, gridSize);
            setModeHelpText();
            setWidgetStates();
        },

        setSizeSelectorId: function(selectorId) {
            var jqId = "#" + selectorId;
            if ($(jqId).length === 0) throw new Error("Size selector does not exist");
            selectSizeId = jqId;
            $(selectSizeId).change(sizeSelectionChanged);
        },

        setResetBtnId: function(btnId) {
            var jqId = "#" + btnId;
            if ($(jqId).length === 0) throw new Error("Reset button does not exist");
            btnResetId = jqId;
            $(btnResetId).click(resetBtnClicked);
        },

        setModeSelectorId: function(selectorId) {
            var jqId = "#" + selectorId;
            if ($(jqId).length === 0) throw new Error("Mode selector does not exist");
            selectModeId = jqId;
            $(selectModeId).change(modeSelectionChanged);
        },

        setModeHelpId: function(spanId) {
            var jqId = "#" + spanId;
            if ($(jqId).length === 0) throw new Error("Mode help span does not exist");
            spanModeHelpId = jqId;
        },
     }
})();