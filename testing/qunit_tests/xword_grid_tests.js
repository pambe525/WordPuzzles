

// HELPER FUNCTIONS
//------------------------------------------------------------------------------------------------------------------

QUnit.module('XWord Grid', {
  beforeEach: function () {
  },
});

// Constructor tests
//--------------------------------------------------------------------------------------------------------------------
test('Constructor uses default size (15) if not specified', function(assert) {
    let puzzle = new XWordGrid();
    assert.equal( puzzle.getPuzzleHtml().children("div").length, 225 );
});
test('Constructor creates grid of correct width & height', function(assert) {
  var gridSize=5, xword = new XWordGrid(gridSize);
  assert.equal(xword.getPuzzleHtml().width(), (xword.cellSize*gridSize + 1));
  assert.equal(xword.getPuzzleHtml().height(), (xword.cellSize*gridSize + 1))
});
test('BASE show: Grid cells have correct id and click handler', function(assert) {
  var size = 8, grid = createXWord(size), counter = 0;
  var cells = $(jqGridId).children('div');
  for (var row = 0; row < size; row++)
    for (var col = 0; col < size; col++ ) {
      assert.equal(cells[counter].id, row + "-" + col);
      assert.equal(typeof(cells[counter].click), 'function');
      counter++;
    }
});
test('BASE show: Grid cells have a span for letter', function(assert) {
  var size = 8, grid = createXWord(size), counter = 0;
  var letterSpans = $(jqGridId+" > div > .xw-letter");
  assert.equal($(letterSpans).length, size*size);
});
test('BASE show: Auto-numbers default blank grid', function(assert) {
  var size = 6;
  createXWord(size);
  var cells = $(jqGridId).children('div');
  for (var col = 0; col < size; col++)
    assert.equal($(cells[col]).text(), col + 1);
  for (var row = 1; row < size; row++)
    assert.equal($(cells[row * size]).text(), row + size);
  assert.equal($(".xw-number").length, 11);
});
test('BASE show: Auto-numbers grid with blocks added', function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  setBlocks(xword, ["0-0", "1-4", "2-3"]);
  assert.equal($(".xw-blocked").length, 6);
  assert.equal($(".xw-number").length, 8);
  assert.equal($(cells[1]).text(), 1);
  assert.equal($(cells[2]).text(), 2);
  assert.equal($(cells[3]).text(), 3);
  assert.equal($(cells[5]).text(), 4);
  assert.equal($(cells[14]).text(), 5);
  assert.equal($(cells[16]).text(), 6);
  assert.equal($(cells[18]).text(), 7);
  assert.equal($(cells[20]).text(), 8);
  assert.equal($(".xw-number").parent().length, 8);
});
test("BASE show: With puzzleData loads blocks into the grid", function(assert) {
  var puzzleData = {puzzle_id: 10, size: 5, data:{blocks:"0,4,20,24", across:{}, down:{}}};
  var xword = createXWord(puzzleData);
  var blockedCells = $(jqGridId + ">.xw-blocked");
  assert.equal(blockedCells.length, 4);
  assert.equal(blockedCells[0].id, "0-0");
  assert.equal(blockedCells[1].id, "0-4");
  assert.equal(blockedCells[2].id, "4-0");
  assert.equal(blockedCells[3].id, "4-4");
});
test("BASE show: With puzzleData loads words as data", function(assert) {
  var puzzleData = {
    puzzle_id: 10, size: 5, data:{blocks:"0,4,20,24", across:{"0-1":{word:"pin",clue:"clue for pin"},
    "1-0":{word:"trial", clue:""}}, down:{"0-1":{word:"prime", clue:"clue for prime"}}}
  };
  var xword = createXWord(puzzleData);
  assert.equal(Object.keys(xword.words.across).length, 2);
  assert.equal(Object.keys(xword.words.down).length, 1);
  assert.equal(xword.words.across["0-1"].word, "pin");
  assert.equal(xword.words.across["0-1"].clue, "clue for pin (3)");
  assert.equal(xword.words.down["0-1"].word, "prime");
  assert.equal(xword.words.down["0-1"].clue, "clue for prime (5)");
  assert.equal(xword.readWord("1-0", true), "TRIAL");
});

// setSharingOn tests
//--------------------------------------------------------------------------------------------------------------------
test('BASE setSharingOn: Sets current datetime string if true else null', function(assert) {
    var puzzle = new XWordGrid(5);
    puzzle.setSharingOn();
    assert.equal(puzzle.sharedAt, new Date().toISOString());
    puzzle.setSharingOn(false);
    assert.equal(puzzle.sharedAt, null);
});

