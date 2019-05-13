$('body').on('click', '.product-filter .iconc', function() {
    var data = createObjFromURI();
    data.view = $(this).prop('id');
    var url = create_url(null, data);
    go_url(url,"null");
});

$('body').on('change', '.product-filter select#order', function() {
    var data = createObjFromURI();
    data.order = $('option:selected', $(this)).val();
    data.page = 1;
    var url = create_url(null, data);
    go_url(url,"null");
});

$('body').on('change', '.product-filter select#limit', function() {
    var data = createObjFromURI();
    data.limit = $('option:selected', $(this)).val();
    data.page = 1;
    var url = create_url(null, data);
    go_url(url,"null");
});

$(document).on('submit', 'form.search-box', function(e) {
    var data = {};//createObjFromURI();
    data.search = $('input[name=search]', $(this)).val();
    var url = create_url(null, data,$(this).prop('action'));
    go_url(url,"null");
    return false;
});


$(document).on('click', '.product-share a', function(e) {
    window.open(this.href,"Compartir","width=550, height=450");
    return false;
});


function inicio_gallery() {
    var $owl = $('.product-gallery');
    $owl.each(function() {
        var $a = $(this);
        $a.owlCarousel({
            autoplay: true,
            autoplayTimeout: 4000,
            loop: true,
            items: 1,
            center: true,
            nav: false,
            thumbs: true,
            thumbImage: false,
            thumbsPrerendered: true,
            thumbContainerClass: 'owl-thumbs row no-gutters',
            thumbItemClass: 'owl-thumb-item col',
            navText: ['<i class="fa fa-chevron-left" aria-hidden="true"></i>','<i class="fa fa-chevron-right" aria-hidden="true"></i>'],
        });
    });
    $('[data-fancybox="galeria"]').fancybox({
        baseClass: "fancybox-custom-layout",
        infobar: false,
        touch: {
          vertical: false
        },
        buttons: ["close", "thumbs", "share"],
        animationEffect: "fade",
        transitionEffect: "fade",
        preventCaptionOverlap: false,
        idleTime: false,
        gutter: 0,
        // Customize caption area
        caption: function(instance) {
            var title=$('.product-detail .titulo').text();
            var resumen=$('.product-detail .resumen').text();
          return '<h3>'+title+'</h3><p>'+resumen+'</p>';
        }
      });
}
