// _dataChanged tests
//--------------------------------------------------------------------------------------------------------------------
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

