ckan.module("ap-tooltip", function ($, _) {
    return {
        options: {
            customClass: 'ap-tooltip',
            placement: "bottom",
            html: true
        },
        initialize: function () {
            new bootstrap.Tooltip(this.el, this.options)
        }
    };
});
