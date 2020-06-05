$(document).ready(function () {
  $("html").on("click", ".ripple-surface", function (evt) {
    let btn = $(evt.currentTarget);
    let x = evt.pageX - btn.offset().left;
    let y = evt.pageY - btn.offset().top;

    $("<span/>").appendTo(btn).css({
      left: x,
      top: y,
    });
  });

  $(".btt-link").click(function (e) {
    $(".btt-link").click(function (e) {
      window.scrollTo(0, 0);
    });
  });
});
