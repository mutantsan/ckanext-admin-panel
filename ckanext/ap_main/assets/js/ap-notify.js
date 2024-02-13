/**
 * Provides a way to trigger an AJAX notification
 */
ckan.module("ap-notify", function ($) {
    return {
        initialize: function () {
            $.proxyAll(this, /_on/);

            this.sandbox.subscribe("ap:notify", this._onShowNotification);

            $(".flash-messages .ap-notification").each((_, el) => {
                this._onShowNotification(el.dataset.message, el.dataset.category);
                el.remove();
            })
        },

        _onShowNotification: function (msg, msgType) {
            var tickIcon = document.createElement("i")
            tickIcon.classList = msgType === "error" ? ["fa fa-times"] : ["fa fa-check"];

            var toastDiv = document.createElement("div");

            toastDiv.id = "ap-notification-toast";
            toastDiv.style.display = "none";
            toastDiv.innerHTML = msg;
            toastDiv.classList = [msgType]
            toastDiv.prepend(tickIcon);

            document.querySelector(".main").appendChild(toastDiv);

            // Animate it and remove after
            $(toastDiv).slideDown(600);

            setTimeout(function () {
                $(toastDiv).slideUp(600, function () {
                    $(this).remove();
                });
            }, 5000);
        }
    };
});
