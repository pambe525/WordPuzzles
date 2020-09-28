/*
  Tests for Class Crossword
  */
var gridId = "xw-grid", jqGridId = "#"+gridId;

QUnit.module('Crossword', {
  beforeEach: function () {
    $("#qunit-fixture").append($(document.createElement('div')).attr('id',gridId));
  },
});

QUnit.test('constructor: Throws errors if arguments are not valid', function(assert) {
  assert.throws(function(){ new Crossword(2, function(){}, '1') }, /gridSize must be a number/, Error);
  assert.throws(function(){ new Crossword('bad-id', function(){}, 1) }, /divId does not exist/, Error);
  assert.throws(function(){ new Crossword('xw-grid', "func", 2) }, /clickHandler must be a function/, Error);
});

QUnit.test('constructor: Creates grid of correct width, height & border', function(assert) {
  var gridSize=5, grid = createXWord(gridSize);
  assert.equal($(jqGridId).width(), (grid.cellSize*gridSize + 1));
  assert.equal($(jqGridId).height(), (grid.cellSize*gridSize + 1))
});

QUnit.test('constructor: Creates grid of (gridSize x gridSize) div cells', function(assert) {
  createXWord(10);
  assert.equal($(jqGridId).children('div').length, 100);
  assert.equal($(jqGridId).css("border-top-width"),"1px");
});

QUnit.test('constructor: Clears current grid area before adding grid', function(assert) {
  createXWord(10);
  assert.equal($(jqGridId).children('div').length, 100);
  createXWord(5);
  assert.equal($(jqGridId).children('div').length, 25);
});

QUnit.test("constructor: Each grid cell has correct styling", function(assert) {
  var grid = createXWord(4);
  assert.equal($(jqGridId + " > div").css("float"), "left");
  assert.equal($(jqGridId + " > div").width(), 30);
  assert.equal($(jqGridId + " > div").height(), 30);
  assert.equal($(jqGridId + " > div").css("border-right-width"), "1px");});

QUnit.test('constructor: Each grid cell has correct id and click handler', function(assert) {
  var size = 8, grid = createXWord(size), counter = 0;
  var cells = $(jqGridId).children('div');
  for (var row = 0; row < size; row++)
    for (var col = 0; col < size; col++ ) {
      assert.equal(cells[counter].id, row + "-" + col);
      assert.equal(typeof(cells[counter].click), 'function');
      counter++;
    }
});

QUnit.test('constructor: Check cell number styling', function(assert) {
  createXWord(2);
  assert.equal($(jqGridId + " > div > .xw-number").css("font-size"), "9px");
  assert.equal($(jqGridId + " > div > .xw-number").position().left, 1);
  assert.equal($(jqGridId + " > div > .xw-number").position().top, -2);
});

QUnit.test("toggleCellBlock: Returns false if cellId is not valid", function(assert) {
  var xword = createXWord(3);
  assert.false(xword.toggleCellBlock("0-3"));
});

QUnit.test("toggleCellBlock: Blocks a cell and returns true", function(assert) {
  var xword = createXWord(4);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(jqGridId).children('div');
  assert.true($(cells[1]).hasClass('xw-blocked'));
});

