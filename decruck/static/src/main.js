import $ from "jquery";
import 'bootstrap';
import './scss/main.scss';
import "@fortawesome/fontawesome-free/js/all";

$('.composition-search__fieldset-checkbox-label').on('click', function(el){
    $('#composition-search__form').submit();
});
