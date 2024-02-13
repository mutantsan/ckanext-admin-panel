ckan.module("ap-bulk-check", function ($) {
    return {
        options: {
            selector: ".checkbox-cell-row input",
        },

        initialize() {
            $.proxyAll(this, /_on/);

            $(this.el).click(this._onClick)

            document.addEventListener('htmx:afterRequest', this._onAfterRequest);
        },

        _onClick(e) {
            $(this.options.selector).prop("checked", $(e.target).prop("checked"));
        },

        /**
         * Reinit bulk check script after HTMX request
         *
         * @param {Event} evt
         */
        _onAfterRequest: function (evt) {
            $('[data-module*="ap-bulk-check"]').each((_, el) => {
                $(el).click(this._onClick);
            })
        }
    };
});
