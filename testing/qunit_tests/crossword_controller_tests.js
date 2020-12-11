/**
 * TEST HELPERS
 */
function getGridCells() {
    return $("#puzzle > div").children("div");
}

var controller = null;

/* ----------------------------------------------------------------------------------------------------------*/
QUnit.module("New Crossword", {
    beforeEach: function () {
        setupFixture(EditPuzzlePageHtml);
        controller = new CrosswordController();
    }
});

test("Constructor customizes labels on page", function (assert) {
    assert.equal($("#size-label").text(), "Grid Size");
    assert.equal($("#radio1-label").text(), "Blocks");
    assert.equal($("#radio2-label").text(), "Clues");
    assert.equal($("#save-ok").prop("hidden"), true);
});

test("Initialization without puzzleData throws error", function (assert) {
    assert.throws(
        function () {
            controller.initialize();
        },
        /Puzzle data is required for initialization/
    )

});

test("initialize sets title and initial state of widgets", function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal($("#page-title").text(), "New Crossword Puzzle");
    assert.equal($("#delete").prop("disabled"), true);
    assert.equal($("#publish").prop("disabled"), true);
    assert.equal($("#clue-form").prop("hidden"), true);
    assert.equal($("#radio-1").prop("checked"), true);
});

test("Initializa sets grid size dropdown and given size", function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    var options = $("#size > option");
    var textVals = $.map(options, function (option) {
        return option.text;
    });
    var values = $.map(options, function (option) {
        return parseInt(option.value);
    });
    assert.equal(options.length, 7);
    assert.deepEqual(textVals, ["5x5", "7x7", "9x9", "11x11", "13x13", "15x15", "17x17"])
    assert.deepEqual(values, [5, 7, 9, 11, 13, 15, 17]);
    assert.equal($("#size").val(), puzzleData.size);
});

test('Initialize creates grid using specified size in data', function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    assert.equal(getGridCells().length, 25);
});

test('Grid Size change redraws grid to new size', function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#size").val(7).change();
    assert.equal(getGridCells().length, 49);
});

test('Grid Size change in Clues edit mode switches to Block edit', function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    var radio2 = $("#radio-2");
    radio2.prop("checked", true).change();  // Toggle edit mode
    assert.true(radio2.is(":checked"));
    $("#size").val(7).change();
    assert.false(radio2.is(":checked"));
});

test('Switching to Clues edit mode shows clue edit form', function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#radio-2").prop("checked", true).change();
    assert.equal($("#clue-form").prop("hidden"), false);
});

test('Switching back to Block edit mode hides clue edit form', function (assert) {
    var puzzleData = {id: 0, size: 5}
    controller.initialize(puzzleData);
    $("#radio-2").prop("checked", true).change();
    $("#radio-1").prop("checked", true).change();
    assert.equal($("#clue-form").prop("hidden"), true);
});