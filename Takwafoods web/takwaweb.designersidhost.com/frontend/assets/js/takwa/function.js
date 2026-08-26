(function ($) {
    "use strict";
	
	var $window = $(window); 
	var $body = $('body'); 

	/* Preloader Effect */
	$window.on('load', function(){
		$(".preloader").fadeOut(600);
	});

	/* Sticky Header */	
	if($('.active-sticky-header').length){
		$window.on('resize', function(){
			setHeaderHeight();
		});

		function setHeaderHeight(){
	 		$("header.main-header").css("height", $('header .header-sticky').outerHeight());
		}	
	
		$(window).on("scroll", function() {
			var fromTop = $(window).scrollTop();
			setHeaderHeight();
			var headerHeight = $('header .header-sticky').outerHeight()
			$("header .header-sticky").toggleClass("hide", (fromTop > headerHeight + 100));
			$("header .header-sticky").toggleClass("active", (fromTop > 600));
		});
	}	
	

	
// History Tabs Carousel
// loop + autoplay used to make the timeline jump backward from 2025 to 1996
// and fight you mid-drag. It's a fixed chronological history, not a rotating
// gallery, so both are off now; owl's built-in mouse-drag still works.
//
// Owl sizes each card as (stage width / items) for whatever "items" count
// matches the current breakpoint. The timeline section is now full viewport
// width instead of sitting in a ~1300px container, so on a wide screen the
// old items:3 stretched each card (and its fixed-height image) far wider
// than it was ever designed for. Added breakpoints that increase the item
// count as the screen widens, so each card stays close to its original
// ~400px size no matter how wide the stage is — instead of 3 huge cards,
// a wide screen shows more cards at their normal size. margin bumped up
// for more visible breathing room between them.
if ($('.history-tabs-carousel').length) {
    $('.history-tabs-carousel').owlCarousel({
        loop: false,
        margin: 40,
        dots: false,
        nav: true,
        stagePadding: 0,
        singleItem: true,
        smartSpeed: 500,
        autoplay: false,
        navText: ['<span class="flaticon-down-arrow-2 left"></span>', '<span class="flaticon-down-arrow-2 right"></span>'],
        responsive: {
            0: {
                items: 1
            },
            600: {
                items: 1
            },
            767: {
                items: 1
            },
            992: {
                items: 2
            },
            1200: {
                items: 3
            },
            1600: {
                items: 4
            },
            1900: {
                items: 5
            }
        }
    });
}




/////////////////////////////
//Universal Code for All Owl Carousel Sliders
/////////////////////////////

if ($('.theme_carousel').length) {
    $(".theme_carousel").each(function (index) {
        var $owlAttr = {},
            $extraAttr = $(this).data("options");
        $.extend($owlAttr, $extraAttr);


        $(this).owlCarousel($owlAttr);


    });

}




	/* Slick Menu JS */
	$('#menu').slicknav({
		label : '',
		prependTo : '.responsive-menu'
	});

	/* The generated hamburger button has no text, so screen readers announce
	   it only as "link". Name it after slicknav builds it. */
	$('.slicknav_btn').attr('aria-label', 'Open the main menu');

	/* The cookie bar is fixed to the bottom of the viewport, so it sat on top
	   of the footer's social icons and swallowed their clicks. Mirror its
	   visibility onto <body> so the CSS can reserve space for it, letting the
	   page scroll clear of the bar instead of hiding content underneath it.
	   The bar is shown/hidden by toggling `d-none` from each page's inline
	   script, hence observing the class rather than hooking those scripts. */
	var cookieBar = document.querySelector('.cookie_consent_modal');
	if (cookieBar) {
		var syncCookieSpace = function () {
			document.body.classList.toggle('cookie-open',
				!cookieBar.classList.contains('d-none'));
		};
		syncCookieSpace();
		new MutationObserver(syncCookieSpace)
			.observe(cookieBar, { attributes: true, attributeFilter: ['class'] });
	}

	if($("a[href='#top']").length){
		$("a[href='#top']").click(function() {
			$("html, body").animate({ scrollTop: 0 }, "slow");
			return false;
		});
	}



	/* Services Slider JS */
	if ($('.service-list').length) {
		const projects_slider = new Swiper('.service-list .swiper', {
			slidesPerView : 1,
			speed: 1000,
			spaceBetween: 30,
			loop: true,
			autoplay: {
				delay: 5000,
			},
			pagination: {
				el: '.service-pagination',
				clickable: true,
			},
			breakpoints: {
				768:{
					slidesPerView: 2,
				},
				991:{
					slidesPerView: 4,
				}
			}
		});
	}


	
	/* Hero Slider Layout JS */
	if ($('.hero-slider-layout .swiper').length) {
	const hero_slider_layout = new Swiper('.hero-slider-layout .swiper', {
		slidesPerView : 1,
		speed: 1000,
		spaceBetween: 0,
		loop: true,
		autoplay: {
			delay: 4000,
		},
		pagination: {
			el: '.hero-pagination',
			clickable: true,
		},
	});
	}

	/* testimonial Slider JS */
	if ($('.testimonial-slider').length) {
		const testimonial_slider = new Swiper('.testimonial-slider .swiper', {
			slidesPerView : 1,
			speed: 1000,
			spaceBetween: 30,
			loop: true,
			autoplay: {
				delay: 5000,
			},
			pagination: {
				el: '.swiper-pagination',
				clickable: true,
			},
			navigation: {
				nextEl: '.testimonial-button-next',
				prevEl: '.testimonial-button-prev',
			},
			breakpoints: {
				768:{
				  	slidesPerView: 1,
				},
				991:{
				  	slidesPerView: 1,
				}
			}
		});
	}

	/* Skill Bar */
	if ($('.skills-progress-bar').length) {
		$('.skills-progress-bar').waypoint(function() {
			$('.skillbar').each(function() {
				$(this).find('.count-bar').animate({
				width:$(this).attr('data-percent')
				},2000);
			});
		},{
			offset: '70%'
		});
	}

	/* Youtube Background Video JS */
	if ($('#herovideo').length) {
		var myPlayer = $("#herovideo").YTPlayer();
	}

	/* Init Counter */
	if ($('.counter').length) {
		$('.counter').counterUp({ delay: 6, time: 3000 });
	}

	/* Image Reveal Animation */
	if ($('.reveal').length) {
        gsap.registerPlugin(ScrollTrigger);
        let revealContainers = document.querySelectorAll(".reveal");
        revealContainers.forEach((container) => {
            let image = container.querySelector("img");
            let tl = gsap.timeline({
                scrollTrigger: {
                    trigger: container,
                    toggleActions: "play none none none"
                }
            });
            tl.set(container, {
                autoAlpha: 1
            });
            tl.from(container, 1, {
                xPercent: -100,
                ease: "power2.out"
            });
            tl.from(image, 1, {
                xPercent: 100,
                scale: 1,
                delay: -1,
                ease: "power2.out"
            });
        });
    }

	/* Parallaxie js */
	var $parallaxie = $('.parallaxie');
	if($parallaxie.length && ($window.width() > 991))
	{
		if ($window.width() > 768) {
			$parallaxie.parallaxie({
				speed: 0.55,
				offset: 0,
			});
		}
	}

	/* Zoom Gallery screenshot */
	$('.gallery-items').magnificPopup({
		delegate: 'a',
		type: 'image',
		closeOnContentClick: false,
		closeBtnInside: false,
		mainClass: 'mfp-with-zoom',
		image: {
			verticalFit: true,
		},
		gallery: {
			enabled: true
		},
		zoom: {
			enabled: true,
			duration: 300, // don't foget to change the duration also in CSS
			opener: function(element) {
			  return element.find('img');
			}
		}
	});

	/* Contact and appointment forms are handled by takwa/contact-form.js, which
	   posts to Web3Forms. The blocks that used to live here posted to
	   form-process.php and form-appointment.php - endpoints from the old Laravel
	   CMS that do not exist on a static site. They fired on every valid
	   submission and wrote their result into #msgSubmit, overwriting the real
	   status message. Removed. */

	/* Animated Wow Js */	
	new WOW().init();

	/* Popup Video */
	if ($('.popup-video').length) {
		$('.popup-video').magnificPopup({
			type: 'iframe',
			mainClass: 'mfp-fade',
			removalDelay: 160,
			preloader: false,
			fixedContentPos: true
		});
	}
	
})(jQuery);