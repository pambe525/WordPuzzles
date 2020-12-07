QUnit.module("TEST", {
    before: function() {
        var elemsWithIds = getElementsWithIdsFrom("edit_puzzle.html");
        $("#qunit-fixture").append(elemsWithIds);
    }
});

test("check if elements exist", function(assert){
    assert.equal($("#qunit-fixture").children().length, 19);
    assert.equal($("#home").length, 1);
    assert.equal($("#save").length, 1);
    $("#save").prop("disabled", true);
    assert.equal($("#save").prop("disabled"), true);
});

test("check if fixture is reset", function(assert){
    assert.equal($("#qunit-fixture").children().length, 19);
    assert.equal($("#home").length, 1);
    assert.equal($("#save").length, 1);
    assert.equal($("#save").prop("disabled"), false);
})
