(function() {
    //==> TESTCASE HELPERS
    let controller = null;
    let puzzleData = null;
    function getGridCells() {
        return $("#puzzle > div").children("div");
    }
    function saveData(responseData) {
        ajaxSettings = null;
        $("#save").click();
        ajaxSettings.success(responseData);
    }
    function verifyClueNums(clueNums) {
        let gridCells = getGridCells();
        let keys = Object.keys(clueNums);
        for (const i in keys)
            assert.equal($(gridCells[keys[i]]).children("span.xw-number").text(), clueNums[keys[i]]);
    }
    function clickOnCell(index) {
        getGridCells()[index].click();
    }
    function gridCell(index) {
        return $(getGridCells()[index]);
    }
    function doClueFormInput(clueWord, clueText) {
            $("#clue-word").val(clueWord);
            $("#clue-text").val(clueText);
            $("#clue-update").click();
        }
    function assertClueFormFields(clueRef, word, clueText, msg) {
        assert.equal($("#clue-ref").text(), clueRef);
        assert.equal($("#clue-word").val(), word);
        assert.equal($("#clue-text").val(), clueText);
        assert.equal($("#clue-msg").text(), msg);
    }
    function readLetterInCell(cell) {
            return $(cell).children(".xw-letter").text();
        }
    function assertHilitedWord(word) {
        let hilitedCells = $(getGridCells()).filter(".xw-hilite");
        assert.equal(hilitedCells.length, word.length);
        let letter;
        for (let i = 0; i < hilitedCells.length; i++) {
            letter = (word[i] === " ") ? "" : word[i].toUpperCase();
            assert.equal(readLetterInCell(hilitedCells[i]), letter);
        }
    }
    function setBlocks(cellIndices) {
        for (let i = 0; i < cellIndices.length; i++)
            clickOnCell(cellIndices[i]);
    }
    function assertHilitedCells(cellIndex, hiliteCellIndices) {
        if (cellIndex !== null) clickOnCell(cellIndex);
        let gridCells = getGridCells();
        assert.equal($(gridCells).filter(".xw-hilite").length, hiliteCellIndices.length);
        for (let i = 0; i < hiliteCellIndices.length; i++)
           assert.true($(gridCells[hiliteCellIndices[i]]).hasClass("xw-hilite"));
    }
    function assertHasRedLetters(flagsArray){
        var letterCells = $(getGridCells()).filter(".xw-hilite").children(".xw-letter");
        for (let i = 0; i < letterCells.length; i++) {
            if (flagsArray[i]) assert.true($(letterCells[i]).hasClass("xw-red"));
            else assert.false($(letterCells[i]).hasClass("xw-red"));
        }
    }

    //==> XWordEditor Initialization
    QUnit.module("XWordEditor::Instantiation", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test('Throws error if puzzleData is null', function (assert) {
        assert.throws(function () {
            new XWordEditor();
        }, /Puzzle data is required/);
    });
    test('Customizes labels on page', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal($("#size-label").text(), "Grid Size");
        assert.equal($("#radio1-label").text(), "Blocks");
        assert.equal($("#radio2-label").text(), "Clues");
        assert.equal($("#save-ok").is(":hidden"), true);
    });
    test('Sets size selector dropdown with correct options', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let options = $("#size > option");
        let textVals = $.map(options, function (option) {
            return option.text;
        });
        let values = $.map(options, function (option) {
            return parseInt(option.value);
        });
        assert.equal(options.length, 7);
        assert.deepEqual(textVals, ["5x5", "7x7", "9x9", "11x11", "13x13", "15x15", "17x17"])
        assert.deepEqual(values, [5, 7, 9, 11, 13, 15, 17]);
    });
    test('Sets specified grid size in dropdown', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal($("#size").val(), puzzleData.size);
    });
    test('Creates grid using specified size in data', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        assert.equal(getGridCells().length, 25);
    });
    test('Sets correct title and state of widgets on new puzzle', function (assert) {
        let puzzleData = {id:0, size: 5};
        new XWordEditor(puzzleData);
        assert.equal($("#page-title").text(), "New Crossword");
        assert.true($("#delete").prop("disabled"));
        assert.true($("#publish").prop("disabled"));
        assert.true($("#unpublish").is(":hidden"));
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#radio-1").prop("checked"));
    });
    test('Sets correct title and state of widgets on existing puzzle', function (assert) {
        let puzzleData = {id: 10, size: 5, desc: "xword 10"};     // ID=10 indicates exisiting puzzle edit
        new XWordEditor(puzzleData);
        assert.equal($("#page-title").text(), "Edit Crossword #10");
        assert.false($("#delete").prop("disabled"));
        assert.true($("#publish").prop("disabled"));
        assert.equal($("#desc").text(), "xword 10");
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#radio-1").prop("checked"));
    });
    test('Redraws grid to new size when grid size changes', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        $("#size").val(7).change();
        assert.equal(getGridCells().length, 49);
    });
    test('Switches to block edit and hides form when grid size changes in clues mode', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let radio2 = $("#radio-2");
        radio2.prop("checked", true).change();  // Toggle edit mode
        assert.true(radio2.is(":checked"));
        $("#size").val(7).change();
        assert.false(radio2.is(":checked"));
        assert.true($("#clue-form").is(":hidden"));
    });
    test('Shows confirmation box when grid size changes after adding blocks', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        let gridCells = getGridCells();
        gridCells[0].click();  // Create a block
        confirmMessage = "";
        confirmResponse = false;
        let selector = $("#size");
        selector.val(7).change();
        assert.equal(confirmMessage, "All changes to grid will be cleared");
        assert.equal(gridCells.length, 25);    // No change to grid
        assert.equal(selector.val(), 5);       // Should revert back to previous selection
    });
    test('Changes grid size change on confirmation after adding blocks', function (assert) {
        let puzzleData = {id: 0, size: 5}
        new XWordEditor(puzzleData);
        getGridCells()[0].click();  // Create a block
        confirmResponse = true;
        let selector = $("#size");
        selector.val(7).change();
        assert.equal(getGridCells().length, 49);    // Grid changed
        assert.equal(selector.val(), 7);       // New selection
    });
    test('Sets dataSaved to false after grid size is changed', function (assert) {
        let puzzleData = {id: 0, size: 5}
        let controller = new XWordEditor(puzzleData);
        saveData({});
        $("#size").val(7).change();
        assert.false(controller.view.dataSaved);
    });
    test('Sets grid to default size (15) if not specified', function (assert) {
        let puzzleData = {id:0};
        new XWordEditor(puzzleData);
        assert.equal(getGridCells().length, 225);
        assert.equal($("#size").val(), 15);
    });
    test('Sets grid bounding box to correct width & height', function (assert) {
        var gridSize = 5;
        new XWordEditor({size: gridSize});
        assert.equal(getGridCells().length, 25);
        let gridBox = $("#puzzle>div");
        assert.equal(gridBox.width(), (29 * gridSize + 1));
        assert.equal(gridBox.height(), (29 * gridSize + 1));
    });
    test('Autonumbers grids with no blocks', function (assert) {
        var gridSize = 5;
        new XWordEditor({size: gridSize});
        let clueNums = {0:"1",1:"2",2:"3",3:"4",4:"5",5:"6",10:"7",15:"8",20:"9"};
        verifyClueNums(clueNums);
     });
    test('Sets dataSaved to false after description is changed', function (assert) {
        let puzzleData = {id: 0, size: 5}
        let controller = new XWordEditor(puzzleData);
        saveData({});
        $("#desc").text("Some text").change();
        assert.false(controller.view.dataSaved);
    });
    test('Restores blocked cells in grid from existing data', function (assert) {
        var gridSize = 5, blockStr = "1,2,7,17,22,23";
        new XWordEditor({size: gridSize, data:{blocks: blockStr}});
        let gridCells = getGridCells();
        let blockedCells = gridCells.filter(".xw-block");
        let blockedIndices = blockStr.split(",");
        assert.equal(blockedCells.length, blockedIndices.length);
        for (var i = 0; i < blockedIndices.length; i++)
            assert.true($(gridCells[parseInt(blockedIndices[i])]).hasClass("xw-block"));
    });

    //--> XWordEditor::Restore Data
    QUnit.module("XWordEditor::Restore Data", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test('Switches to clues edit mode when existing word data is restored', function (assert) {
        var gridSize = 5, blockStr = "1,2,7,17,22,23";
        var puzzleData = {id: 10, size: gridSize, data:{
            blocks: blockStr, across:{"0-0":{word:"ABCDE", clue:"1 across (5)"}}, down:{}}
        }
        new XWordEditor(puzzleData);
        assert.true($("#radio-2").prop("checked"));
        assert.false($("#clue-form").prop("hidden"));
     });
    test('Hilites word in grid and loads clue form when data is restored', function (assert) {
        var gridSize = 5, blockStr = "";
        var puzzleData = {
            id: 10, size: gridSize, data:{blocks: blockStr, across:{0:{word:"ABCDE", clue:""}}, down:{}}
        }
        new XWordEditor(puzzleData);
        let hilitedCells = getGridCells().slice(0,5);
        assert.true($(hilitedCells).hasClass("xw-hilite"));
        assertHilitedWord("ABCDE");
        assertClueFormFields("#1 Across (5)", "ABCDE", "", "");
     });
    test('Sets dataSaved to true after data is restored', function (assert) {
        var gridSize = 5, blockStr = "";
        var puzzleData = {
            id: 10, size: gridSize, data:{blocks: blockStr, across:{0:{word:"ABCDE", clue:""}}, down:{}}
        }
        controller = new XWordEditor(puzzleData);
        assert.true(controller.view.dataSaved);
     });
    test('Sets Published state if restored xword is published', function (assert) {
        let gridData = {
            blocks:"0,1,23,24",
            across:{2: {word: "PUP", clue: "clue for 1a"}, 5: {word: "SIENA", clue: "clue for 4a"},
                    10: {word: "ADDUP", clue: "clue for 6a"}, 15: {word: "LLAMA", clue:"clue for 7a"},
                    20: {word: "EEL", clue: "clue for 8a"}},
            down:  {2: {word: "PEDAL", clue: "clue for 1d"}, 3: {word: "UNUM", clue: "clue for 2d"},
                    4: {word: "PAPA", clue: "clue for 3d"}, 5: {word: "SALE", clue: "clue for 4d"},
                    6: {word: "IDLE", clue: "clue for 5d"}}
        }
        let timestamp = new Date().toISOString();
        puzzleData = {id: 10, size: 5, is_xword: true, desc: "Crosword", shared_at: timestamp, data: gridData};
        new XWordEditor(puzzleData);
        assert.true($("#publish").is(":hidden"));
        assert.false($("#unpublish").is(":hidden"));
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#navbar").is(":hidden"));
        clickOnCell(3);   // Hiliting should be disabled
        assert.equal($(getGridCells()).filter(".xw-hilite").length, 0);
    })
    // Existing puzzle - Hilites the first incomplete clue across or down
    // Existing puzzle - Hides form if all clues are complete and enables publish
    // Loads words and colors them

    //==> XWordEditor::Save/Delete
    QUnit.module("XWordEditor::Save/Delete", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test('Includes correct data in ajax call for new xword on save', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        $("#save").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxSettings.method, "POST");
        assert.equal(ajaxSettings.dataType, "json");
        assert.equal(ajaxSettings.data.action, "save");
        assert.equal(ajaxData.id, puzzleData.id);
        assert.equal(ajaxData.size, puzzleData.size);
        assert.equal(ajaxData.is_xword, true);
        assert.equal(ajaxData.shared_at, null);
        assert.deepEqual(ajaxData.data, {blocks:"",across:{}, down:{}});
    });
    test('Includes correct data in ajax call for existing xword on save', function (assert) {
        let puzzleData = {id: 10, size: 7, desc: "xword #10"}
        new XWordEditor(puzzleData);
        $("#save").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxData.id, puzzleData.id);
        assert.equal(ajaxData.size, puzzleData.size);
        assert.equal(ajaxData.desc, puzzleData.desc);
        assert.deepEqual(ajaxData.data, {blocks:"",across:{}, down:{}});
    });
    test('Includes changes to desc in ajax call on save', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        let descField = $("#desc");
        descField.text("This is a crossword");
        $("#save").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxData.desc, descField.text());
    });
    test('Includes full data in ajax call for xword on save', function (assert) {
        let gridData = {
            blocks:"0,4,12,20,24",
            across:{1: {word: "abcd", clue: "clue for 1a"}, 5: {word: "efghi", clue: "clue for 4a"}},
            down:{1: {word: "jklmn", clue:""}, 2:{word:"op", clue:"clue for 2d"}}
        }
        let puzzleData = {id: 10, size: 5, desc: "xword #10", data: gridData};
        new XWordEditor(puzzleData);
        $("#save").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.deepEqual(ajaxData.data, gridData);
    });
    test('Enables delete button after successful save', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        saveData({});
        assert.equal($("#delete").prop("disabled"), false);
        assert.false($("#save-ok").is(":hidden"));
    });
    test('Includes puzzle id when saving data a second time ', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        let saveBtn = $("#save");
        saveData({id: 10, error_message: ""});  // First save with id=0, as new puzzle
        saveData({});                          // Second save - id should be updated from first save
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.equal(ajaxData.id, 10);
    });
    test('Displays alert message when trapped error occurs on save', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        let msg = "Trapped error";
        saveData({error_message: msg});
        assert.equal(alertMessage, msg);
        assert.equal($("#save-ok").is(":hidden"), true);
        assert.equal($("#delete").prop("disabled"), true);
    });
    test('Displays alert message when system error occurs on save', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        ajaxSettings = null;
        $("#save").click();
        let msg = "System error occurred";
        ajaxSettings.error(null, null, msg);
        assert.equal(alertMessage, msg);
    });
    test('Sets dataSaved to true on successful save', function (assert) {
        let puzzleData = {id: null, size: 5}
        let controller = new XWordEditor(puzzleData);
        assert.false(controller.view.dataSaved);
        saveData({});
        assert.true(controller.view.dataSaved);
    });
    test('Shows confirm box before deleting - cancel takes no action', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        $("#save").click();          // First save the grid to enable Delete btn
        confirmResponse = false;     // Cancel confirmation box
        $("#delete").click();
        assert.true(confirmMessage.indexOf("All saved data will be permanently deleted.") === 0);
        assert.equal(getGridCells().length, 25)
    });
    test('Makes ajax call to delete puzzle on confirmation', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        saveData({id: 15});           // First save the grid to enable Delete btn
        confirmResponse = true;      // Confirm delete
        $("#delete").click();
        assert.equal(ajaxSettings.method, "POST");
        assert.equal(ajaxSettings.dataType, "json");
        assert.equal(ajaxSettings.data.action, "delete");
        assert.equal(ajaxSettings.data.id, 15);
    });
    test('Displays alert message when system error occurs on delete', function (assert) {
        let puzzleData = {id: null, size: 5}
        new XWordEditor(puzzleData);
        $("#save").click();          // First save the grid to enable Delete btn
        confirmResponse = true;      // Confirm delete
        ajaxSettings = alertMessage = null;
        $("#delete").click();
        let msg = "System error occurred";
        ajaxSettings.error(null, null, msg);
        assert.equal(alertMessage, msg);
    });

    //==> XWordEditor::Block Editing
    QUnit.module("XWordEditor::Block Editing", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            controller = new XWordEditor({id: null, size: 5});       }
    });
    test('Enables cell blocking in block edit mode ', function (assert) {
        clickOnCell(0);
        assert.true($(gridCell(0)).hasClass("xw-block"));
    });
    test('Clears numbering in cell when it is blocked', function (assert) {
        clickOnCell(0);
        assert.equal(gridCell(0).children("span.xw-number").length, 0);
    });
    test('Retains block editing when grid size is reset', function (assert) {
        $("#size").val(7).change();
        clickOnCell(0);
        assert.true(gridCell(0).hasClass("xw-block"));
    });
    test('Unlocks cell when cell is re-clicked', function (assert) {
        clickOnCell(1);
        clickOnCell(1);   // Second click
        assert.false(gridCell(1).hasClass("xw-block"));
    });
    test('Blocks symmetric cell with rotational symmetry', function (assert) {
        clickOnCell(6);
        assert.true(gridCell(18).hasClass("xw-block"));
        clickOnCell(23);
        assert.true(gridCell(1).hasClass("xw-block"));
    });
    test('Blocks center cell in grid without symmetry', function (assert) {
        clickOnCell(12);   // Center cell
        assert.true(gridCell(12).hasClass("xw-block"));
    });
    test('Auto-numbers grid after cell block/unblock', function (assert) {
        clickOnCell(0);   // corner cells
        clickOnCell(4);   // corner cells
        clickOnCell(12);  // center cell
        let clueNums = {1:"1",2:"2",3:"3",5:"4",9:"5",10:"6",13:"7",15:"8",17:"9",21:"10"};
        verifyClueNums(clueNums);
    });
    test('Sets dataSaved to false after blocking/unblocking a grid cell', function (assert) {
        saveData({});
        clickOnCell(8);   // block a cell
        assert.false(controller.view.dataSaved);
        saveData({});
        clickOnCell(8);   // unblock cell
        assert.false(controller.view.dataSaved);
    });
    test("Does not block cell if it or symm cell contains a letter", function(assert) {
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("trial", "");
        $("#radio-1").prop("checked", true).change();
        clickOnCell(0);
        assert.false($(gridCell(0)).hasClass("xw-block"));
        clickOnCell(23);
        assert.false($(gridCell(1)).hasClass("xw-block"));
    });
    //==> Unblocking cells that are word start or end

    //==> XWordEditor::Add Clues
    QUnit.module("XWordEditor::Add Clue", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            controller = new XWordEditor({id: null, size: 5});
            $("#radio-2").prop("checked", true).change();
        }
    });
    test('Shows clue edit form and sets focus on word input', function (assert) {
        assert.false($("#clue-form").prop("hidden"));
        assert.true($("#clue-word").is(":focus"));
    });
    test('Hides clue edit form after switching back to block edit mode', function (assert) {
        $("#radio-1").prop("checked", true).change();  // Switch back to Block edit mode
        assert.true($("#clue-form").is(":hidden"));
    });
    test('Disables blocking selected cells when in clue edit mode', function (assert) {
        getGridCells()[0].click();
        assert.false($(getGridCells()[0]).hasClass("xw-block"));
    });
    test('Initializes clue form with default hilited word data', function (assert) {
        assertClueFormFields("#1 Across (5)", "", "", "");
    });
    test('Sets maxlength of word input field', function (assert) {
        assert.equal($("#clue-word").attr("maxlength"), "5");
    });
    test('Switching back to block edit mode clears hilite', function (assert) {
        $("#radio-1").prop("checked", true).change();
        assert.equal(getGridCells().filter(".xw-hilite").length, 0);
    });
    test('Throws error if word input does not fit grid', function (assert) {
        let word = "abcd ";
        let gridCells = getGridCells();
        let msgField = $("#clue-msg");
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must be 5 chars");
        word = "abcdef";
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must be 5 chars");
        for (let i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), "");
    });
    test('Throws error if word input does not contain alphabets', function (assert) {
        let word = "ab5cd";
        let gridCells = getGridCells();
        let msgField = $("#clue-msg");
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must contain all letters");
        word = "ab cd";
        doClueFormInput(word, "");
        assert.equal(msgField.text(), "Word must contain all letters");
        for (var i = 0; i < word.length; i++)
            assert.equal(readLetterInCell(gridCells[i]), "");
    });
    test('Trims, capitalizes and adds word input to grid if valid', function (assert) {
        let word ="trial";
        doClueFormInput(" "+word+" ", "");
        assert.equal($("#clue-msg").text(), "");
        assertHilitedWord(word);
    });
    test('Replaces existing chars in grid when updating word', function (assert) {
        let word = "chnge";
        doClueFormInput("trial", "");
        doClueFormInput(word, "");  // Update the word
        assert.equal($("#clue-msg").text(), "");
        assertHilitedWord(word);
    });
    test('Shows error message if no. in parenthesis in clue mismatches word length', function (assert) {
        let msg = "Incorrect number(s) in parentheses at end of clue";
        doClueFormInput("trial", "clue for trial (8)");
        assertHilitedWord("     ");
        assertClueFormFields("#1 Across (5)", "trial", "clue for trial (8)", msg);
        doClueFormInput("trial", "clue for trial (3,2,1)");
        assertClueFormFields("#1 Across (5)", "trial", "clue for trial (3,2,1)", msg);
        doClueFormInput("trial", "clue for trial (1,2-2,1)");
        assertClueFormFields("#1 Across (5)", "trial", "clue for trial (1,2-2,1)", msg);
    });
    test('Initializes clue form with saved word data after adding word length to clue', function (assert) {
        clickOnCell(0);   // Hilite 1 Down
        assertClueFormFields("#1 Down (5)", "", "", "");
        doClueFormInput("TRIAL", "clue 1 down (1,2,2)");
        assertHilitedWord("TRIAL");
        clickOnCell(0);   // Toggle Hilite to 1 Across
        doClueFormInput("TESTS", "clue 1 across");
        clickOnCell(0);   // Toggle back to 1 Down
        assertClueFormFields("#1 Down (5)", "TRIAL", "clue 1 down (1,2,2)", "");
        clickOnCell(6);
        doClueFormInput("RIVER", "clue 6 across (1-2,2)");
        clickOnCell(0);
        assertHilitedWord("TESTS");
        assertClueFormFields("#1 Across (5)", "TESTS", "clue 1 across (5)", "");
        clickOnCell(6);
        assertHilitedWord("RIVER");
        assertClueFormFields("#6 Across (5)", "RIVER", "clue 6 across (1-2,2)", "");
    });
    test("Shows error msg if word conflicts with existing letters", function(assert) {
        $("#radio-1").prop("checked", true).change();
        setBlocks([0,2,4]);
        $("#radio-2").prop("checked", true).change();
        clickOnCell(1);
        doClueFormInput("SNAKE", "clue 1 down");
        clickOnCell(3);
        doClueFormInput("TENET", "clue 2 down");
        clickOnCell(5);
        doClueFormInput("PAPER","");
        assertHilitedWord(" N E ");
        assertClueFormFields("#3 Across (5)", "PAPER", "", "Word conflicts with existing letters");
    });
    test("No tooltip set if clue text is empty", function(assert) {
        doClueFormInput("ACROS", "");
        assert.equal($(getGridCells()[0]).prop("title"), "");
    });
    test("Sets tooltip if clue text is not empty", function(assert) {
        doClueFormInput("acros", "clue text for 1a");
        assert.equal($(getGridCells()[0]).prop("title"), "1 Across: clue text for 1a (5)");
    });
    test("Replaces tooltip if clue text is changed", function(assert) {
        doClueFormInput("acros", "clue text for 1a");
        //clickOnCell(0);
        doClueFormInput("acros", "");
        assert.equal($(getGridCells()[0]).prop("title"), "");
        //clickOnCell(0);
        doClueFormInput("acros", "clue text");
        assert.equal($(getGridCells()[0]).prop("title"), "1 Across: clue text (5)");
    });
    test("Adds to ACROSS tooltip if DOWN clue text is added", function(assert) {
        doClueFormInput("acros", "clue for 1a");
        //clickOnCell(0);
        clickOnCell(0);
        doClueFormInput("adown", "clue for 1d");
        assert.equal($(getGridCells()[0]).prop("title"), "1 Across: clue for 1a (5)\n1 Down: clue for 1d (5)");
    });
    test("Keeps DOWN tooltip if blank ACROSS clue text is added", function(assert) {
        clickOnCell(0);
        doClueFormInput("adown", "clue for 1d");
        clickOnCell(0);
        doClueFormInput("acros", "");
        assert.equal($(getGridCells()[0]).prop("title"), "1 Down: clue for 1d (5)");
    });
    test("Does not add ACROSS tooltip to DOWN only clue", function(assert) {
        doClueFormInput("acros", "clue for 1a");
        clickOnCell(1);
        doClueFormInput("crown", "clue for 2d");
        let gridCells = getGridCells();
        assert.equal($(gridCells[0]).prop("title"), "1 Across: clue for 1a (5)");
        assert.equal($(gridCells[1]).prop("title"), "2 Down: clue for 2d (5)");
    });
    test("Sets word letters with no clue to class 'xw-red'", function(assert) {
        doClueFormInput("crown", "");  // 1 ACROSS
        let wordLetters = $(getGridCells()).filter(".xw-hilite").children(".xw-letter");
        assert.equal(wordLetters.length, 5);
        assert.true(wordLetters.hasClass("xw-red"));
        clickOnCell(1);
        doClueFormInput("river", "");  // 2 DOWN
        wordLetters = $(getGridCells()).filter(".xw-hilite").children(".xw-letter");
        assert.equal(wordLetters.length, 5);
        assert.true(wordLetters.hasClass("xw-red"));
    });
    test("Skips setting word letters with clue in single cells to red", function(assert) {
        $("#radio-1").prop("checked", true).change();
        setBlocks([5,7,9]);
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("WORDS", "Clue text");
        let wordLetters = $(getGridCells()).filter(".xw-hilite").children(".xw-letter");
        assert.false(wordLetters.even().hasClass("xw-red"));
        assert.true(wordLetters.odd().hasClass("xw-red"));
    });
    test("Updates word letter color when clue is set in single", function(assert) {
        $("#radio-1").prop("checked", true).change();
        setBlocks([5,7,9]);
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("WORDS", "");  // All Red
        doClueFormInput("WORDS", "clue added");
        let wordLetters = $(getGridCells()).filter(".xw-hilite").children(".xw-letter");
        assert.false(wordLetters.even().hasClass("xw-red"));
        assert.true(wordLetters.odd().hasClass("xw-red"));
    });
    test("Skips setting cross-letters to red if both cross-words have clues", function(assert) {
        $("#radio-1").prop("checked", true).change();
        setBlocks([5,7,9]);
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("WORDS", "Clue text");   // 1 ACROSS with clue
        clickOnCell(1);
        doClueFormInput("OVERT", "");  //  2 DOWN no clue
        clickOnCell(8);
        doClueFormInput("DIVER", "Clue text"); // DOWN word with clue
        clickOnCell(10);
        doClueFormInput("SERVE", "");   //ACROSS word with no clue
        clickOnCell(0);
        assertHasRedLetters([0,1,0,0,0]);
        clickOnCell(6);
        assertHasRedLetters([1,1,1,1,1]);
        clickOnCell(8);
        assertHasRedLetters([0,0,1,0,1]);
        clickOnCell(10);
        assertHasRedLetters([1,1,1,1,1]);
    });
    test('Sets dataSaved to true on successfully adding word/clue', function (assert) {
        saveData({});
        assert.true(controller.view.dataSaved);
        doClueFormInput("TOO", "Clue text");    // 1 ACROSS
        assert.true(controller.view.dataSaved);     // dataSaved is still true
        doClueFormInput("WORDS", "");               // Adds word successfully
        assert.false(controller.view.dataSaved);
    });

    //==> XWordEditor::Delete Clues
    QUnit.module("XWordEditor::Delete Clue", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            controller = new XWordEditor({id: null, size: 5});
            $("#radio-2").prop("checked", true).change();
        }
    });
    test("Deletes word data and letters in grid", function(assert) {
        $("#radio-1").prop("checked", true).change();
        setBlocks([1, 3]);
        $("#radio-2").prop("checked", true).change();
        doClueFormInput("ACROS", "");
        clickOnCell(0);
        doClueFormInput("ADOWN", "");
        clickOnCell(5);
        let clueDeleteBtn = $("#clue-delete");
        clueDeleteBtn.click();
        assertClueFormFields("#4 Across (5)", "", "", "");
        assertHilitedWord("     ");
        clickOnCell(0);
        clueDeleteBtn.click();
        assertClueFormFields("#1 Down (5)", "", "", "");
        assertHilitedWord("     ");
    });
    /**
    test("deleteWordData: Preserves ACROSS letters in grid shared by cross-words", function(assert) {
      var xword = createXWord(5);
      xword.setWordData("1-0", "ACROS", "", true);  // ACROSS WORD 1
      xword.setWordData("3-0", "WIDER", "", true);  // ACROSS WORD 2
      xword.setWordData("0-1", "ACRID", "", false); // DOWN WORD 1
      xword.setWordData("0-3", "COVER", "", false); // DOWN WORD 2
      xword.deleteWordData("1-0", true);
      assert.true(xword._getCellsInWord("1-0", true).children(".xw-letter:even").is(":empty"));
      assert.false(xword._getCellsInWord("1-0", true).children(".xw-letter:odd").is(":empty"));
    });
    test("deleteWordData: Preserves DOWN letters in grid shared by cross-words", function(assert) {
      var xword = createXWord(5);
      xword.setWordData("1-0", "ACROS", "", true);  // ACROSS WORD 1
      xword.setWordData("3-0", "WIDER", "", true);  // ACROSS WORD 2
      xword.setWordData("0-1", "ACRID", "", false); // DOWN WORD 1
      xword.setWordData("0-3", "COVER", "", false); // DOWN WORD 2
      xword.deleteWordData("0-1", false);
      assert.true(xword._getCellsInWord("0-1", false).children(".xw-letter:even").is(":empty"));
      assert.false(xword._getCellsInWord("0-1", false).children(".xw-letter:odd").is(":empty"));
    });
    test("deleteWordData: Deletes letter color classes", function(assert) {
      var xword = createXWord(5);
      xword.toggleCellBlock("1-0");
      xword.toggleCellBlock("1-2");
      xword.toggleCellBlock("1-4");
      xword.setWordData("0-0", "ACROS", "clue 1A", true);   // ACROSS WORD
      xword.setWordData("0-1", "COVER", "clue 2D", false);  // DOWN WORD 1
      xword.setWordData("0-3", "OVERT", "clue 3D", false);  // DOWN WORD 2
      xword.deleteWordData("0-0", true);
      var wordCells = xword._getCellsInWord("0-0", true).children(".xw-letter");
      assert.false(wordCells.hasClass("xw-blue"));
      assert.false(wordCells.hasClass("xw-xblue"));
    });
    test("deleteWordData: Deletes tooltip for the word if it exists", function(assert) {
      var xword = createXWord(5);
      xword.setWordData("0-0", "AVERT", "clue 1D", false);  // DOWN WORD 1
      xword.setWordData("0-0", "ACROS", "clue 1A", true);   // ACROSS WORD
      xword.deleteWordData("0-0", true);
      assert.equal($("#0-0").attr("title"), "1 Down: clue 1D (5)");
    });
    */

    //==> XWordEditor::Clues Status
    QUnit.module("XWordEditor::Clues Status", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
        }
    });
    test('Shows status of ACROSS & DOWN clues in status line for new grid', function (assert) {
        let puzzleData = {id: null, size: 7};
        new XWordEditor(puzzleData);
        assert.equal($("#status").text(), "ACROSS: 0 of 7, DOWN: 0 of 7");
    });
    test('Updates status of ACROSS & DOWN clues after adding blocks', function (assert) {
        let puzzleData = {id: null, size: 5};
        new XWordEditor(puzzleData);
        clickOnCell(3);
        clickOnCell(6);
        clickOnCell(11);
        assert.equal($("#status").text(), "ACROSS: 0 of 4, DOWN: 0 of 3");
    });
    test('Updates status of ACROSS & DOWN clues after adding clues', function (assert) {
        let puzzleData = {id: null, size: 5};
        new XWordEditor(puzzleData);
        setBlocks([1,3,11])
        $("#radio-2").prop("checked", true).change();
        clickOnCell(0);
        doClueFormInput("PEACH", "Clue 1d");
        clickOnCell(5);
        doClueFormInput("EAGER", "Clue 4a");
        clickOnCell(2);
        doClueFormInput("IGLOO", "Clue 2d");
        clickOnCell(4);
        doClueFormInput("ARDEN", "");
        clickOnCell(15);
        doClueFormInput("CHORE", "Clue 5a");
        assert.equal($("#status").text(), "ACROSS: 2 of 2, DOWN: 2 of 3");
    });
    test('Updates status of ACROSS & DOWN clues after deleting clues', function (assert) {
        let puzzleData = {id: null, size: 5};
        new XWordEditor(puzzleData);
        setBlocks([1,3,11])
        $("#radio-2").prop("checked", true).change();
        clickOnCell(0);
        doClueFormInput("PEACH", "Clue 1d");
        clickOnCell(5);
        doClueFormInput("EAGER", "Clue 4a");
        clickOnCell(4);
        doClueFormInput("ARDEN", "Clue 3d");
        clickOnCell(0);
        let clueDeleteBtn = $("#clue-delete");
        clueDeleteBtn.click();
        clickOnCell(5);
        clueDeleteBtn.click();
        assert.equal($("#status").text(), "ACROSS: 0 of 2, DOWN: 1 of 3");
    });

    //==> XWordEditor::Publish/Unpublish
    QUnit.module("XWordEditor::Publish/Unpublish", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            let gridData = {
                blocks:"0,1,23,24",
                across:{2: {word: "PUP", clue: "clue for 1a"}, 5: {word: "SIENA", clue: "clue for 4a"},
                    10: {word: "ADDUP", clue: "clue for 6a"}, 15: {word: "LLAMA", clue:"clue for 7a"},
                    20: {word: "EEL", clue: "clue for 8a"}},
                down:  {2: {word: "PEDAL", clue: "clue for 1d"}, 3: {word: "UNUM", clue: "clue for 2d"},
                    4: {word: "PAPA", clue: "clue for 3d"}, 5: {word: "SALE", clue: "clue for 4d"},
                    6: {word: "IDLE", clue: "clue for 5d"}}
            }
            puzzleData = {id: 10, size: 5, is_xword: true, desc: "Crosword", data: gridData};
            new XWordEditor(puzzleData);
        }
    });
    test('Enables Publish button and hides clue form when all clues are done', function (assert) {
        assert.equal($("#status").text(), "ACROSS: 5 of 5, DOWN: 5 of 5");
        assert.false($("#publish").prop("disabled"));
        assert.true($("#clue-form").is(":hidden"));
        assert.equal($(getGridCells()).filter(".xw-hilite").length, 0);
    });
    test('Displays confirmation box when publish btn is clicked', function (assert) {
        confirmResponse = false;     // Cancel confirmation box
        $("#publish").click();
        assert.true(confirmMessage.indexOf("Puzzle will be accessible to all users.") === 0);
        assert.true(confirmMessage.indexOf("Editing will be disabled. Please confirm.") > 0);
    });
    test('Hides Publish btn and shows Unpublish btn when publish is confirmed', function (assert) {
        confirmResponse = true;     // Cancel confirmation box
        let publishBtn = $("#publish");
        publishBtn.click();
        assert.true(publishBtn.is(":hidden"));
        assert.false($("#unpublish").is(":hidden"));
    });
    test('Disables editing and hides clueform when publish is confirmed', function (assert) {
        confirmResponse = true;     // Cancel confirmation box
        $("#publish").click();
        assert.true($("#clue-form").is(":hidden"));
        assert.true($("#navbar").is(":hidden"));
        clickOnCell(3);   // Hiliting should be disabled
        assert.equal($(getGridCells()).filter(".xw-hilite").length, 0);
    });
    test('Saves data after setting timestamp when publish is confirmed', function (assert) {
        confirmResponse = true;     // Cancel confirmation box
        ajaxSettings = null;
        $("#publish").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.deepEqual(ajaxData.data, puzzleData.data);
        assert.equal(ajaxData.id, puzzleData.id);
        assert.equal(ajaxData.size, puzzleData.size);
        assert.equal(ajaxData.desc, puzzleData.desc);
        assert.true(ajaxData.shared_at !== null);
    });
    test('Displays confirmation box when unpublish btn is clicked', function (assert) {
        confirmResponse = true;
        let publishBtn = $("#publish");
        let unpublishBtn = $("#unpublish");
        publishBtn.click();       // Publish first to show Unpublish button
        confirmResponse = false;
        unpublishBtn.click();
        assert.true(confirmMessage.indexOf("Puzzle will not be accessible to users.") === 0);
        assert.true(confirmMessage.indexOf("Editing will be re-enabled. Please confirm.") > 0);
        assert.true(publishBtn.is(":hidden"));     // Publish btn still hidden
        assert.false(unpublishBtn.is(":hidden"));   // Unpublish btn still shown
    });
    test('Shows Publish btn and hides Unpublish btn when unpublish is confirmed', function (assert) {
        confirmResponse = true;
        let publishBtn = $("#publish");
        let unpublishBtn = $("#unpublish");
        publishBtn.click();       // Publish first to show Unpublish button
        confirmResponse = true;
        unpublishBtn.click();
        assert.false(publishBtn.is(":hidden"));
        assert.true(unpublishBtn.is(":hidden"));
    });
    test('Re-enables editing and shows clueform when unpublish is confirmed', function (assert) {
        confirmResponse = true;
        $("#publish").click();       // Publish first to show Unpublish button
        confirmResponse = true;
        $("#unpublish").click();
        assert.false($("#navbar").is(":hidden"));
        let clueForm = $("#clue-form");
        assert.true(clueForm.is(":hidden"));
        clickOnCell(3);   // Hilite a word so clueform is visible
        assert.false(clueForm.is(":hidden"));
        assert.equal($(getGridCells()).filter(".xw-hilite").length, 3);
    });
    test('Saves data after deleting timestamp when unpublish is confirmed', function (assert) {
        confirmResponse = true;
        $("#publish").click();       // Publish first to show Unpublish button
        confirmResponse = true;
        $("#unpublish").click();
        let ajaxData = JSON.parse(ajaxSettings.data.data);
        assert.deepEqual(ajaxData.data, puzzleData.data);
        assert.equal(ajaxData.id, puzzleData.id);
        assert.equal(ajaxData.size, puzzleData.size);
        assert.equal(ajaxData.desc, puzzleData.desc);
        assert.true(ajaxData.shared_at === null);
    });

    //=> XWordEditor::Hiliting
    QUnit.module("XWordEditor::Hiliting", {
        beforeEach: function () {
            setupFixture(EditPuzzlePageHtml);
            puzzleData = {id: null, size: 5};
            new XWordEditor(puzzleData);
        }
    });
    test("Hilites ACROSS word first when a cell is clicked", function(assert) {
      setBlocks([0, 10]);
      $("#radio-2").prop("checked", true).change();
      assertHilitedCells(8, [5,6,7,8,9]);
      assertHilitedCells(12, [11,12,13]);
      assertHilitedCells(15, [15,16,17,18,19]);
      assertHilitedCells(23, [20,21,22,23]);
    });
    test("Hilites DOWN word if clicked cell is not part of ACROSS word", function(assert) {
      setBlocks([1, 2, 4, 11]);
      $("#radio-2").prop("checked", true).change();
      assertHilitedCells(0, [0,5,10,15]);
      assertHilitedCells(12, [7,12,17]);
      assertHilitedCells(14, [9,14,19,24]);
      assertHilitedCells(15, [15,16,17,18,19]);
      assertHilitedCells(21, [16,21]);
    });
    test("Toggles hilite from across to down if applicable when same cell is clicked", function(assert) {
      setBlocks([2, 6, 8]);
      $("#radio-2").prop("checked", true).change();
      assertHilitedCells(4, [3,4]);
      assertHilitedCells(4, [4,9,14,19,24]);
      assertHilitedCells(12, [10,11,12,13,14]);
      assertHilitedCells(12, [7,12,17]);
    });
    test("Does not change hilite if blocked cell is clicked", function(assert) {
      setBlocks([0, 4]);
      $("#radio-2").prop("checked", true).change();
      assertHilitedCells(5, [5,6,7,8,9]);
      assertHilitedCells(0, [5,6,7,8,9]);
    });
    test("Retains ACROSS or DOWN hilite if no DOWN or ACROSS alternative", function(assert) {
      setBlocks([1,11]);
      $("#radio-2").prop("checked", true).change();
      assertHilitedCells(6, [5,6,7,8,9]);     // ACROSS hilite
      assertHilitedCells(6, [5,6,7,8,9]);     // Re-click cell with no DOWN word (should retain ACROSS hilite)
      assertHilitedCells(0, [0,5,10,15,20]);  // DOWN hilite
      assertHilitedCells(0, [0,5,10,15,20]);  // Re-click cell with no ACROSS word (should retain DOWN hilite)
    });
    test('Hilites 1st ACROSS clue in an unblocked grid on switch to clue edit mode', function (assert) {
        new XWordEditor({id: null, size: 5});
        $("#radio-2").prop("checked", true).change();
        let hilitedCells = getGridCells().slice(0,5);
        assert.true($(hilitedCells).hasClass("xw-hilite"));
    });
    test("Hilites 1st ACROSS word in a new blocked grid on switch to clue edit mode", function(assert) {
        new XWordEditor({id: null, size: 5});
        setBlocks([0,2,4,5]);
        $("#radio-2").prop("checked", true).change();
        assertHilitedCells(null, [6,7,8,9]);
    });
    test("Hiliting a blank ACROSS & DOWN word initializes clue-form with clue ref", function(assert) {
        new XWordEditor({id: null, size: 5});
        setBlocks([0,2,4,5]);
        $("#radio-2").prop("checked", true).change();
        assertHilitedCells(15, [15,16,17,18]);
        assertClueFormFields("#7 Across (4)", "", "", "");
        assertHilitedCells(15, [10,15]);
        assertClueFormFields("#6 Down (2)", "", "", "");
    });
})();