// SAVE tests
//--------------------------------------------------------------------------------------------------------------------
test('BASE save: Success invokes saveSuccessHandler', function(assert) {
    var puzzle = new XWordGrid(5);
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({status:"OK"}); }  // mock save success
    puzzle.setSaveSuccessHandler(handler);
    puzzle.save();
    assert.true(handlerCalled);
    assert.equal(dataArg.status, "OK");
});
test('BASE save: Failure invokes saveFailureHandler', function(assert) {
    var puzzle = new XWordGrid(5);
    var handlerCalled = false;
    var handler = function(){ handlerCalled=true; };
    $.ajax = function(obj) { obj.error(); };  // mock save failure
    puzzle.setSaveFailureHandler(handler);
    puzzle.save();
    assert.true(handlerCalled);
});
test('BASE save: Success does nothing if saveSuccessHandler is not set', function(assert) {
    var puzzle = new XWordGrid(5);
    $.ajax = function(obj) { obj.success({puzzle_id:2}); };  // mock failure
    try {
        puzzle.save();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});
test('BASE save: Failure does nothing if saveFailureHandler is not set', function(assert) {
    var puzzle = new XWordGrid(5);
    $.ajax = function(obj) { obj.error(); };  // mock save failure
    try {
        puzzle.save();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});
test('BASE save: Invokes ajax call with correct parameters', function(assert) {
    var puzzle = new XWordGrid(5);
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    assert.equal(ajaxArg.method, "POST");
    assert.equal(ajaxArg.dataType, "json");
});
test('BASE save: Includes proper data parameters in ajax call', function(assert) {
    var puzzle = new XWordGrid(5);
    puzzle.id = 222;
    puzzle._getDataToSave = function(){ return {somedata:"blah"}; };
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    var ajaxDataObj = JSON.parse(ajaxArg.data['data']);
    assert.equal(ajaxDataObj['id'], 222);
    assert.equal(ajaxDataObj['size'], 5);
    assert.equal(ajaxDataObj['desc'], "");
    assert.equal(ajaxDataObj['is_xword'], true);
    assert.equal(ajaxDataObj['shared_at'], null);
    assert.deepEqual(ajaxDataObj['data'], {somedata:"blah"});
});
test('BASE save: Includes action parameter in ajax call', function(assert) {
    var puzzle = new XWordGrid(10);
    puzzle._getDataToSave = function(){ return {somedata:"blah"}; };
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    assert.equal(ajaxArg.data['action'], 'save');
});
test('BASE save: Updates puzzle_id', function(assert) {
    var puzzle = new XWordGrid(10);
    assert.equal(puzzle.id, null);   // Initial puzzle_id is null
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({id: 2}); }  // mock success
    puzzle.setSaveSuccessHandler(handler);
    puzzle.save();
    assert.equal(puzzle.id, 2);  // Update puzzle_id
});

// DELETE tests
//--------------------------------------------------------------------------------------------------------------------
test('BASE delete: Success invokes deleteSuccessHandler', function(assert) {
    var puzzle = new XWordGrid(5);
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({status:"OK"}); }  // mock success
    puzzle.setDeleteSuccessHandler(handler);
    puzzle.delete();
    assert.true(handlerCalled);
    assert.equal(dataArg.status, "OK");
});
test('BASE delete: Failure invokes deleteFailureHandler', function(assert) {
    var puzzle = new XWordGrid(6);
    var handlerCalled = false;
    var handler = function(){ handlerCalled=true; };
    $.ajax = function(obj) { obj.error(); };  // mock failure
    puzzle.setDeleteFailureHandler(handler);
    puzzle.delete();
    assert.true(handlerCalled);
});
test('BASE delete: Success does nothing if saveSuccessHandler is not set', function(assert) {
    var puzzle = new XWordGrid(7);
    $.ajax = function(obj) { obj.success(); };  // mock failure
    try {
        puzzle.delete();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});
test('BASE delete: Failure does nothing if saveFailureHandler is not set', function(assert) {
    var puzzle = new XWordGrid(7);
    $.ajax = function(obj) { obj.error(); };  // mock failure
    try {
        puzzle.delete();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});
test('BASE delete: Invokes ajax call with correct parameters', function(assert) {
    var puzzle = new XWordGrid(6);
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.equal(ajaxArg.method, "POST");
    assert.equal(ajaxArg.dataType, "json");
});
test('BASE delete: Includes puzzle_id in ajax call', function(assert) {
    var puzzle = new XWordGrid(5);
    puzzle.id = 10;
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.deepEqual(ajaxArg.data['id'], puzzle.id);
});
test('BASE delete: Includes action parameter in ajax call', function(assert) {
    var puzzle = new XWordGrid(4);
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.equal(ajaxArg.data['action'], 'delete');
});

// _dataChanged tests
//--------------------------------------------------------------------------------------------------------------------
test("_dataChanged: Called when cell is blocked or unblocked", function(assert) {
  var xword = createXWord(3);
  var called = false;
  xword.setDataChangedHandler(function(){ called = true; })
  xword.toggleCellBlock("1-1");
  assert.true(called);
});
test("_dataChanged: Called when word data is set", function(assert) {
  var xword = createXWord(5);
  var called = false;
  xword.setDataChangedHandler(function(){ called = true; })
  xword.setWordData("0-0","trial","clue text", true);
  assert.true(called);
});
test("_dataChanged: Called when word data is deleted", function(assert) {
  var xword = createXWord(5);
  var called = false;
  xword.setDataChangedHandler(function(){ called = true; })
  xword.setWordData("0-0","trial","clue text", true);
  called = false;
  xword.deleteWordData("0-0", true);
  assert.true(called);
});

// toggleCellBlock tests
//--------------------------------------------------------------------------------------------------------------------
test("toggleCellBlock: Returns false if cellId is not valid", function(assert) {
  var xword = createXWord(3);
  assert.false(xword.toggleCellBlock("0-3"));
});
test("toggleCellBlock: Blocks a cell and returns true", function(assert) {
  var xword = createXWord(4);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(jqGridId).children('div');
  assert.true($(cells[1]).hasClass('xw-blocked'));
});
test("toggleCellBlock: Automatically blocks symmetric cell", function(assert) {
  var xword = createXWord(4);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(jqGridId).children('div');
  assert.true($(cells[14]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 2);
});
test("toggleCellBlock: Unblocks cells if cells are already blocked", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  xword.toggleCellBlock("0-3");  //BLOCK
  xword.toggleCellBlock("0-3");  // UNBLOCK
  assert.false($(cells[3]).hasClass('xw-blocked'));
  assert.false($(cells[21]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});
test("toggleCellBlock: Blocks grid's center cell (no symmetric cell)", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  xword.toggleCellBlock("2-2");  // BLOCK
  assert.true($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 1);
  xword.toggleCellBlock("2-2");  // UNBLOCK
  assert.false($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});
test("toggleCellBlock: Does not block cell that contains a letter", function(assert) {
    var xword = createXWord(5);
    $("#0-0>.xw-letter").text("A");
    xword.toggleCellBlock("0-0");
    assert.false($("#0-0").hasClass('xw-blocked'));
});
test("toggleCellBlock: Clears existing blocked cell number", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  assert.equal($(cells[4]).text(), 5);
  assert.equal($(cells[20]).text(), 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(cells[4]).text(), "");
  assert.equal($(cells[20]).text(), "");
});
test("toggleCellBlock: Clears existing class names on numbered blocks", function(assert) {
  var xword = createXWord(5);
  assert.equal($(".xw-number").length, 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(".xw-number").length, 9);
});
test("toggleCellBlock: Does not unblock if a neighbor letter is in an in-line ACROSS word", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-4");
  xword.setWordData("1-0", "left", "", true);
  xword.toggleCellBlock("1-4");  // TRY TO UNBLOCK CELL
  assert.true($("#1-4").hasClass('xw-blocked'));
  xword.toggleCellBlock("3-0");  // TRY TO UNBLOCK SYMMETRIC CELL
  assert.true($("#3-0").hasClass('xw-blocked'));
});
test("toggleCellBlock: if a neighbor letter is in an in-line DOWN word", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-4");  // BLOCK CELL
  xword.setWordData("2-4", "dwn", "", false);
  xword.toggleCellBlock("1-4");  // TRY TO UNBLOCK CELL
  assert.true($("#1-4").hasClass('xw-blocked')); // CELL REMAINS BLOCKED
  xword.toggleCellBlock("3-0");  // TRY TO UNBLOCK SYMMETRIC CELL
  assert.true($("#3-0").hasClass('xw-blocked'));
});
test("toggleCellBlock: Unblocks cell if neighbor letter is not in in-line word", function(assert) {
  var xword = createXWord(4);
  xword.toggleCellBlock("0-1");  // BLOCK CELL
  xword.setWordData("0-0", "down", "", false);
  xword.toggleCellBlock("0-1");  // UNBLOCK CELL
  assert.false($("#0-1").hasClass('xw-blocked'));
});
test("toggleCellBlock: Does not block cell if symmetric cell has a letter", function(assert) {
  var xword = createXWord(4);
  xword.setWordData("0-0", "down", "", false);
  xword.toggleCellBlock("3-3");  // BLOCK SYMMETRIC CELL
  assert.false($("#0-0").hasClass('xw-blocked'));
});

// hasBlocks tests
//--------------------------------------------------------------------------------------------------------------------
test("hasBlock: Returns false when no blocks are present", function(assert) {
  var xword =   createXWord(6);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("0-0");
  xword.toggleCellBlock("0-0");
  assert.false(xword.hasBlocks());
});
test("hasBlock: Returns true when blocks are present", function(assert) {
  var xword = createXWord(5);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("2-2");
  assert.true(xword.hasBlocks());
});

// getClueNum tests
//--------------------------------------------------------------------------------------------------------------------
test("getClueNum: Returns 0 if given cell is blocked or out of bounds", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("3-2");
  assert.equal(xword.getClueNum("3-4"), 0);  // Symmetry cell
  assert.equal(xword.getClueNum("8-2"), 0);  // Outside grid
});
test("getClueNum: Returns 0 if cell is the only letter in word", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("1-1");
  assert.equal(xword.getClueNum("1-0"), 0);  // Across word - 1 letter
  assert.equal(xword.getClueNum("0-1", false), 0);  // Down word - 1 letter
});
test("getClueNum: Returns clue number on first cell of word", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.getClueNum("0-5"), 1);
  assert.equal(xword.getClueNum("5-0", false), 1);
});

