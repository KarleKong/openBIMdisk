/**
 * display number with animation in a counting manner
 * @param $element the jquery element holding the number
 * @param number the number to be animated
 * @param duration duration of the animation
 * @param fractionDigits number of decimals to be rounded to
 */
export function animateNumberDisplay($element, number, duration, fractionDigits) {
    $element.text(number);
    $element.prop('counter', 0).animate({ // start counting from 0
        counter: $element.text()
    }, {
        duration: duration,
        easing: 'swing',
        step: function (current) {
            $element.text(current.toFixed(fractionDigits));
        }
    });
}