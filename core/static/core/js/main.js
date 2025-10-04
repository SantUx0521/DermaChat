document.addEventListener('DOMContentLoaded', () => {
    const menu = document.querySelector('.fa-bars');
    const linksDiv = document.querySelector('.links-div');
    menu.addEventListener('click', () => {
        linksDiv.classList.toggle('active');
    });
    document.addEventListener('click', (e) => {
        if (!linksDiv.contains(e.target) && !menu.contains(e.target)) {
            linksDiv.classList.remove('active');
        }
    });
    window.addEventListener('resize', () => {
        if (window.innerWidth > 580) {
            linksDiv.classList.remove('active');
        }
    });
});

