ckan.module("ap-bulk-check", function ($) {
    return {
        initialize() {
            $.proxyAll(this, /_on/);

            $(this.el).click(this._onClick)
        },

        _onClick(e) {
            $(".checkbox-cell-row input").prop("checked", $(e.target).prop("checked"));
        },
    };
});
