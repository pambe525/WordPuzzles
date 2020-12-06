QUnit.module("TEST");

test("check if elements exist", function(assert){
    assert.equal($("#qunit-fixture").children().length, 19);
    assert.equal($("#home").length, 1);
    assert.equal($("#save").length, 1);
})