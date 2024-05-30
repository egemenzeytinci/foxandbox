!function () {
    const ba = document.querySelector('button.btn-apply');

    const cards = document.querySelectorAll('div.movie');
    const rm = document.getElementById('row-movie');

    const sp = document.querySelector('div.spinner');

    const nav = document.querySelector('nav.nav-pagination');
    const ul = document.querySelector('ul.ul-pagination');

    const tte = document.querySelector('[data-bs-toggle="tooltip"]')
    const tt = new bootstrap.Tooltip(tte);

    const em = document.getElementById('exact-match');

    const ty = document.querySelector('input[name=type]');

    var pl = [];

    function fetchData(page = 1) {
        // Checked genres
        const cg = document.querySelectorAll('input[name=genre]:checked');
        const genres = [...cg].map(c => c.value);

        // Checked years
        const cy = document.querySelectorAll('input[name=year]:checked');
        const years = [...cy].map(c => c.value);

        // Checked score
        const cs = document.querySelector('input[name=score]:checked');

        // Checked number of votes
        const cn = document.querySelector('input[name=num_votes]:checked');

        const xhr = new XMLHttpRequest();

        var formData = new FormData();

        // Form data for the request
        if (genres.length > 0) formData.append('genres', genres);
        if (years.length > 0) formData.append('years', years);
        if (cs) formData.append('score', cs.value)
        if (cn) formData.append('num_votes', cn.value)

        formData.append('exact', em.checked);
        formData.append('type', ty.value)
        formData.append('page', page);

        const url = ty.value == 'movie' ? '/movie/search' : '/series/search'

        xhr.open('POST', url, false);

        xhr.send(formData);

        return JSON.parse(xhr.responseText);
    }

    function fillCards(data) {
        // If the request is not successful
        if (!data || !data.status) {
            return;
        }

        // Hide default movies
        cards.forEach((x) => x.style.display = 'none');

        // Show spinner while movies are loading
        sp.classList.remove('visually-hidden');

        rm.innerHTML = '';

        for (const r of data.results) {
            // Create card content with filtered movies
            content = `
            <div class="col-12 col-lg-3 col-md-3 mb-3">
                <div class="card">
                    <img src="/static/images/${r.title_id}.webp" class="card-img-top" alt="">
                    <div class="card-body">
                        <p class="card-text">
                            ${r.primary_title}
                        </p>
                    </div>
                    <a href="/detail/${r.title_id}" class="stretched-link" target="_blank"></a>
                </div>
            </div>
            `
            rm.innerHTML += content;
        }

        // Hide spinner
        sp.classList.add('visually-hidden');
    }

    function changePage(e) {
        // Get li element for the adding active to class
        const pi = e.target.closest('.page-item');

        // Page number
        const pageNum = parseInt(e.target.innerHTML);

        // Remove active from the classes of all elements
        pl.forEach((p) => p.classList.remove('active'));

        // Add active to selected page
        pi.classList.add('active');

        // Fetch data by page number
        const data = fetchData(pageNum);

        // Create cards
        fillCards(data);
    }

    ba.addEventListener('click', function (e) {
        e.preventDefault();

        const data = fetchData();

        fillCards(data);

        ul.innerHTML = '';

        // Find the page count by total hitted items
        pageCount = Math.ceil(data.total_count / 12);

        pageCount = pageCount > 20 ? 20 : pageCount;

        for (let i = 1; i <= pageCount; i++) {
            let cls = '';

            // Add active to first page
            if (i == 1) {
                cls = 'active'
            }

            // Pagination elements
            content = `
            <li class="page-item ${cls}">
                <a class="page-link text-decoration-none text-blue" href="javascript:">
                    ${i}
                </a>
            </li>
            `

            ul.innerHTML += content;

            pl = document.querySelectorAll('li.page-item');

            // Page click callback
            pl.forEach((e) => e.onclick = changePage);
        }

        nav.classList.remove('visually-hidden');

        this.blur();
    })
}()
