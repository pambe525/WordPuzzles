const { test } = QUnit;
QUnit.config.autostart = true;
QUnit.config.collapse = false;
QUnit.config.hidepassed = true;

/**
 * Reads a template file synchronously and parses html elements with ids
 * @param templateFileName (in templates folder)
 * @returns array of jquery objects
 */
function getElementsWithIdsFrom(templateFileName) {
    var elemsWithIds = null;
    var path = "../../templates/" + templateFileName;
    $.ajax({
        url: path,
        type: 'get',
        dataType: 'html',
        async: false,
        success: function (data) {
            var html = $.parseHTML(data);
            elemsWithIds = $(html).find("*[id]");
        }
    });
    return elemsWithIds;
}

/**
 * Assigns jquery array of objects to qunit-fixture
 * @param jqueryObjects (returned by getElementsWithIdsFrom())
 */
function setupFixture(jqueryObjects) {
    $("#qunit-fixture").html(jqueryObjects.clone());
}

// Template pages to be tested
var assert = QUnit.assert;
var EditPuzzlePageHtml = getElementsWithIdsFrom("edit_puzzle.html");
var alertMessage = null;
var ajaxSettings = null;
var confirmMessage = null;
var confirmResponse = false;

// MOCK FUNCTIONS TO REPLACE WINDOWS & JQUERY FUNCTIONS
window.confirm = function (message) {
    confirmMessage = message;
    return confirmResponse;
}

window.alert = function(message) {
    alertMessage = message;
}

$.ajax = function(settings) {
    ajaxSettings = settings;
}



