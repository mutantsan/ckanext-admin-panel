ckan.setSchedule = function (scheduleContainer) {
    $(scheduleContainer).val(getSchedule())
}

/**
 * Get a cron schedule string
 *
 * @returns
 */
function getSchedule() {
    const min = $("#job-minute").val() || "*";
    const hour = $("#job-hour").val() || "*";
    const day = $("#job-day").val() || "*";
    const month = $("#job-month").val() || "*";
    const week = $("#job-week").val() || "*";

    return `${min} ${hour} ${day} ${month} ${week}`
}

ckan.newJobForm = function (formSelector) {
    // const form = $(formSelector);

    // form[0].reset();

    // // $("#job-minute").val("*");
    // // $("#job-hour").val("*");
    // // $("#job-day").val("*");
    // // $("#job-month").val("*");
    // // $("#job-week").val("*");

    // // // $("#job").modal("show");
    // // $("#job_name").val("");
    // // $("#job_action").val("");

    // // job_string();

    // $("#job-save").unbind("click"); // remove existing events attached to this
    // $("#job-save").click(function () {
    //     schedule = getSchedule();

    //     let name = $("#job-name").val();

    //     $.post(routes.save, { name: name, command: job_command, schedule: schedule, _id: -1, logging: logging, mailing: mailing }, function () {
    //         location.reload();
    //     });
    // });
}