// toggleWordHilite tests
//--------------------------------------------------------------------------------------------------------------------
test("toggleWordHilite: Hilites referenced ACROSS word and returns true", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "1-2", "2-4", "3-1"]);
  assert.true(xword.toggleWordHilite("0-2"));
  assertHilitedCells(assert, ["0-1","0-2","0-3","0-4","0-5","0-6"], true);
  assert.true(xword.toggleWordHilite("1-1"));
  assertHilitedCells(assert, ["1-0","1-1"], true);
  assert.true(xword.toggleWordHilite("1-3"));
  assertHilitedCells(assert, ["1-3","1-4","1-5","1-6"], true);
  assert.true(xword.toggleWordHilite("2-3"));
  assertHilitedCells(assert, ["2-0","2-1","2-2","2-3"], true);
  assert.true(xword.toggleWordHilite("3-3"));
  assertHilitedCells(assert, ["3-2","3-3","3-4"], true);
});
test("toggleWordHilite: Hilites referenced DOWN word and returns false", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-2", "2-4", "3-1"]);
  assert.false(xword.toggleWordHilite("0-1"));
  assertHilitedCells(assert, ["0-1","1-1","2-1"], false);
  assert.false(xword.toggleWordHilite("2-3"));
  assertHilitedCells(assert, ["0-3","1-3","2-3","3-3","4-3","5-3", "6-3"], false);
  assert.false(xword.toggleWordHilite("0-5"));
  assertHilitedCells(assert, ["0-5","1-5","2-5"], false);
});
test("toggleWordHilite: Clears previous hilites", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-0");
  xword.toggleWordHilite("0-1");
  xword.toggleWordHilite("1-1");
  assert.equal($(jqGridId + "> .xw-hilited").length, 7);
  assert.equal($(jqGridId + "> .xw-across").length, 7);
});
test("toggleWordHilite: Toggles from across to down if applicable", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-4", "3-1"]);
  assert.true(xword.toggleWordHilite("0-3"));
  assertHilitedCells(assert, ["0-3","0-4","0-5","0-6"], true);
  assert.false(xword.toggleWordHilite("0-3"));
  assertHilitedCells(assert, ["0-3","1-3","2-3","3-3","4-3","5-3","6-3"], false);
});
test("toggleWordHilite: Toggles from down to across if applicable", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-4", "3-1"]);
  assert.false(xword.toggleWordHilite("0-6"));
  assertHilitedCells(assert, ["0-6","1-6","2-6","3-6","4-6","5-6"], false);
  assert.true(xword.toggleWordHilite("0-6"));
  assertHilitedCells(assert, ["0-3","0-4","0-5","0-6"], true);
  assert.false(xword.toggleWordHilite("0-6"));
  assertHilitedCells(assert, ["0-6","1-6","2-6","3-6","4-6","5-6"], false);
});
test("toggleWordHilite: Return null if cell is blocked and does nothing", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-4", "3-1"]);
  assert.equal(xword.toggleWordHilite("1-2"), null);
  assert.equal($(".xw-hilited").length, 0);
});
test("toggleWordHilite: ACROSS hilite is retained if no DOWN word and returns true", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-0");
  assert.equal(xword.toggleWordHilite("0-0"), true);
  assert.equal(xword.toggleWordHilite("0-0"), true);
  assertHilitedCells(assert, ["0-0","0-1","0-2","0-3","0-4"], true);
});
test("toggleWordHilite: DOWN hilite is retained if no ACROSS word and returns false", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("0-1");
  assert.equal(xword.toggleWordHilite("0-0"), false);
  assert.equal(xword.toggleWordHilite("0-0"), false);
  assertHilitedCells(assert, ["0-0","1-0","2-0","3-0","4-0"], false);
});

