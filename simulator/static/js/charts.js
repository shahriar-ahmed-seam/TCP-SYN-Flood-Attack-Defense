const LineChart = {
  draw(canvas, history) {
    if (!canvas || !history) return;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.parentElement.clientWidth;
    const height = canvas.height = canvas.parentElement.clientHeight;

    ctx.clearRect(0, 0, width, height);

    const padL = 40;
    const padR = 16;
    const padT = 16;
    const padB = 24;

    const w = width - padL - padR;
    const h = height - padT - padB;
    const maxVal = 550;

    ctx.strokeStyle = "#1e293b";
    ctx.lineWidth = 1;
    ctx.fillStyle = "#64748b";
    ctx.font = "10px ui-monospace, monospace";
    ctx.textAlign = "right";

    const ticks = [0, 100, 250, 500];
    ticks.forEach(t => {
      const y = padT + h - (t / maxVal) * h;
      ctx.beginPath();
      ctx.moveTo(padL, y);
      ctx.lineTo(width - padR, y);
      ctx.stroke();
      ctx.fillText(`${t}ms`, padL - 6, y + 3);
    });

    const timeoutY = padT + h - (500 / maxVal) * h;
    ctx.strokeStyle = "rgba(244, 63, 94, 0.4)";
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(padL, timeoutY);
    ctx.lineTo(width - padR, timeoutY);
    ctx.stroke();
    ctx.setLineDash([]);

    if (history.length < 2) return;

    const pts = history.map((item, i) => {
      const x = padL + (i / Math.max(1, history.length - 1)) * w;
      const v = Math.min(maxVal, item.rtt_ms);
      const y = padT + h - (v / maxVal) * h;
      return { x, y, success: item.success };
    });

    ctx.beginPath();
    ctx.moveTo(pts[0].x, padT + h);
    pts.forEach(p => ctx.lineTo(p.x, p.y));
    ctx.lineTo(pts[pts.length - 1].x, padT + h);
    ctx.closePath();
    ctx.fillStyle = "rgba(56, 189, 248, 0.08)";
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(pts[0].x, pts[0].y);
    for (let i = 1; i < pts.length; i++) {
      ctx.lineTo(pts[i].x, pts[i].y);
    }
    ctx.strokeStyle = "#38bdf8";
    ctx.lineWidth = 1.5;
    ctx.stroke();

    const last = pts[pts.length - 1];
    ctx.beginPath();
    ctx.arc(last.x, last.y, 3, 0, Math.PI * 2);
    ctx.fillStyle = last.success ? "#10b981" : "#f43f5e";
    ctx.fill();
  }
};
