/**
 * Disable current field on a form init based on target field value.
 *
 * For now, we are disabling it's only in UI. A person still could
 * remove a disable attribute via dev tools and send a value to a server.
 *
 * This is something we should fix later, but it's not a priority right now
 * because malicious use of the portal is not something we expect from sysadmins.
 */
ckan.module("ap-disable-field", function ($) {
    return {
        options: {
            targetFieldId: null,
            value: null,
        },

        initialize() {
            $.proxyAll(this, /_on/);

            const targetField = $(`#${this.options.targetFieldId}`);

            if (targetField.val() == this.options.value) {
                this.el.prop("disabled", 1);
            }
        }
    };
});
