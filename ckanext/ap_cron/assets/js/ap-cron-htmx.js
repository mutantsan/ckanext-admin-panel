/**
 * A script to manage AJAX actions on the cron list page
 */
ckan.module("ap-cron-htmx", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);
            var self = this;

            document.body.addEventListener('htmx:confirm', function (evt) {
                if (evt.detail.path.includes("/reports/cron/delete")) {
                    evt.preventDefault();

                    swal({
                        text: self._("Are you sure you wish to delete a cron job?"),
                        icon: "warning",
                        buttons: true,
                        dangerMode: true,
                    }).then((confirmed) => {
                        if (confirmed) {
                            evt.detail.issueRequest(true);
                            self._onRemoveCronJob(evt);
                        }
                    });
                }
            });
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
