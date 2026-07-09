(function () {
    if (window.matchMedia("(pointer: coarse)").matches) return;

    document.body.classList.add("pg-cursor-on");

    const dot = document.createElement("div");
    dot.className = "pg-cursor-dot";
    const ring = document.createElement("div");
    ring.className = "pg-cursor-ring";
    document.body.appendChild(dot);
    document.body.appendChild(ring);

    let mx = window.innerWidth / 2, my = window.innerHeight / 2;
    let rx = mx, ry = my;

    window.addEventListener("mousemove", (e) => {
        mx = e.clientX; my = e.clientY;
        dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%, -50%)`;
    });

    function loop() {
        rx += (mx - rx) * 0.18;
        ry += (my - ry) * 0.18;
        ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%, -50%)`;
        requestAnimationFrame(loop);
    }
    loop();

    document.addEventListener("mousedown", () => ring.classList.add("pg-active"));
    document.addEventListener("mouseup", () => ring.classList.remove("pg-active"));
    document.addEventListener("mouseover", (e) => {
        if (e.target.closest("a, button, .case-card, .feature, .card, .stat")) {
            ring.classList.add("pg-hover");
        }
    });
    document.addEventListener("mouseout", (e) => {
        if (e.target.closest("a, button, .case-card, .feature, .card, .stat")) {
            ring.classList.remove("pg-hover");
        }
    });
})();

(function () {
    const canvas = document.getElementById("pg-bg");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    let w, h, particles;

    function resize() {
        w = canvas.width = window.innerWidth;
        h = canvas.height = window.innerHeight;
    }
    window.addEventListener("resize", resize);
    resize();

    const count = Math.min(70, Math.floor((w * h) / 22000));
    particles = Array.from({ length: count }, () => ({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.25,
        vy: (Math.random() - 0.5) * 0.25,
    }));

    function tick() {
        ctx.clearRect(0, 0, w, h);
        ctx.fillStyle = "rgba(212,164,78,0.55)";
        for (const p of particles) {
            p.x += p.vx; p.y += p.vy;
            if (p.x < 0 || p.x > w) p.vx *= -1;
            if (p.y < 0 || p.y > h) p.vy *= -1;
            ctx.beginPath();
            ctx.arc(p.x, p.y, 1.4, 0, Math.PI * 2);
            ctx.fill();
        }
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const a = particles[i], b = particles[j];
                const dx = a.x - b.x, dy = a.y - b.y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 130) {
                    ctx.strokeStyle = `rgba(212,164,78,${0.12 * (1 - dist / 130)})`;
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.moveTo(a.x, a.y);
                    ctx.lineTo(b.x, b.y);
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(tick);
    }
    tick();
})();