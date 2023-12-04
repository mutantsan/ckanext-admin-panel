/**
 * A script to manage AJAX actions on the cron list page
 */
ckan.module("ap-cron-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            document.addEventListener('htmx:beforeRequest', this._onHTMXbeforeRequest);
            document.addEventListener('htmx:afterSettle', this._onHTMXafterSettle);
            document.addEventListener('htmx:confirm', this._onHTMXconfirm);
        },

        _onHTMXbeforeRequest: function (e) {
            $(e.detail.target).find("[data-module]").unbind()

            for (const [key, _] of Object.entries(ckan.module.instances)) {
                ckan.module.instances[key] = null;
            }
        },

        _onHTMXafterSettle: function (e) {
            const doNotInitialize = ["ap-hyperscript"]

            $(e.detail.target).find("[data-module]").each(function (_, element) {
                const moduleName = $(element).attr("data-module");

                if (!doNotInitialize.includes(moduleName)) {
                    ckan.module.initializeElement(element);
                }
            })
        },

        _onHTMXconfirm: function (evt) {
            if (evt.detail.path.includes("/cron/delete")) {
                evt.preventDefault();

                swal({
                    text: this._("Are you sure you wish to delete a cron job?"),
                    icon: "warning",
                    buttons: true,
                    dangerMode: true,
                }).then((confirmed) => {
                    if (confirmed) {
                        evt.detail.issueRequest(true);
                        this._onRemoveCronJob(evt);
                        this.sandbox.publish("ap:notify", this._("A cron job has been removed"));
                    }
                });
            }
        },

        /**
         * Remove a cron job table row from DOM
         *
         * @param {Event} e
         */
        _onRemoveCronJob: function (e) {
            job_tr = $(e.target).closest("tr");
            job_tr.remove();
        },
    };
});