QUnit.test("toggleCellBlock: Also automatically blocks symmetric cell", function(assert) {
  var xword = createXWord(4);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(jqGridId).children('div');
  assert.true($(cells[14]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 2);
});

QUnit.test("toggleCellBlock: Unblocks cells if cells are already blocked", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  xword.toggleCellBlock("0-3");  //BLOCK
  xword.toggleCellBlock("0-3");  // UNBLOCK
  assert.false($(cells[3]).hasClass('xw-blocked'));
  assert.false($(cells[21]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});

QUnit.test("toggleCellBlock: Blocks center cell (no symmetric cell)", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  xword.toggleCellBlock("2-2");  // BLOCK
  assert.true($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 1);
  xword.toggleCellBlock("2-2");  // UNBLOCK
  assert.false($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});

QUnit.test("toggleCellBlock: Does not block cell that contains a letter", function(assert) {
    var xword = createXWord(5);
    $("#0-0").append("A").addClass("xw-letter");
    xword.toggleCellBlock("0-0");
    assert.false($("#0-0").hasClass('xw-blocked'));
});

QUnit.test("toggleCellBlock: Clears existing blocked cell number", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  assert.equal($(cells[4]).text(), 5);
  assert.equal($(cells[20]).text(), 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(cells[4]).text(), "");
  assert.equal($(cells[20]).text(), "");
});

QUnit.test("toggleCellBlock: Clears existing class names on numbered blocks", function(assert) {
  var xword = createXWord(5);
  var cells = $(jqGridId).children('div');
  assert.equal($(".xw-number").length, 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(".xw-number").length, 9);
});

QUnit.test('constructor: Auto-number default blank grid', function(assert) {
  var size = 6;
  createXWord(size);
  var cells = $(jqGridId).children('div');
  for (var col = 0; col < size; col++)
    assert.equal($(cells[col]).text(), col + 1);
  for (var row = 1; row < size; row++)
    assert.equal($(cells[row * size]).text(), row + size);
  assert.equal($(".xw-number").length, 11);
});

QUnit.test('constructor: Auto-numbers blocked grid', function(assert) {
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

QUnit.test("hasBlock: Returns false when no blocks are present", function(assert) {
  var xword =   createXWord(6);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("0-0");
  xword.toggleCellBlock("0-0");
  assert.false(xword.hasBlocks());
});

QUnit.test("hasBlock: Returns true when blocks are present", function(assert) {
  var xword = createXWord(5);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("2-2");
  assert.true(xword.hasBlocks());
});

QUnit.test("getWordLength: Returns 0 if given cell is blocked or out of bounds", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("3-2");
  assert.equal(xword.getWordLength("3-4"), 0);  // Symmetry cell
  assert.equal(xword.getWordLength("8-2"), 0);  // Outside grid
});

QUnit.test("getWordLength: ACROSS returns full length of grid with no blocks", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.getWordLength("0-0"), 7);
});

QUnit.test("getWordLength: ACROSS returns length between blocks", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["1-6","3-1"]);
  assert.equal(xword.getWordLength("1-1"), 6);
  assert.equal(xword.getWordLength("5-1"), 6);
  assert.equal(xword.getWordLength("3-3"), 3);
  assert.equal(xword.getWordLength("3-0"), 1);
});

QUnit.test("getWordLength: DOWN returns full length of grid with no blocks", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.getWordLength("3-0", false), 7);
});

QUnit.test("getWordLength: DOWN returns length between blocks", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("1-6");
  xword.toggleCellBlock("1-3");
  assert.equal(xword.getWordLength("0-0", false), 5);
  assert.equal(xword.getWordLength("5-6", false), 5);
  assert.equal(xword.getWordLength("3-3", false), 3);
  assert.equal(xword.getWordLength("0-3", false), 1);
});

QUnit.test("getClueNum: Returns 0 if given cell is blocked or out of bounds", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("3-2");
  assert.equal(xword.getClueNum("3-4"), 0);  // Symmetry cell
  assert.equal(xword.getClueNum("8-2"), 0);  // Outside grid
});

QUnit.test("getClueNum: Returns 0 if cell is the only letter in word", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("1-1");
  assert.equal(xword.getClueNum("1-0"), 0);  // Across word - 1 letter
  assert.equal(xword.getClueNum("0-1", false), 0);  // Down word - 1 letter
});

QUnit.test("getClueNum: Returns clue number on first cell of word", function(assert) {
  var xword = createXWord(7);
  assert.equal(xword.getClueNum("0-5"), 1);
  assert.equal(xword.getClueNum("5-0", false), 1);
});

