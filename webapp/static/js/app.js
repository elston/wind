/*global angular*/

(function () {
    'use strict';

    $("ul.nav-tabs > li > a").on("shown.bs.tab", function (e) {
            var tabName = $(e.target).attr("href").substr(1);
            if (tabName.startsWith('dyntab-')) {
                window.location.hash = null;
            } else {
                // store the currently selected tab in the hash value
                window.location.hash = tabName;
            }
            if (tabName === 'locations') {  // update Google map
                var tabBody = document.querySelector('[ng-controller=LocationsCtrl]');
                var tabScope = angular.element(tabBody).scope();
                if (tabScope) {
                    tabScope.updateMap();
                }
            }
        }
    );

    // on load of the page: switch to the currently selected tab
    var hash = window.location.hash;
    $('ul.nav-tabs a[href="' + hash + '"]').tab('show');

}());

var app = angular.module('app', ['ui.grid', 'ui.grid.selection', 'ui.bootstrap', 'ngLoadingSpinner',
    'ui.grid.autoResize', 'ngFileUpload', 'rzModule']);
