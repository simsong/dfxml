$(".uscb-tab").each(function(index, element) {
  $(element).click(function() {
    $(this).siblings().removeClass("uscb-tab-active")
    $(this).toggleClass("uscb-tab-active");
  });

});

$(".uscb-tab-menu").click(function() {
  $(".uscb-tab-dropdown-content").toggleClass("uscb-tab-show");
});