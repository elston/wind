/*global app,$SCRIPT_ROOT,alertify,google*/

app.controller('MainCtrl', ['$scope', '$timeout',
    function ($scope, $timeout) {
        'use strict';

        $scope.tabs = [];

        $scope.addTab = function (event, tabData) {
            var tabSelector = $(".nav-tabs a[href='#dyntab-" + tabData.type + '-' + tabData.id + "']");
            if (tabSelector.length == 0) {
                $scope.tabs.push(tabData);
                tabSelector.click(function (e) {
                    e.preventDefault()
                    $(this).tab('show')
                })
            }
            $timeout(function () {
                var tabSelector = $(".nav-tabs a[href='#dyntab-" + tabData.type + '-' + tabData.id + "']");
                tabSelector.tab('show');
            });
        };

        $scope.deleteTab = function (tabData) {
            var index = $scope.tabs.indexOf(tabData);
            if (index > -1) {
                $scope.tabs.splice(index, 1);
            }
        };

        $scope.$on('addTab', $scope.addTab);

    }]);
