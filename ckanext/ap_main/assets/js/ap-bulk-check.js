ckan.module("ap-bulk-check", function ($) {
    return {
        options: {
            selector: ".checkbox-cell-row input",
        },

        initialize() {
            $.proxyAll(this, /_on/);

            $(this.el).click(this._onClick)
        },

        _onClick(e) {
            $(this.options.selector).prop("checked", $(e.target).prop("checked"));
        },
    };
});