// Hilites tests
//--------------------------------------------------------------------------------------------------------------------
test("clearHilites: Clears all hilites", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-0");
  xword.toggleWordHilite("0-1");
  xword.clearHilites();
  assert.equal($(jqGridId + "> .xw-hilited").length, 0);
});
test("getFirstHilitedCellId: Returns null if no hilited cells", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.getFirstHilitedCellId(), null);
});
test("getFirstHilitedCellId: Returns first cell id of hilited cells", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("1-1");
  xword.toggleWordHilite("1-4");
  assert.equal(xword.getFirstHilitedCellId(), "1-2");
});
test("isHiliteAcross: Returns null if no hilited cells", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.isHiliteAcross(), null);
});
test("isHiliteAcross: Returns true if hilited is across", function(assert) {
  var xword = createXWord(7);
  xword.toggleWordHilite("0-0");
  assert.true(xword.isHiliteAcross());
});
test("hiliteNextIncomplete: Hilites 1 Across on new grid", function(assert) {
  var xword = createXWord(7);
  xword.hiliteNextIncomplete();
  assert.equal(xword.getFirstHilitedCellId(), "0-0")
  assert.true(xword.isHiliteAcross());
});
test("hiliteNextIncomplete: The first across incomplete word is hilited", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("0-0", "first", "clue text (5)");
  xword.hiliteNextIncomplete(true);
  assert.equal(xword.getFirstHilitedCellId(), "1-0")
  assert.true(xword.isHiliteAcross());
});
test("hiliteNextIncomplete: The next incomplete word is hilited", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("2-0", "first", "clue text (5)");
  xword.toggleWordHilite("1-0");
  assert.true(xword.isHiliteAcross());
  xword.hiliteNextIncomplete(true);
  assert.equal(xword.getFirstHilitedCellId(), "3-0")
  assert.true(xword.isHiliteAcross());
});
test("hiliteNextIncomplete: If no incomplete Across words finds first down word", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("0-0", "itema", "clue text 1 (5)");
  xword.setWordData("1-0", "itemb", "clue text 2 (5)");
  xword.setWordData("2-0", "itemc", "clue text 3 (5)");
  xword.setWordData("3-0", "itemd", "clue text 4 (5)");
  xword.setWordData("4-0", "iteme", "clue text 5 (5)");
  xword.toggleWordHilite("0-0");
  xword.hiliteNextIncomplete();
  assert.equal(xword.getFirstHilitedCellId(), "0-0");
  assert.false(xword.isHiliteAcross());
});

