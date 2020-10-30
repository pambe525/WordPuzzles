QUnit.module('Puzzle', {
  beforeEach: function () {
    $("#qunit-fixture").append($(document.createElement('div')).attr('id',"display-id"));
  },
});

// SAVE tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Save success invokes saveSuccessHandler', function(assert) {
    var puzzle = new Puzzle();
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({status:"OK"}); }  // mock save success
    puzzle.setSaveSuccessHandler(handler);
    puzzle.save();
    assert.true(handlerCalled);
    assert.equal(dataArg.status, "OK");
});

QUnit.test('Save failure invokes saveFailureHandler', function(assert) {
    var puzzle = new Puzzle();
    var handlerCalled = false;
    var handler = function(){ handlerCalled=true; };
    $.ajax = function(obj) { obj.error(); };  // mock save failure
    puzzle.setSaveFailureHandler(handler);
    puzzle.save();
    assert.true(handlerCalled);
});

QUnit.test('Save success does nothing if saveSuccessHandler is not set', function(assert) {
    var puzzle = new Puzzle();
    $.ajax = function(obj) { obj.success({puzzle_id:2}); };  // mock failure
    try {
        puzzle.save();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});

QUnit.test('Save failure does nothing if saveFailureHandler is not set', function(assert) {
    var puzzle = new Puzzle();
    $.ajax = function(obj) { obj.error(); };  // mock save failure
    try {
        puzzle.save();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});

QUnit.test('Save invokes ajax call with correct parameters', function(assert) {
    var puzzle = new Puzzle();
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    assert.equal(ajaxArg.method, "POST");
    assert.equal(ajaxArg.dataType, "json");
});

QUnit.test('Save includes proper data parameters in ajax call', function(assert) {
    var puzzle = new Puzzle();
    puzzle.puzzleId = 222;
    puzzle._getDataToSave = function(){ return {somedata:"blah"}; };
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    var ajaxDataObj = JSON.parse(ajaxArg.data['data']);
    assert.equal(ajaxDataObj['puzzle_id'], 222);
    assert.equal(ajaxDataObj['size'], 0);
    assert.equal(ajaxDataObj['desc'], "");
    assert.equal(ajaxDataObj['is_xword'], true);
    assert.equal(ajaxDataObj['shared_at'], null);
    assert.deepEqual(ajaxDataObj['data'], {somedata:"blah"});
});

QUnit.test('Save includes action parameter in ajax call', function(assert) {
    var puzzle = new Puzzle();
    puzzle._getDataToSave = function(){ return {somedata:"blah"}; };
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.save();
    assert.equal(ajaxArg.data['action'], 'save');
});

QUnit.test('Save updates puzzle_id', function(assert) {
    var puzzle = new Puzzle();
    assert.equal(puzzle.puzzleId, 0);   // Initial puzzle_id is zero
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({puzzle_id: 2}); }  // mock success
    puzzle.setSaveSuccessHandler(handler);
    puzzle.save();
    assert.equal(puzzle.puzzleId, 2);  // Update puzzle_id
});

// DELETE tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Delete success invokes deleteSuccessHandler', function(assert) {
    var puzzle = new Puzzle();
    var handlerCalled = false, dataArg;
    var handler = function(data){ handlerCalled=true; dataArg=data};
    $.ajax = function(obj) { obj.success({status:"OK"}); }  // mock success
    puzzle.setDeleteSuccessHandler(handler);
    puzzle.delete();
    assert.true(handlerCalled);
    assert.equal(dataArg.status, "OK");
});

QUnit.test('Delete failure invokes deleteFailureHandler', function(assert) {
    var puzzle = new Puzzle();
    var handlerCalled = false;
    var handler = function(){ handlerCalled=true; };
    $.ajax = function(obj) { obj.error(); };  // mock failure
    puzzle.setDeleteFailureHandler(handler);
    puzzle.delete();
    assert.true(handlerCalled);
});

QUnit.test('Delete success does nothing if saveSuccessHandler is not set', function(assert) {
    var puzzle = new Puzzle();
    $.ajax = function(obj) { obj.success(); };  // mock failure
    try {
        puzzle.delete();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});

QUnit.test('Delete failure does nothing if saveFailureHandler is not set', function(assert) {
    var puzzle = new Puzzle();
    $.ajax = function(obj) { obj.error(); };  // mock failure
    try {
        puzzle.delete();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});

QUnit.test('Delete invokes ajax call with correct parameters', function(assert) {
    var puzzle = new Puzzle();
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.equal(ajaxArg.method, "POST");
    assert.equal(ajaxArg.dataType, "json");
});

QUnit.test('Delete includes puzzle_id in ajax call', function(assert) {
    var puzzle = new Puzzle();
    puzzle.puzzleId = 10;
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.deepEqual(ajaxArg.data['puzzle_id'], puzzle.puzzleId);
});

QUnit.test('Delete includes action parameter in ajax call', function(assert) {
    var puzzle = new Puzzle();
    var ajaxArg = null;
    $.ajax = function(obj) { ajaxArg = obj };
    puzzle.delete();
    assert.equal(ajaxArg.data['action'], 'delete');
});

// DATA CHANGE tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('Data change invokes dataChangedHandler', function(assert) {
    var puzzle = new Puzzle();
    var handlerCalled = false;
    var handler = function(){ handlerCalled=true; };
    puzzle.setDataChangedHndler(handler);
    puzzle._dataChanged();
    assert.true(handlerCalled);
});

QUnit.test('Data change does nothing if datChangedHandler is not set', function(assert) {
    var puzzle = new Puzzle();
    try {
        puzzle._dataChanged();
        assert.ok(true);
    } catch(e) { assert.notOk(true, "No exception expected.")}
});

// setSharingOn tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('SetSharingOn sets current datetime string if true else null', function(assert) {
    var puzzle = new Puzzle();
    puzzle.setSharingOn();
    assert.equal(puzzle.sharedAt, new Date().toISOString());
    puzzle.setSharingOn(false);
    assert.equal(puzzle.sharedAt, null);
});

// show() tests
//--------------------------------------------------------------------------------------------------------------------
QUnit.test('show appends html to given container div id', function(assert) {
    var puzzle = new Puzzle();
    var called = true;
    puzzle._setHtmlOnDiv = function() { $(puzzle.divId).html("<span>SOME HTML</span>")};
    puzzle.show("display-id");
    assert.equal($("#display-id").html(), "<span>SOME HTML</span>");
});

QUnit.test('show calls _loadPuzzleData if passed as argument', function(assert) {
    var puzzle = new Puzzle();
    var dataPassed = null;
    puzzle._loadPuzzleData = function(data) { dataPassed = data; };
    puzzleData = "some data";
    puzzle.show("display-id", puzzleData);
    assert.equal(dataPassed, "some data");
});