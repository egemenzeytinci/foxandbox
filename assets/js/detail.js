!function () {
    const rb = document.querySelector('button.recommendation');
    const rd = document.querySelector('div.recommendation');

    // Recommendation button callback
    const tbc = function () {
        rd.scrollIntoView({ behavior: 'smooth' });
    }

    // Go to recommendation section
    rb.onclick = tbc;
}()
