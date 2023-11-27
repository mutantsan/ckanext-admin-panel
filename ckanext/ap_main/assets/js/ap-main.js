ckan.module("ap-main", function ($, _) {
    "use strict";

    return {
        options: {},

        initialize: function () {
            document.querySelector("body").setAttribute("admin-panel-active", true);
        }
    };
});
