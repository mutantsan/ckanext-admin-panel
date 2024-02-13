/**
 * A script to manage AJAX actions for ticket modal
 */
ckan.module("ap-support-modal-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            htmx.on('htmx:afterSettle', this._onHTMXafterSettle);
            htmx.on("htmx:beforeRequest", this._onBeforeRequest);
        },

        _onHTMXafterSettle: function (e) {
            // Initialize popovers inside dynamically created elements
            if ($.fn.popover !== undefined) {
                $('[data-bs-toggle="popover"]').popover();
            };
        },

        _onFormSubmit: function (e) {
            if (typeof window.ckeditors === "undefined") {
                return;
            }

            window.ckeditors.forEach(editor => {
                if (editor.sourceElement === this.el.find("#field-text")[0]) {
                    e.detail.requestConfig.parameters.text = editor.getData();
                }
            });
        },
        /**
         * Update a Ckeditor textarea on htmx request if it's enabled
         *
         * @param {Event} e
         */
        _onBeforeRequest: function (e) {
            if (typeof window.ckeditors === "undefined") {
                return;
            }

            window.ckeditors.forEach(editor => {
                if (editor.sourceElement === this.el.find("#field-text")[0]) {
                    e.detail.requestConfig.parameters.text = editor.getData();
                }
            });
        }
    };
});
