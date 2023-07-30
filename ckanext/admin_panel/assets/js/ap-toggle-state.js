ckan.module("ap-toggle-state", function ($) {
    /**
     * Disable/enable module host when `control` changes.
     */
    return {
        options: {
            control: null,
            event: "change",
            property: "checked",
        },

        initialize() {
            $.proxyAll(this, /_on/);

            this.control = $(this.options.control).on(
                this.options.event,
                this._onChange
            );
        },

        _onChange(event) {
            this.el.prop(
                "disabled",
                !this.control.prop(this.options.property)
            );
        },
    };
});
