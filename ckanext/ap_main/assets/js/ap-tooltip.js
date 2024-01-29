ckan.module("ap-tooltip", function ($, _) {
    return {
        options: {
            customClass: 'ap-tooltip',
            placement: "bottom",
            html: true
        },
        initialize: function () {
            new bootstrap.Tooltip(this.el, this.options)

            document.addEventListener('htmx:afterRequest', this._onAfterRequest)
        },

        /**
         * Reinit tooltips after HTMX request to init dinamically created elements
         * tooltips
         *
         * @param {Event} evt
         */
        _onAfterRequest: function (evt) {
            $('[data-module*="ap-tooltip"]').each((_, el) => {
                new bootstrap.Tooltip(el, this.options)
            })
        }
    };
});