// setEditable tests
//--------------------------------------------------------------------------------------------------------------------
test("setEditable: TRUE Makes all cells editable", function(assert) {
  var xword = createXWord(7);
  xword.setEditable(true);
  assert.equal($(jqGridId + "> div").attr("contenteditable"), "true");
});
test("setEditable: FALSE Makes all cells uneditable", function(assert) {
  var xword = createXWord(7);
  xword.setEditable(false);
  assert.equal($(jqGridId + "> div").attr("contenteditable"),"false");
});

// readWord tests
//--------------------------------------------------------------------------------------------------------------------
test("readWord: Returns null if current cell is blocked", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-0");
  assert.equal(xword.readWord("0-0", true), null);
});
test("readWord: Returns null if ACROSS or DOWN word does not exist", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  assert.equal(xword.readWord("0-0", true), null);
});
test("readWord: Returns word in grid containing given cell", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.readWord("0-0", true), "       ");
  xword.setWordData("0-0", "testing", "clue", true);
  assert.equal(xword.readWord("0-0", true), "TESTING");
});

// getWordData tests
//--------------------------------------------------------------------------------------------------------------------
test("getWordData: Returns null if cellId is blocked or not in grid", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  assert.equal(xword.getWordData("0-1", true), null);
  assert.equal(xword.getWordData("0-7", true), null);
});
test("getWordData: Returns null if word does not exist", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  assert.equal(xword.getWordData("0-1", true), null);
  assert.equal(xword.getWordData("1-1", true), null);
});
test("getWordData: Returns ACROSS word data if word is set", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");  // Block 2nd cell in first row
  var acrossWordData = {word:"fiver",clue:"some text"};
  xword.words["across"]["0-2"] = acrossWordData;
  assert.equal(xword.getWordData("0-0", true), null);  // No across word
  var wordData = xword.getWordData("0-5", true);  // Should return data for across word starting at 0-2
  assert.equal(wordData.word, acrossWordData.word);
  assert.equal(wordData.clue, acrossWordData.clue);
});
test("getWordData: Returns DOWN word data if word is set", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");  // Block 2nd cell in first row
  var downWordData = {word:"fiver",clue:"some text"};
  xword.words["down"]["0-0"] = downWordData;
  var wordData = xword.getWordData("3-0", false);  // Should return data for down starting at 0-0
  assert.equal(wordData.word, downWordData.word);
  assert.equal(wordData.clue, downWordData.clue);
});

