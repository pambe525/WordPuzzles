/*
  Tests for Class Crossword
  */
QUnit.module('Crossword', {
  beforeEach: function () {
    $("#qunit-fixture").append($(document.createElement('div')).attr('id','xw-grid'));
  },
});

QUnit.test('constructor: Throws errors if arguments are not valid', function(assert) {
  assert.throws(function(){ new Crossword(2,function(){}), '1'}, /gridSize must be a number/, Error);
  assert.throws(function(){ new Crossword('bad-id', function(){}, 1) }, /divId does not exist/, Error);
  assert.throws(function(){ new Crossword('xw-grid', "func", 2) }, /clickHandler must be a function/, Error);
});

QUnit.test('constructor: Creates grid of correct width, height & border', function(assert) {
  var gridId = "#xw-grid", gridSize = 10;
  var grid = new Crossword('xw-grid', function(){}, gridSize);
  assert.equal($(gridId).width(), (grid.cellSize*gridSize + 2));
  assert.equal($(gridId).height(), (grid.cellSize*gridSize + 2))
});

QUnit.test('constructor: Creates grid of (gridSize x gridSize)div cells', function(assert) {
  var grid = new Crossword('xw-grid', function(){}, 10);
  var gridId = "#xw-grid";
  assert.equal($(gridId).children('div').length, 100);
  assert.equal($(gridId).css("border-top-width"),"1px");
});

QUnit.test('constructor: Each grid cell has correct id, css, size and click handler', function(assert) {
  var size = 8, gridId = "#xw-grid", counter = 0;
  var grid = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  for (var row = 0; row < size; row++)
    for (var col = 0; col < size; col++ ) {
      assert.equal(cells[counter].id, row + "-" + col);
      assert.equal(typeof(cells[counter].click), 'function');
      assert.equal($(cells[counter]).width(), grid.cellSize);
      assert.equal($(cells[counter]).height(), grid.cellSize);
      assert.equal($(cells[counter]).css("float"), "left");
      assert.equal($(cells[counter]).css("border-right-width"), "1px");
      counter++;
    }
});

QUnit.test('constructor: Check cell number styling', function(assert) {
  var size = 2, gridId = "#xw-grid";
  new Crossword('xw-grid', function(){}, size);
  var firstCell = $(gridId).children('div')[0];
  var cellNum = $(firstCell).children('span')[0]
  assert.equal($(cellNum).css("font-size"), "9px");
  assert.equal($(cellNum).position().left, 1);
  assert.equal($(cellNum).position().top, -2);
});

QUnit.test("toggleCellBlock: Returns false if cellId is not valid", function(assert) {
  var size = 3, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  assert.false(xword.toggleCellBlock("0-3"));
});

QUnit.test("toggleCellBlock: Blocks a cell and returns true", function(assert) {
  var size = 4, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(gridId).children('div');
  assert.true($(cells[1]).hasClass('xw-blocked'));
});

QUnit.test("toggleCellBlock: Also automatically blocks symmetric cell", function(assert) {
  var size = 4, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  assert.true(xword.toggleCellBlock("0-1"));
  var cells = $(gridId).children('div');
  assert.true($(cells[14]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 2);
});

QUnit.test("toggleCellBlock: Unblocks cells if cells are already blocked", function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  xword.toggleCellBlock("0-3");  //BLOCK
  xword.toggleCellBlock("0-3");  // UNBLOCK
  assert.false($(cells[3]).hasClass('xw-blocked'));
  assert.false($(cells[21]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});

QUnit.test("toggleCellBlock: Blocks center cell (no symmetric cell)", function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  xword.toggleCellBlock("2-2");  // BLOCK
  assert.true($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 1);
  xword.toggleCellBlock("2-2");  // UNBLOCK
  assert.false($(cells[12]).hasClass('xw-blocked'));
  assert.equal($(".xw-blocked").length, 0);
});

QUnit.test("toggleCellBlock: Clears existing blocked cell number", function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  assert.equal($(cells[4]).text(), 5);
  assert.equal($(cells[20]).text(), 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(cells[4]).text(), "");
  assert.equal($(cells[20]).text(), "");
});

QUnit.test("toggleCellBlock: Clears existing class names on numbered blocks", function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  assert.equal($(".xw-number").length, 9);
  xword.toggleCellBlock("0-4");  // BLOCK CELL WITH A NUMBER
  assert.equal($(".xw-number").length, 9);
});

QUnit.test('constructor: Auto-number default blank grid', function(assert) {
  var size = 6, gridId = "#xw-grid";
  new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  for (var col = 0; col < size; col++) {
    assert.equal($(cells[col]).text(), col + 1);
  }
  for (var row = 1; row < size; row++) {
    assert.equal($(cells[row * size]).text(), row + size);
  }
  assert.equal($(".xw-number").length, 11);
});

QUnit.test('constructor: Auto-numbers blocked grid', function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  var cells = $(gridId).children('div');
  xword.toggleCellBlock("0-0");
  xword.toggleCellBlock("1-4");
  xword.toggleCellBlock("2-3");
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
  var size = 6, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("0-0");
  xword.toggleCellBlock("0-0");
  assert.false(xword.hasBlocks());
});

QUnit.test("hasBlock: Returns true when blocks are present", function(assert) {
  var size = 5, gridId = "#xw-grid";
  var xword = new Crossword('xw-grid', function(){}, size);
  assert.false(xword.hasBlocks());
  xword.toggleCellBlock("2-2");
  assert.true(xword.hasBlocks());
});