(function () {
    'use strict';

    // store the currently selected tab in the hash value
    $("ul.nav-tabs > li > a").on("shown.bs.tab", function (e) {
        window.location.hash = $(e.target).attr("href").substr(1);
    });

    // on load of the page: switch to the currently selected tab
    var hash = window.location.hash;
    $('ul.nav-tabs a[href="' + hash + '"]').tab('show');

}());

var app = angular.module('app', ['ui.grid', 'ui.grid.selection', 'ui.bootstrap', 'ngLoadingSpinner',
    'ui.grid.autoResize']);
