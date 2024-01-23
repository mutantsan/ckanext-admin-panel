/**
 * A script to manage AJAX actions for support feature
 */
ckan.module("ap-support-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            document.addEventListener('htmx:afterSettle', this._onHTMXafterSettle);
        },

        _onHTMXafterSettle: function (e) {
            // Initialize popovers inside dynamically created elements
            if ($.fn.popover !== undefined) {
                $('[data-bs-toggle="popover"]').popover();
            };
        },
    };
});
