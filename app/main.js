document.addEventListener("DOMContentLoaded", () => {
    const flashes = document.querySelectorAll(".flash");
    flashes.forEach((flash, index) => {
        window.setTimeout(() => {
            flash.style.opacity = "0";
            flash.style.transform = "translateY(-6px)";
            flash.style.transition = "all 240ms ease";
            window.setTimeout(() => flash.remove(), 260);
        }, 4200 + index * 250);
    });
});
