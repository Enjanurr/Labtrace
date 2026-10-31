$(function () {
  
    // ---- CSRF for every jQuery AJAX call -----------------------------------
  var csrfToken = $('meta[name="csrf-token"]').attr("content");
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", csrfToken);
      }
    }
  });

  // ---- Inline flash message for AJAX results ------------------------------
  function showFlash(kind, text) {
    var cls = kind === "success"
      ? "rounded-lg border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-800"
      : "rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800";
    var $msg = $("<div>").addClass(cls).text(text);
    $("#ajax-flash").append($msg);
    setTimeout(function () { $msg.fadeOut(400, function () { $(this).remove(); }); }, 5000);
  }

  // ---- Active visits board: refresh rows + count --------------------------
  function refreshActive() {
    var $body = $("#active-rows");
    if (!$body.length) { return; }
    $.getJSON($body.data("url")).done(function (res) {
      $body.html(res.html);
      $("#active-count").text(res.count);
    });
  }
  if ($("#active-rows").length) { setInterval(refreshActive, 30000); }

  // ---- AJAX check-out (works for my-visits page and staff board) ----------
  $(document).on("click", ".js-checkout", function () {
    var $btn = $(this);
    if (!window.confirm($btn.data("confirm") || "Check out now?")) { return; }
    $btn.prop("disabled", true).text("Checking out...");

    $.post($btn.data("url"))
      .done(function (res) {
        showFlash("success", res.message);
        if ($btn.data("reload")) {
          setTimeout(function () { window.location.reload(); }, 900);
        } else {
          $btn.closest(".visit-row").fadeOut(300, function () {
            $(this).remove();
            refreshActive();
          });
        }
      })
      .fail(function (xhr) {
        var msg = (xhr.responseJSON && xhr.responseJSON.error) || "Check-out failed.";
        showFlash("error", msg);
        $btn.prop("disabled", false).text("Check out");
      });
  });


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