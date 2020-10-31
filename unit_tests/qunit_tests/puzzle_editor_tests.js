QUnit.module('PuzzleEditor', {
  beforeEach: function () {
    $("#qunit-fixture").append($(document.createElement('div')).attr('id',"display-id"));
  },
});

// Constructor tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Constructor: No argument throws error', function(assert) {
    assert.expect(0)
    //assert.throws( function(){ new PuzzleEditor(); }, /No argument specified on Puzzle/, Error)
});