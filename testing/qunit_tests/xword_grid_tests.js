
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




