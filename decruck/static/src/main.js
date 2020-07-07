import $ from "jquery";
import 'bootstrap';
import './scss/main.scss';
import "@fortawesome/fontawesome-free/js/all";

// Mobile Nav
$('#navbar-toggle').on('click', function(el){
    $('.nav').first().toggleClass('mobile-nav-active');
})

$('.composition-search__fieldset-checkbox-label').on('click', function(el){
    $('#composition-search__form').submit();
});

$('.composition-search__fieldset-sort-label').on('click', function(el){
    $('#composition-search__form').submit();
});

// Checkout Form
$('#shopping-cart__proxy-button').on('click', function(el){
    $('#shopping-cart__pp-form-container form').submit();
})

// Homepage image size
let hpContianer = document.getElementById('home-page__cover-image');
if (hpContianer) {
    let setImageHeight = () => {
        let offsets = hpContianer.getBoundingClientRect();
        let footer = document.getElementById('footer');
        let footerOffsets = footer.getBoundingClientRect();
        hpContianer.style.height = String(footerOffsets.top - offsets.top + 16) + 'px';

        let hpMain = document.getElementById('home-page__main');
        window.DEBUG = hpMain.style;
        console.log(hpContianer.height);
    }
    setImageHeight();
    window.addEventListener('resize', setImageHeight);
}