// setWordData tests
//--------------------------------------------------------------------------------------------------------------------
test("setWordData: Throws error if cellId is blocked or not in grid", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-3");
  assert.throws(function(){ xword.setWordData("0-3","Text","") }, /Invalid cell id/, Error);
  assert.throws(function(){ xword.setWordData("0-7","Text","") }, /Invalid cell id/, Error);
});
test("setWordData: Throws error if cellId is not in word (across or down)", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("1-2");
  assert.throws(function(){ xword.setWordData("0-0","Text","", true) }, /Invalid cell id/, Error);
  assert.throws(function(){ xword.setWordData("0-2","Text","", false) }, /Invalid cell id/, Error);
});
test("setWordData: Throws error if across or down word does not fit", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("0-6");
  assert.throws(function(){ xword.setWordData("0-5","tex","", true) }, /Word must be 4 chars/, Error);
  assert.throws(function(){ xword.setWordData("1-2","text","", true) }, /Word must be 7 chars/, Error);
  assert.throws(function(){ xword.setWordData("1-2","longword","", true) }, /Word must be 7 chars/, Error);
  assert.throws(function(){ xword.setWordData("0-0","longword","", false) }, /Word must be 6 chars/, Error);
});
test("setWordData: Throws error if word does not contain alphabets", function(assert) {
  var xword = createXWord(7);
  assert.throws(function(){ xword.setWordData("0-0","","", true) }, /Word must contain all letters/, Error);
  assert.throws(function(){ xword.setWordData("0-0","a1de5gh","", true) }, /Word must contain all letters/, Error);
  assert.throws(function(){ xword.setWordData("0-0","ab e gh","", true) }, /Word must contain all letters/, Error);
});
test("setWordData: Stores the word and clue as across or down in json obj", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("0-6");
  xword.setWordData("0-4", "word", "clue1 (4)", true);
  xword.setWordData("1-0", "downey", "clue2 (6)", false);
  assert.deepEqual(xword.words["across"]["0-2"], {word:"word", clue:"clue1 (4)"});
  assert.deepEqual(xword.words["down"]["0-0"], {word:"downey", clue:"clue2 (6)"});
});
test("setWordData: Sets word letters in grid", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("0-6");
  xword.setWordData("0-4", "word", "clue1", true);
  xword.setWordData("1-0", "downey", "clue2", false);
  assert.equal(xword.readWord("0-3", true), "WORD");
  assert.equal(xword.readWord("0-0", false), "DOWNEY");
});
test("setWordData: Updates existing word letters in grid", function(assert) {
  var xword = createXWord(7);
  xword.setWordData("0-3", "current", "oldclue", true);
  assert.equal(xword.readWord("0-3", true), "CURRENT");
  assert.deepEqual(xword.words["across"]["0-0"], {word:"current", clue:"oldclue (7)"});
  assert.equal(xword.getClueNum("0-0", true), 1);  // Cell number should not be overwritten
  xword.setWordData("0-3", "replace", "newclue", true);
  assert.equal(xword.readWord("0-3", true), "REPLACE");
  assert.deepEqual(xword.words["across"]["0-0"], {word:"replace", clue:"newclue (7)"});
  assert.equal(xword.getClueNum("0-0", true), 1);
});
test("setWordData: Throws error if word conflicts with existing letters", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("0-0");
  xword.toggleCellBlock("0-2");
  xword.toggleCellBlock("2-2");
  xword.setWordData("0-1", "snake", "clue1", false);
  xword.setWordData("0-3", "tenet", "clue2", false);
  assert.throws(function(){xword.setWordData("1-0","paper","", true)}, /Word conflicts with existing letters/, Error);
  xword.setWordData("3-0", "skyer", "clue3", true);
});
test("setWordData: Throws error if word length mismatch nos. in parenthesis at end of clue", function(assert) {
  var xword = createXWord(7);
  assert.throws(function(){xword.setWordData("3-2", "letters", "clue 1 (6)", true)},
      /Incorrect number\(s\) in parentheses at end of clue/, Error);
  assert.throws(function(){xword.setWordData("3-2", "letters", "clue 1 (2,3,1)", true)},
      /Incorrect number\(s\) in parentheses at end of clue/, Error);
  assert.throws(function(){xword.setWordData("3-2", "letters", "clue 1 (6-2)", true)},
      /Incorrect number\(s\) in parentheses at end of clue/, Error);
});
test("setWordData: Checks match between word length and number is parentheses in clue", function(assert) {
  var xword = createXWord(7);
  xword.setWordData("3-2", "letters", "clue 1 (7)", true);
  assert.equal(xword.getWordData("3-2", true).clue, "clue 1 (7)");
  xword.setWordData("3-2", "letters", "clue 1 (2,4,1)", true);
  assert.equal(xword.getWordData("3-2", true).clue, "clue 1 (2,4,1)");
  xword.setWordData("3-2", "letters", "clue 1 (2-2,1-1,1)", true);
  assert.equal(xword.getWordData("3-2", true).clue, "clue 1 (2-2,1-1,1)");
});
test("setWordData: No tooltip set if clue text is empty", function(assert) {
  var xword = createXWord(7);
  xword.setWordData("3-2", "letters", "", true);
  assert.equal($("#3-0").prop("title"), "");
});
test("setWordData: Sets tooltip if clue text is not empty", function(assert) {
  var xword = createXWord(7);
  xword.setWordData("3-2", "letters", "Clue text (7)", true);
  assert.equal($("#3-0").prop("title"), "10 Across: Clue text (7)\n");
});
test("setWordData: Replaces tooltip if clue text is changed", function(assert) {
  var xword = createXWord(7);
  xword.setWordData("3-2", "letters", "Clue text (7)", true);
  xword.setWordData("3-2", "letters", "", true);
  assert.equal($("#3-0").prop("title"), "");
});
test("setWordData: Adds to ACROSS tooltip if DOWN clue text is added", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "across", "Clue text1 (6)", true);
  xword.setWordData("0-0", "adowns", "Clue text2 (6)", false);
  assert.equal($("#0-0").prop("title"), "1 Across: Clue text1 (6)\n1 Down: Clue text2 (6)");
});
test("setWordData: Keeps DOWN tooltip if blank ACROSS clue text is added", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "adowns", "Clue text2 (6)", false);
  xword.setWordData("0-0", "across", "", true);
  assert.equal($("#0-0").prop("title"), "1 Down: Clue text2 (6)");
});
test("setWordData: Does not add ACROSS tooltip to DOWN only clue", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "across", "Clue text1 (6)", true);
  xword.setWordData("0-1", "crossd", "Clue text2 (6)", false);
  assert.equal($("#0-1").prop("title"), "2 Down: Clue text2 (6)");
});
test("setWordData: Adds no. of letters parentheses in clue text if missing", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "across", "Clue text2", false);
  assert.equal(xword.getWordData("0-0", false).clue, "Clue text2 (6)");
});
test("setWordData: By default word letters are red without clue", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "across", "", true);
  var wordLetters = $(xword._getCellsInWord("0-0").children(".xw-letter"));
  assert.equal(wordLetters.css("color"), "rgb(255, 0, 0)");
});
test("setWordData: With clue set, word letters in single cells are blue", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-0");
  xword.toggleCellBlock("1-2");
  xword.toggleCellBlock("1-4");
  xword.setWordData("0-0", "WORDS", "Clue text", true);
  var wordLetters = $(xword._getCellsInWord("0-0").children(".xw-letter"));
  assert.equal(wordLetters.even().css("color"), "rgb(0, 0, 255)");
  assert.equal(wordLetters.odd().css("color"), "rgb(255, 0, 0)");
});
test("setWordData: Letters in cross-cells are blue only if both words have clues", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-0");
  xword.toggleCellBlock("1-2");
  xword.toggleCellBlock("1-4");
  xword.setWordData("0-0", "WORDS", "Clue text", true);
  xword.setWordData("0-1", "OVERT", "", false);  // DOWN word but no clue
  xword.setWordData("0-3", "DIVER", "Clue text", false); // DOWN word with clue
  xword.setWordData("2-0", "SERVE", "", true);     //ACROSS word with no clue
  var wordLetters = $(xword._getCellsInWord("0-0").children(".xw-letter"));
  assert.equal($(wordLetters[0]).css("color"), "rgb(0, 0, 255)");
  assert.equal($(wordLetters[1]).css("color"), "rgb(255, 0, 0)");
  assert.equal($(wordLetters[2]).css("color"), "rgb(0, 0, 255)");
  assert.equal($(wordLetters[3]).css("color"), "rgb(0, 0, 255)");
  assert.equal($(wordLetters[4]).css("color"), "rgb(0, 0, 255)");
  wordLetters = $(xword._getCellsInWord("2-0").children(".xw-letter"));
  assert.equal(wordLetters.css("color"), "rgb(255, 0, 0)");
});

