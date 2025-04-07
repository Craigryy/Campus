document.querySelectorAll('.filter-btn').forEach(button => {
    button.addEventListener('click', () => {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');

        let filter = button.dataset.filter;
        document.querySelectorAll('.resource-item').forEach(item => {
            if (filter === "all" || item.dataset.type === filter) {
                item.style.display = "block";
            } else {
                item.style.display = "none";
            }
        });
    });
});
