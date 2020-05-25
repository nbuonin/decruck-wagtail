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

// Shopping Cart Utilities
const SESSION_ID = 'decruck-cart'
const DELIMITER = '-'
function hasCartItem(id) {
    let sessionVal = sessionStorage.getItem(SESSION_ID);
    return sessionVal ? sessionVal.split(DELIMITER).includes(id) : false;
}

function getAllCartItems(id) {
    return sessionStorage.getItem(SESSION_ID).split(DELIMITER);
}

function setCartItem(id) {
    let sessionVal = sessionStorage.getItem(SESSION_ID);
    if (sessionVal) {
        let items = sessionVal.split(DELIMITER);
        sessionStorage.setItem(SESSION_ID, items.append(id).join('-'));
    } else {
        sessionStorage.setItem(SESSION_ID, id);
    }
}

function removeCartItem(id) {
    let sessionVal = sessionStorage.getItem(SESSION_ID);
    if (sessionVal) {
        let items = sessionVal.split(DELIMITER);
        sessionStorage.setItem(SESSION_ID, items.filter(el => el !== id).join('-'));
    }
}

// Add to cart button
$('#score-page__atc-button').on('click', function(el){
    let item = el.target.dataset.item;
    if (!hasCartItem(item)){
        setCartItem(item);
        el.target.textContent = el.target.dataset.remove;
    } else {
        removeCartItem(item);
        el.target.textContent = el.target.dataset.add;
    }
});

// On Score page load check if item is in cart
$(document).ready(function(){
    let atcBtn = $('#score-page__atc-button')[0];
    // Set the button text on load, according to translated values
    if (atcBtn){
        let item = atcBtn.dataset.item;
        if (hasCartItem(item)){
            atcBtn.textContent = atcBtn.dataset.remove;
        } else {
            atcBtn.textContent = atcBtn.dataset.add;
        }
    }
});