// hasData tests
//--------------------------------------------------------------------------------------------------------------------
test("hasData: returns false if no data in grid", function(assert) {
  var xword = createXWord(6);
  assert.false(xword.hasData());
});
test("hasData: returns true if grid has blocks", function(assert) {
  var xword = createXWord(6);
  xword.toggleCellBlock("0-0");
  assert.true(xword.hasData());
});
test("hasData: returns true if grid has word data", function(assert) {
  var xword = createXWord(6);
  xword.setWordData("0-0", "ACROSS", "", true);
  assert.true(xword.hasData());
});

// deleteWordData tests
//--------------------------------------------------------------------------------------------------------------------
test("deleteWordData: Returns false if cellId is blocked or out of range", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("1-0");
  assert.false(xword.deleteWordData("1-0"));
  assert.false(xword.deleteWordData("0-5"));
});
test("deleteWordData: Returns false if referenced word does not exist", function(assert) {
  var xword = createXWord(5);
  assert.false(xword.deleteWordData("0-0"));
});
test("deleteWordData: Deletes word data of existing word and returns true ", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("0-0", "ACROS", "", true);  // ACROSS WORD
  xword.setWordData("0-0", "ADOWN", "", false); // DOWN WORD
  assert.true(xword.deleteWordData("0-0", true));
  assert.equal(xword.getWordData("0-0", true), null)
  assert.true(xword.deleteWordData("0-0", false));
  assert.equal(xword.getWordData("0-0", false), null);
});
test("deleteWordData: Deletes existing word in grid", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("0-0")
  xword.setWordData("0-1", "CROS", "", true);  // ACROSS WORD
  xword.setWordData("1-0", "DOWN", "", false); // DOWN WORD
  xword.deleteWordData("0-1", true);
  assert.true(xword._getCellsInWord("0-1", true).children(".xw-letter").is(":empty"));
  xword.deleteWordData("1-0", false);
  assert.true(xword._getCellsInWord("1-0", false).children(".xw-letter").is(":empty"));
});
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