QUnit.test("toggleWordHilite: Hilites referenced ACROSS words", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "1-2", "2-4", "3-1"]);
  xword.toggleWordHilite("0-2");
  assertHilitedCells(assert, ["0-1","0-2","0-3","0-4","0-5","0-6"], true);
  xword.toggleWordHilite("1-1");
  assertHilitedCells(assert, ["1-0","1-1"], true);
  xword.toggleWordHilite("1-3");
  assertHilitedCells(assert, ["1-3","1-4","1-5","1-6"], true);
  xword.toggleWordHilite("2-3");
  assertHilitedCells(assert, ["2-0","2-1","2-2","2-3"], true);
  xword.toggleWordHilite("3-3");
  assertHilitedCells(assert, ["3-2","3-3","3-4"], true);
});

QUnit.test("toggleWordHilite: Hilites referenced DOWN words", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-2", "2-4", "3-1"]);
  xword.toggleWordHilite("0-1");
  assertHilitedCells(assert, ["0-1","1-1","2-1"], false);
  xword.toggleWordHilite("2-3");
  assertHilitedCells(assert, ["0-3","1-3","2-3","3-3","4-3","5-3", "6-3"], false);
  xword.toggleWordHilite("0-5");
  assertHilitedCells(assert, ["0-5","1-5","2-5"], false);
});

QUnit.test("toggleWordHilite: Clears previous hilites", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-0");
  xword.toggleWordHilite("0-1");
  xword.toggleWordHilite("1-1");
  assert.equal($(jqGridId + "> .xw-hilited").length, 7);
  assert.equal($(jqGridId + "> .xw-across").length, 7);
});

QUnit.test("toggleWordHilite: Toggles from across to down if applicable", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-4", "3-1"]);
  xword.toggleWordHilite("0-3");
  assertHilitedCells(assert, ["0-3","0-4","0-5","0-6"], true);
  xword.toggleWordHilite("0-3");
  assertHilitedCells(assert, ["0-3","1-3","2-3","3-3","4-3","5-3","6-3"], false);
});

QUnit.test("toggleWordHilite: Toggles from down to across if applicable", function(assert) {
  var xword = createXWord(7);
  setBlocks(xword, ["0-0", "0-2", "1-2", "2-4", "3-1"]);
  xword.toggleWordHilite("0-6");
  assertHilitedCells(assert, ["0-6","1-6","2-6","3-6","4-6","5-6"], false);
  xword.toggleWordHilite("0-6");
  assertHilitedCells(assert, ["0-3","0-4","0-5","0-6"], true);
  xword.toggleWordHilite("0-6");
  assertHilitedCells(assert, ["0-6","1-6","2-6","3-6","4-6","5-6"], false);
});

QUnit.test("clearHilites: Clears all hilites", function(assert) {
  var xword = createXWord(7);
  xword.toggleCellBlock("0-0");
  xword.toggleWordHilite("0-1");
  xword.clearHilites();
  assert.equal($(jqGridId + "> .xw-hilited").length, 0);
});

QUnit.test("setEditable: TRUE Makes all cells editable", function(assert) {
  var xword = createXWord(7);
  xword.setEditable(true);
  assert.equal($(jqGridId + "> div").attr("contenteditable"), "true");
});

QUnit.test("setEditable: FALSE Makes all cells uneditable", function(assert) {
  var xword = createXWord(7);
  xword.setEditable(false);
  assert.equal($(jqGridId + "> div").attr("contenteditable"),"false");
});



/******************************************************************************************
/* HELPER FUNCTIONS */
function createXWord(size) {
  return new Crossword(gridId, function(){}, size);
}

function setBlocks(xword, blockIds) {
  blockIds.forEach( function(item) {
    xword.toggleCellBlock(item);
  });
}

function assertHilitedCells(assert, hilitedCellIds, isAcross) {
  var hilitedCells = $(jqGridId + "> .xw-hilited");
  assert.equal(hilitedCells.length, hilitedCellIds.length);
  var hasClassLabel = (isAcross) ? "xw-across" : "xw-down";
  var noClassLabel = (isAcross) ? "xw-down" : "xw-across";
  hilitedCellIds.forEach( function(item, index) {
    assert.equal(item, hilitedCells[index].id);
    assert.ok(hilitedCells[index].className.indexOf(hasClassLabel) >= 0);
    assert.ok(hilitedCells[index].className.indexOf(noClassLabel) < 0);
  });
}
