$(function () {
  // Auto-dismiss flash messages after 5s
  setTimeout(function () {
    $(".flash-message").fadeOut(400, function () { $(this).remove(); });
  }, 5000);

  // Red border on fields that have server-side errors
  $("p.field-error").each(function () {
    $(this).closest(".field")
      .find("input, select, textarea")
      .removeClass("border-slate-300")
      .addClass("border-red-500");
  });

  // Show/Hide password
  $(".toggle-password").on("click", function () {
    var $input = $($(this).data("target"));
    var show = $input.attr("type") === "password";
    $input.attr("type", show ? "text" : "password");
    $(this).text(show ? "Hide" : "Show");
  });

  // Live institutional-email hint (server-side validation is still authoritative)
  var $email = $("#id_email");
  var $hint = $("#email-hint");
  if ($email.length && $hint.length) {
    var domains = String($email.data("allowed-domains") || "")
      .split(",")
      .map(function (d) { return $.trim(d).toLowerCase(); })
      .filter(Boolean);

    var checkEmail = function () {
      var value = $.trim($email.val()).toLowerCase();
      if (!value || value.indexOf("@") === -1) {
        $hint.text("").attr("class", "-mt-3 text-xs");
        return;
      }
      var domain = value.split("@").pop();
      if (domains.indexOf(domain) !== -1) {
        $hint.text("Institutional email looks good.")
          .attr("class", "-mt-3 text-xs font-medium text-green-600");
      } else {
        $hint.text("Email must end with @" + domains.join(" or @") + ".")
          .attr("class", "-mt-3 text-xs font-medium text-red-600");
      }
    };

    $email.on("input blur", checkEmail);
    checkEmail();
  }

  // Confirm dialog for destructive forms: <form data-confirm="Are you sure?">
  $("form[data-confirm]").on("submit", function (e) {
    if (!window.confirm($(this).data("confirm"))) {
      e.preventDefault();
    }
  });
});