// _getDataToSave tests
//--------------------------------------------------------------------------------------------------------------------
test("_getDataToSave: Returns grid data for an empty grid as JSON obj", function(assert) {
  var xword = createXWord(5);
  var gridDataObj = xword._getDataToSave();
  assert.equal(gridDataObj.blocks, "");
  assert.deepEqual(gridDataObj.across, {});
  assert.deepEqual(gridDataObj.down, {});
});
test("_getDataToSave: Returns grid data for blocks", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("1-1");
  xword.toggleCellBlock("1-4");
  xword.toggleCellBlock("2-2");
  var gridDataObj = xword._getDataToSave();
  assert.equal(gridDataObj.blocks, "1,6,9,12,15,18,23");
});
test("_getDataToSave: Returns grid data for words", function(assert) {
  var xword = createXWord(5);
  xword.toggleCellBlock("0-1");
  xword.toggleCellBlock("1-4");
  xword.toggleCellBlock("2-2");
  xword.setWordData("0-2","NET","clue 2a");
  xword.setWordData("1-1","DOWN","clue 4d", false);
  xword.setWordData("4-0","ONE", "");
  var gridDataObj = xword._getDataToSave();
  assert.equal(gridDataObj.blocks, "1,9,12,15,23");
  var expected = {across:{"0-2":{word:"NET",clue:"clue 2a (3)"},"4-0":{word:"ONE",clue:""}},
                  down:{"1-1":{word:"DOWN", clue:"clue 4d (4)"}}};
  assert.deepEqual(gridDataObj.across, expected.across);
  assert.deepEqual(gridDataObj.down, expected.down);
});

// isReady tests
//--------------------------------------------------------------------------------------------------------------------
test("isReady: Returns false when grid is incomplete", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("0-0","ABCDE", "clue 1a");
  xword.setWordData("1-0","FGHIJ", "clue 6a");
  xword.setWordData("2-0","KLMNO", "clue 7a");
  xword.setWordData("3-0","PQRST", "clue 8a");
  xword.setWordData("4-0","UVWXY", "clue 9a");
  assert.equal(xword.isReady(), false);
});
test("isReady: Returns true when grid with no blocks is complete", function(assert) {
  var xword = createXWord(5);
  xword.setWordData("0-0","ABCDE", "clue 1a");
  xword.setWordData("1-0","FGHIJ", "clue 6a");
  xword.setWordData("2-0","KLMNO", "clue 7a");
  xword.setWordData("3-0","PQRST", "clue 8a");
  xword.setWordData("4-0","UVWXY", "clue 9a");
  xword.setWordData("0-0", "AFKPU", "clue 1d", false);
  xword.setWordData("0-1", "BGLQV", "clue 2d", false);
  xword.setWordData("0-2", "CHMRW", "clue 3d", false);
  xword.setWordData("0-3", "DINSX", "clue 4d", false);
  xword.setWordData("0-4", "EJOTY", "clue 5d", false);
  assert.equal(xword.isReady(), true);
});
test("isReady: Returns true when grid with blocks is complete", function(assert) {
  var xword = createXWord(3);
  xword.toggleCellBlock("1-1");
  xword.setWordData("0-0","tin", "clue 1a");
  xword.setWordData("2-0","ton", "clue 3a");
  xword.setWordData("0-0","tot", "clue 1d", false);
  xword.setWordData("0-2","non", "clue 2d", false);
  assert.equal(xword.isReady(), true);
});

// setShared tests
//--------------------------------------------------------------------------------------------------------------------
test("setShared: When true sets sharedAt attribute to current time stamp", function(assert) {
  var xword = createXWord(3);
  xword.setShared(true);
  assert.equal(xword.sharedAt, new Date().toUTCString());
  xword.setShared(false);
  assert.equal(xword.sharedAt, null);
});

