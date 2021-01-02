
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