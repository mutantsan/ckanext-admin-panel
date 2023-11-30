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
