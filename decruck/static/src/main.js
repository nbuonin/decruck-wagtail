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
