(function () {
    var cfg     = window.FINDIT;
    var query   = cfg.query;
    var perPage = cfg.perPage;
    var sortBy  = cfg.sortBy;
    var orderBy = cfg.orderBy;
    var allProducts = [];
    var grid    = document.getElementById('product-grid');
    var pagWrap = document.getElementById('pagination-wrap');
    var resInfo = document.getElementById('result-info');
    var loadBar = document.getElementById('loading-bar');
    var grads   = ['g0','g1','g2','g3','g4','g5','g6','g7','g8','g9','g10','g11'];

    function esc(s) {
        var d = document.createElement('div');
        d.textContent = s || '';
        return d.innerHTML;
    }

    function buildCard(item, idx) {
        var gi   = idx % 12;
        var link = item.link
            ? (item.link.indexOf('http') === 0 ? item.link : 'https://www.amazon.com' + item.link)
            : '#';
        var badgeCls  = item.price ? 'badge-deal' : (idx % 4 === 2 ? 'badge-hot' : 'badge-new');
        var badgeTxt  = item.price ? 'Deal'       : (idx % 4 === 2 ? 'Hot'       : 'New');
        var priceHtml = item.price
            ? '<span class="card-price">' + esc(item.price) + '</span>'
            : '<span class="card-price-na">Price unavailable</span>';
        var brandHtml  = item.name ? '<div class="card-brand">' + esc(item.name) + '</div>' : '';
        var imgContent = item.image
            ? '<img src="' + esc(item.image) + '" alt="' + esc(item.title || '') + '" loading="lazy">'
            : '<span class="card-img-icon">&#128717;</span>';
        var imgClass    = item.image ? '' : grads[gi];
        var sourceBadge = item.source
            ? '<span class="source-badge source-' + item.source.toLowerCase() + '">' + esc(item.source) + '</span>'
            : '';
        var overlaySrc = item.source || 'Store';
        return '<a href="' + link + '" target="_blank" rel="noopener" class="product-card">' +
            '<div class="card-img ' + imgClass + '">' +
                imgContent +
                '<span class="card-badge ' + badgeCls + '">' + badgeTxt + '</span>' +
                sourceBadge +
                '<div class="card-overlay"><div class="overlay-cta">View on ' + esc(overlaySrc) + ' &#8599;</div></div>' +
            '</div>' +
            '<div class="card-body">' +
                brandHtml +
                '<div class="card-title">' + esc(item.title || 'Product details unavailable') + '</div>' +
                '<div class="card-sep"></div>' +
                '<div class="card-footer">' + priceHtml + '<span class="card-btn">&#8599;</span></div>' +
            '</div>' +
        '</a>';
    }

    function sortProducts(arr) {
        var rev = (orderBy === 'desc');
        if (sortBy === 'price') {
            return arr.slice().sort(function (a, b) {
                function getP(p) {
                    var m = (p.price || '').match(/[\d,]+\.?\d*/);
                    return m ? parseFloat(m[0].replace(',', '')) : Infinity;
                }
                return rev ? getP(b) - getP(a) : getP(a) - getP(b);
            });
        }
        if (sortBy === 'name' || sortBy === 'title') {
            return arr.slice().sort(function (a, b) {
                var cmp = (a[sortBy] || '').localeCompare(b[sortBy] || '');
                return rev ? -cmp : cmp;
            });
        }
        return arr;
    }

    function renderPage(page) {
        var sorted = sortProducts(allProducts);
        var start  = (page - 1) * perPage;
        var end    = start + perPage;
        grid.innerHTML = sorted.slice(start, end).map(function (item, i) {
            return buildCard(item, start + i);
        }).join('');
        var totalPages = Math.max(1, Math.ceil(allProducts.length / perPage));
        renderPagination(page, totalPages);
        var showing = Math.min(perPage, allProducts.length - start);
        resInfo.innerHTML =
            '<h2>' + allProducts.length + ' Product' + (allProducts.length !== 1 ? 's' : '') + ' Found</h2>' +
            '<p>Page ' + page + ' of ' + totalPages + ' &nbsp;&middot;&nbsp; Showing ' + showing + ' items</p>';
    }

    function renderPagination(page, totalPages) {
        if (totalPages <= 1) { pagWrap.innerHTML = ''; return; }

        var pages = [];
        var delta = 2;
        var left  = page - delta;
        var right = page + delta;

        for (var n = 1; n <= totalPages; n++) {
            if (n === 1 || n === totalPages || (n >= left && n <= right)) {
                pages.push(n);
            }
        }

        var h = '';
        h += page > 1
            ? '<a class="pag-btn" onclick="goPage(' + (page - 1) + ')">&#8592; Prev</a>'
            : '<span class="pag-btn disabled">&#8592; Prev</span>';

        var prev = null;
        for (var i = 0; i < pages.length; i++) {
            var n = pages[i];
            if (prev !== null && n - prev > 1) {
                h += '<span class="pag-btn disabled">&hellip;</span>';
            }
            h += '<a class="pag-btn' + (n === page ? ' active' : '') + '" onclick="goPage(' + n + ')">' + n + '</a>';
            prev = n;
        }

        h += page < totalPages
            ? '<a class="pag-btn" onclick="goPage(' + (page + 1) + ')">Next &#8594;</a>'
            : '<span class="pag-btn disabled">Next &#8594;</span>';

        pagWrap.innerHTML = h;
    }

    window.goPage = function (n) {
        renderPage(n);
        window.scrollTo({ top: grid.offsetTop - 90, behavior: 'smooth' });
    };

    document.querySelectorAll('select[name="sort"], select[name="order"], select[name="per_page"]').forEach(function (sel) {
        sel.addEventListener('change', function () {
            if (allProducts.length === 0) { this.form.submit(); return; }
            if (sel.name === 'sort')      sortBy  = sel.value;
            if (sel.name === 'order')     orderBy = sel.value;
            if (sel.name === 'per_page')  perPage = parseInt(sel.value, 10);
            renderPage(1);
        });
    });

    var es = new EventSource('/stream?search=' + encodeURIComponent(query));

    es.onmessage = function (e) {
        var data = JSON.parse(e.data);

        if (data.type === 'product') {
            allProducts.push(data.item);
            var idx = allProducts.length - 1;
            if (idx < perPage) {
                var skel = grid.querySelector('.skeleton-card');
                if (skel) skel.remove();
                var wrapper = document.createElement('div');
                wrapper.innerHTML = buildCard(data.item, idx);
                grid.appendChild(wrapper.firstElementChild);
            }
            resInfo.innerHTML =
                '<h2>' + allProducts.length + ' result' + (allProducts.length !== 1 ? 's' : '') + ' so far</h2>' +
                '<p>Loading more<span class="loading-dots">...</span></p>';
        }

        if (data.type === 'done') {
            es.close();
            if (loadBar) loadBar.style.display = 'none';
            renderPage(1);
        }
    };

    es.onerror = function () {
        es.close();
        if (loadBar) loadBar.style.display = 'none';
        if (allProducts.length === 0) {
            grid.innerHTML =
                '<div class="empty-state" style="grid-column:1/-1">' +
                '<div class="empty-icon">&#9888;&#65039;</div>' +
                '<h3>Search failed</h3>' +
                '<p>Could not load results. Please try again.</p>' +
                '</div>';
        } else {
            renderPage(1);
        }
    };
}());
