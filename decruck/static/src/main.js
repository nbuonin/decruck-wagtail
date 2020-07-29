import $ from "jquery";
import 'bootstrap';
import './scss/main.scss';
import "@fortawesome/fontawesome-free/js/all";

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
    }
    setImageHeight();
    window.addEventListener('resize', setImageHeight);
}

// Composition search page
$('.composition-search__fieldset-checkbox-label').on('click', function(el){
    $('#composition-search__form').submit();
})
