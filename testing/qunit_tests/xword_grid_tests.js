// _dataChanged tests
//--------------------------------------------------------------------------------------------------------------------
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


// Hilites tests
//--------------------------------------------------------------------------------------------------------------------
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


