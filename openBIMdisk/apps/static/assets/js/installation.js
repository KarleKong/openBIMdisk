import {animateNumberDisplay} from './Util.js';
import BIM from './3d-model/main.js'

const animDuration = 1000;

$('#install-total .total').text(952);
animateNumberDisplay($('#install-total .installed'), 100, animDuration, 0);

$('#install-block-a .total').text(476);
animateNumberDisplay($('#install-block-a .installed'), 60, animDuration, 0);

$('#install-block-b .total').text(476);
animateNumberDisplay($('#install-block-b .installed'), 40, animDuration, 0);

animateNumberDisplay($('#avg-install-time > .display-number > span'), 15, animDuration, 0);

setTimeout(function () {
    BIM.init();
    BIM.animate();
}, animDuration);