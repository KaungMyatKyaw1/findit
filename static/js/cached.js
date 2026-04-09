document.querySelectorAll('select[name="sort"], select[name="order"], select[name="per_page"]').forEach(function (sel) {
    sel.addEventListener('change', function () { sel.form.submit(); });
});
