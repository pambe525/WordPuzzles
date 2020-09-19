/*
  Tests for Class CrosswordEditor
  */
QUnit.module('CrosswordEditor', {
  beforeEach: function () {
    $("#qunit-fixture").append($(document.createElement('div')).attr('id','xw-grid'));
  },
});

QUnit.test('constructor: Throws errors if no argument', function(assert) {
    assert.throws(function(){ new CrosswordEditor(); }, /Argument expected/, Error);
});

QUnit.test('constructor: Throws errors if arg is not of type Crossword', function(assert) {
    assert.throws(function(){ new CrosswordEditor("crossword"); },
      /Object of type Crossword expected/, Error);
});

QUnit.test('constructor: ', function(assert) {
    var gridId = "#xw-grid", gridSize = 10;
    var grid = new Crossword('xw-grid', function(){}, gridSize);
});